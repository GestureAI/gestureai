<script lang="ts">
	import {
		Breadcrumb,
		BreadcrumbItem,
		BreadcrumbLink,
		BreadcrumbList,
		BreadcrumbPage,
		BreadcrumbSeparator
	} from '$lib/components/ui/breadcrumb';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { usernameStore } from '$lib/stores';
	import { UseAutoScroll } from '$lib/hooks/use-auto-scroll.svelte';
	import { Paperclip, ArrowUp, Hand } from '@lucide/svelte';
	import GestureAIDialog from '$lib/components/gesture-ai-dialog.svelte';

	const autoScroll = new UseAutoScroll();

	// For WS communication and ui state
	interface ChatMessageFromServer {
		id: string; // Server generated ID.
		type: 'message';
		username: string;
		message: string;
		timestamp: number;
	}

	// For messages added to the ui immediately by the sender, pending server confirmation.
	interface PendingChatMessage {
		id: `client-${string}`; // Temporary client-side ID, e.g., "client-uuid".
		type: 'message';
		username: string;
		message: string;
		timestamp: number;
	}

	type DisplayMessage = ChatMessageFromServer | PendingChatMessage;

	interface WelcomeMessage {
		type: 'welcome';
		username: string;
		message: string;
		timestamp: number;
	}

	interface HistoryMessage {
		type: 'history';
		messages: ChatMessageFromServer[]; // History only contains server-confirmed messages
	}

	type WebSocketIncomingData = WelcomeMessage | HistoryMessage | ChatMessageFromServer;

	interface User {
		username: string;
	}

	let gestureAIDialogOpen = $state<boolean>(false);
	let messages = $state<DisplayMessage[]>([]);
	let currentUser = $state<User | null>(null);
	let messageInput = $state<string>('');
	let isConnected = $state<boolean>(false);

	let currentWebSocket: WebSocket | null = null;
	let connectionAttempts = 0;
	let reconnectTimerId: number | null = null;
	// Flag to prevent auto-reconnect on intentional close
	let isIntentionallyClosing = false;

	function formatTime(timestamp: number): string {
		return new Date(timestamp).toLocaleTimeString([], {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	// Core WS connection and reconnection logic
	function connect() {
		// Prevent multiple concurrent connection attempts or connecting if already connected
		if (
			currentWebSocket &&
			(currentWebSocket.readyState === WebSocket.OPEN ||
				currentWebSocket.readyState === WebSocket.CONNECTING)
		) {
			return;
		}

		connectionAttempts++;
		console.log(`[Client WS] connect: Attempting (attempt #${connectionAttempts})...`);

		// Limit reconnection attempts
		if (connectionAttempts > 5) {
			console.error('[Client WS] connect: Max connection attempts reached.');
			return;
		}

		// Reset flag for new connection sequence
		isIntentionallyClosing = false;

		try {
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			currentWebSocket = new WebSocket(`${protocol}//${window.location.host}/ws`);

			currentWebSocket.onopen = () => {
				console.log('[Client WS] onopen: Connection successful!');
				isConnected = true;
				// Reset attempts on successful connection
				connectionAttempts = 0;
				if (reconnectTimerId) {
					clearTimeout(reconnectTimerId);
					reconnectTimerId = null;
				}
			};

			currentWebSocket.onmessage = (event: MessageEvent) => {
				const data = JSON.parse(event.data) as WebSocketIncomingData;
				console.log('[Client WS] onmessage: Received:', data);

				if (data.type === 'welcome') {
					currentUser = { username: data.username };
				} else if (data.type === 'history') {
					// Add history messages, filtering out any already present
					const newHistoryMessages = data.messages.filter(
						(histMsg) => !messages.some((existingMsg) => existingMsg.id === histMsg.id)
					);
					messages = [...messages, ...newHistoryMessages].sort((a, b) => a.timestamp - b.timestamp);
				} else if (data.type === 'message') {
					const serverMessage = data as ChatMessageFromServer;
					// Attempt to find and replace a pending message sent by this client
					const pendingMsgIndex = messages.findIndex(
						(msg) =>
							msg.id?.startsWith('client-') && // Check if it's a pending message
							msg.username === serverMessage.username &&
							msg.message === serverMessage.message
					);

					if (pendingMsgIndex > -1) {
						// Replace pending message with the server confirmed version
						const updatedMessages = [...messages];
						updatedMessages[pendingMsgIndex] = serverMessage;
						messages = updatedMessages.sort((a, b) => a.timestamp - b.timestamp);
					} else if (!messages.some((existingMsg) => existingMsg.id === serverMessage.id)) {
						// This is a new message (likely from another user) and not a duplicate
						messages = [...messages, serverMessage].sort((a, b) => a.timestamp - b.timestamp);
					}
				}
			};

			currentWebSocket.onclose = (event: CloseEvent) => {
				console.log(
					`[Client WS] onclose: Closed. Code: ${event.code}, Intentional: ${isIntentionallyClosing}`
				);
				isConnected = false;
				currentWebSocket = null;

				if (isIntentionallyClosing || connectionAttempts > 5) return;

				// Implement exponential backoff for reconnection attempts
				const timeout = Math.min(1000 * Math.pow(2, connectionAttempts), 30000);
				console.log(`[Client WS] onclose: Reconnecting in ${timeout / 1000}s...`);
				if (reconnectTimerId) clearTimeout(reconnectTimerId);
				reconnectTimerId = setTimeout(connect, timeout) as unknown as number;
			};

			currentWebSocket.onerror = (errorEvent: Event) => {
				console.error('[Client WS] onerror:', errorEvent);
				// onclose should follow and handle reconnection
			};
		} catch (err) {
			console.error('[Client WS] connect: Exception during WebSocket init:', err);
			if (!isIntentionallyClosing && connectionAttempts <= 5) {
				// Retry if WebSocket constructor failed
				const timeout = Math.min(1000 * Math.pow(2, connectionAttempts), 30000);
				if (reconnectTimerId) clearTimeout(reconnectTimerId);
				reconnectTimerId = setTimeout(connect, timeout) as unknown as number;
			}
		}
	}

	// Add message sent by the user to the UI immediately
	function sendMessageInternal(): void {
		if (
			!messageInput.trim() ||
			!currentWebSocket ||
			currentWebSocket.readyState !== WebSocket.OPEN ||
			!currentUser
		) {
			return;
		}
		const messageText = messageInput.trim();

		const pendingMsg: PendingChatMessage = {
			id: `client-${crypto.randomUUID()}`,
			type: 'message',
			username: currentUser.username,
			message: messageText,
			timestamp: Date.now()
		};
		messages = [...messages, pendingMsg].sort((a, b) => a.timestamp - b.timestamp);

		currentWebSocket.send(messageText);
		messageInput = '';
	}

	// Connect to WS on mount, disconnect on unmount
	$effect(() => {
		console.log('[Client $effect] Mount: Initializing connection sequence.');
		connectionAttempts = 0;
		isIntentionallyClosing = false;

		// Attempt initial connection
		connect();

		return () => {
			console.log('[Client $effect] Unmount: Cleaning up WebSocket.');

			// Signal that any subsequent close is intentional
			isIntentionallyClosing = true;
			if (reconnectTimerId) {
				clearTimeout(reconnectTimerId);
				reconnectTimerId = null;
			}
			if (currentWebSocket) {
				currentWebSocket.close(1000, 'Client component unmounting');
				currentWebSocket = null;
			}
		};
	});

	// Set username store value so it can be used in sidebar component
	$effect(() => {
		if (currentUser?.username) {
			usernameStore.set(currentUser.username);
		}
	});
</script>

<GestureAIDialog bind:gestureAIDialogOpen />

<div class="flex flex-grow flex-col overflow-hidden">
	<!-- Header with sidebar logic and breadcrumb component -->
	<header class="flex h-16 shrink-0 items-center justify-between gap-2">
		<div class="flex items-center gap-2 px-4">
			<Sidebar.Trigger class="-ml-1" />
			<Separator orientation="vertical" class="mr-2 h-4" />

			<Breadcrumb class="hidden sm:block">
				<BreadcrumbList
					class="rounded-lg border border-border bg-background px-3 py-2 shadow-sm shadow-black/5"
				>
					<BreadcrumbItem>
						<BreadcrumbLink href="/">GestureAI</BreadcrumbLink>
					</BreadcrumbItem>
					<BreadcrumbSeparator />
					<BreadcrumbItem>
						<BreadcrumbPage>Global Chat</BreadcrumbPage>
					</BreadcrumbItem>
				</BreadcrumbList>
			</Breadcrumb>
		</div>

		<!-- Show if user is connected to websocket -->
		<div class="mr-4">
			<Badge
				variant="outline"
				class="gap-1.5 rounded-lg border border-border bg-background px-3 py-2 shadow-sm shadow-black/5"
			>
				<span
					class="size-2 rounded-full {isConnected ? 'bg-emerald-500' : 'bg-red-500'}"
					aria-hidden="true"
				></span>
				{isConnected ? 'Connected' : 'Disconnected'}
			</Badge>
		</div>
	</header>

	<div class="flex flex-1 flex-col overflow-hidden px-2 sm:px-0">
		<!-- Chat area -->
		<div
			class="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-y-4 overflow-y-auto rounded"
			bind:this={autoScroll.ref}
		>
			{#each messages as message (message.id)}
				<div class="flex w-full {message.username === currentUser?.username ? 'justify-end' : ''}">
					<div class="flex flex-col">
						<b>
							{message.username}<span class="ml-2 text-xs text-muted-foreground">
								{formatTime(message.timestamp)}
							</span>
						</b>
						{message.message}
					</div>
				</div>
			{/each}
		</div>

		<!-- Input area -->
		<div class="mx-auto mt-4 flex w-full max-w-3xl shrink-0 items-center">
			<div class="w-full rounded-t backdrop-blur-lg">
				<form
					onsubmit={(event) => {
						event.preventDefault();
						sendMessageInternal();
					}}
					class="chat-shadow relative flex w-full flex-col gap-2 rounded-t-xl border border-b-0 border-primary/70 px-3 py-3 text-secondary-foreground max-sm:pb-6"
				>
					<textarea
						bind:value={messageInput}
						placeholder="Type your message here..."
						class="w-full resize-none bg-transparent text-base leading-6 text-foreground outline-none placeholder:text-secondary-foreground/60"
						aria-label="Message input"
						autocomplete="off"
						style="height: 48px !important;"
						onkeydown={(e) => {
							if (e.key === 'Enter' && !e.shiftKey) {
								e.preventDefault();
								if (messageInput.trim()) {
									sendMessageInternal();
								}
							}
						}}
					>
					</textarea>

					<!-- Action buttons -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-x-2">
							<!-- Open modal for  AI sign language recognition -->
							<button
								class="inline-flex h-auto items-center gap-2 rounded-full border border-secondary-foreground/10 px-2 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/40 hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 max-sm:p-2"
								onclick={() => {
									gestureAIDialogOpen = true;
								}}
							>
								<Hand class="size-4 shrink-0" />
								<span class="max-sm:hidden">Gesture AI</span>
							</button>

							<!-- Attach media button -->
							<label
								class="inline-flex h-auto cursor-pointer items-center gap-2 rounded-full border border-secondary-foreground/10 px-2 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/40 hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 max-sm:p-2"
								aria-label="Attach a file"
							>
								<input class="sr-only" type="file" />
								<Paperclip class="size-4 shrink-0" />
								<span class="max-sm:hidden">Attach</span>
							</label>
						</div>

						<!-- Send text button -->
						<Button
							onclick={sendMessageInternal}
							size="icon"
							type="submit"
							aria-label="Message requires text"
							disabled={!messageInput.trim()}
						>
							<ArrowUp />
						</Button>
					</div>
				</form>
			</div>
		</div>
	</div>
</div>

<style>
	.chat-shadow {
		box-shadow:
			rgba(0, 0, 0, 0.1) 0px 80px 50px 0px,
			rgba(0, 0, 0, 0.07) 0px 50px 30px 0px,
			rgba(0, 0, 0, 0.06) 0px 30px 15px 0px,
			rgba(0, 0, 0, 0.04) 0px 15px 8px,
			rgba(0, 0, 0, 0.04) 0px 6px 4px,
			rgba(0, 0, 0, 0.02) 0px 2px 2px;
	}
</style>
