<script lang="ts">
	import type {
		UploadedFile,
		ChatMessageFromServer,
		PendingChatMessage,
		DisplayMessage,
		WebSocketIncomingData,
		User
	} from '$lib/types';
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
	import { Paperclip, ArrowUp, Hand, X } from '@lucide/svelte';
	import * as Avatar from '$lib/components/ui/avatar/index.js';
	import GestureAIDialog from '$lib/components/gesture-ai-dialog.svelte';
	import { createUploadThing } from '$lib/utils/uploadthing';
	import { toast } from 'svelte-sonner';

	const { startUpload } = createUploadThing('imageUploader', {});

	const autoScroll = new UseAutoScroll();

	// Component state - reactive variables that trigger UI updates
	let gestureAIDialogOpen = $state<boolean>(false);
	let messages = $state<DisplayMessage[]>([]);
	let messageInput = $state<string>('');
	let isConnected = $state<boolean>(false);
	let currentUser = $derived<User>({ username: $usernameStore });
	let imageFile = $state<UploadedFile | null>(null);
	let finalText = $state<string>('');

	// Reactive effect - updates message input when gesture AI provides text
	$effect(() => {
		if (finalText) {
			messageInput = finalText;
		}
	});

	// Utility function for displaying message timestamps
	function formatTime(timestamp: number): string {
		return new Date(timestamp).toLocaleTimeString([], {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	// WebSocket connection management variables
	let currentWebSocket: WebSocket | null = null;
	let connectionAttempts = 0;
	let reconnectTimerId: number | null = null;
	// Flag to prevent auto-reconnect on intentional close
	let isIntentionallyClosing = false;

	// WebSocket connection establishment with retry logic
	// Flow: connect() -> WebSocket creation -> event handlers setup -> username sending
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

		// Circuit breaker - prevents infinite reconnection attempts
		if (connectionAttempts > 20) {
			console.error('[Client WS] connect: Max connection attempts reached.');
			return;
		}

		// Reset flag for new connection sequence
		isIntentionallyClosing = false;

		try {
			// Protocol selection based on current page protocol (http/https)
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			currentWebSocket = new WebSocket(`${protocol}//${window.location.host}/ws`);

			// Connection success handler - sends username immediately after connection
			currentWebSocket.onopen = () => {
				console.log('[Client WS] onopen: Connection successful!');
				// Critical: Send username as first message to register with server
				if (currentWebSocket && $usernameStore) {
					currentWebSocket.send(
						JSON.stringify({
							type: 'set_username',
							username: $usernameStore
						})
					);
				}
				isConnected = true;
				// Reset connection attempts on success
				connectionAttempts = 0;
				if (reconnectTimerId) {
					clearTimeout(reconnectTimerId);
					reconnectTimerId = null;
				}
			};

			// Message handler - processes incoming messages from WebSocket server
			// Flow: Server message -> onmessage -> parse -> update local state
			currentWebSocket.onmessage = (event: MessageEvent) => {
				const data = JSON.parse(event.data) as WebSocketIncomingData;
				console.log('[Client WS] onmessage: Received:', data);

				// Handle chat history - sent when first connecting
				if (data.type === 'history') {
					// Add history messages, filtering out any already present
					const newHistoryMessages = data.messages.filter(
						(histMsg) => !messages.some((existingMsg) => existingMsg.id === histMsg.id)
					);
					messages = [...messages, ...newHistoryMessages].sort((a, b) => a.timestamp - b.timestamp);
				} else if (data.type === 'message') {
					const serverMessage = data as ChatMessageFromServer;
					// Optimistic UI update handling - replace pending message with server confirmation
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

			// Connection close handler - manages reconnection logic
			currentWebSocket.onclose = (event: CloseEvent) => {
				console.log(
					`[Client WS] onclose: Closed. Code: ${event.code}, Intentional: ${isIntentionallyClosing}`
				);
				isConnected = false;
				currentWebSocket = null;

				// Skip reconnection if intentional close or max attempts reached
				if (isIntentionallyClosing || connectionAttempts > 20) return;

				// Exponential backoff reconnection strategy
				const timeout = Math.min(1000 * Math.pow(2, connectionAttempts), 30000);
				console.log(`[Client WS] onclose: Reconnecting in ${timeout / 1000}s...`);
				if (reconnectTimerId) clearTimeout(reconnectTimerId);
				reconnectTimerId = setTimeout(connect, timeout) as unknown as number;
			};

			// Error handler - logs errors, onclose will handle reconnection
			currentWebSocket.onerror = (errorEvent: Event) => {
				console.error('[Client WS] onerror:', errorEvent);
			};
		} catch (err) {
			console.error('[Client WS] connect: Exception during WebSocket init:', err);
			// Retry if WebSocket constructor failed
			if (!isIntentionallyClosing && connectionAttempts <= 20) {
				const timeout = Math.min(1000 * Math.pow(2, connectionAttempts), 30000);
				if (reconnectTimerId) clearTimeout(reconnectTimerId);
				reconnectTimerId = setTimeout(connect, timeout) as unknown as number;
			}
		}
	}

	// Message sending with optimistic UI updates
	// Flow: User input -> sendMessageInternal -> add to UI -> send to server -> server confirms
	function sendMessageInternal(): void {
		if (
			!messageInput.trim() ||
			!currentWebSocket ||
			currentWebSocket.readyState !== WebSocket.OPEN ||
			!currentUser
		) {
			return;
		}

		imageFile = null;
		const messageText = messageInput.trim();

		// Optimistic UI update - show message immediately before server confirmation
		const pendingMsg: PendingChatMessage = {
			id: `client-${crypto.randomUUID()}`, // Temporary client-side ID
			type: 'message',
			username: $usernameStore,
			message: messageText,
			timestamp: Date.now()
		};
		messages = [...messages, pendingMsg].sort((a, b) => a.timestamp - b.timestamp);

		// Send to server - will be replaced by server confirmation in onmessage
		currentWebSocket.send(messageText);
		messageInput = '';
	}

	// Component lifecycle - establishes connection on mount, cleans up on unmount
	// Flow: Component mount -> $effect -> connect() -> WebSocket lifecycle
	$effect(() => {
		console.log('[Client $effect] Mount: Initializing connection sequence.');
		connectionAttempts = 0;
		isIntentionallyClosing = false;

		// Start initial connection attempt
		connect();

		// Cleanup function - called when component is destroyed
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
</script>

<GestureAIDialog bind:gestureAIDialogOpen bind:finalText />

<div class="flex flex-grow flex-col overflow-hidden">
	<!-- Header with sidebar logic and breadcrumb component -->
	<header class="border-border flex h-16 shrink-0 items-center justify-between gap-2 border-b">
		<div class="flex items-center gap-2 px-4">
			<Sidebar.Trigger class="-ml-1" />
			<Separator orientation="vertical" class="mr-2 h-4" />

			<Breadcrumb class="hidden sm:block">
				<BreadcrumbList>
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
			<Badge variant="outline" class="gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium">
				<span
					class="size-1.5 rounded-full {isConnected ? 'bg-success' : 'bg-destructive'}"
					aria-hidden="true"
				></span>
				<span class="text-muted-foreground">{isConnected ? 'Connected' : 'Disconnected'}</span>
			</Badge>
		</div>
	</header>

	<div class="flex flex-1 flex-col overflow-hidden px-2 sm:px-0">
		<!-- Chat area -->
		<div
			class="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-y-1 overflow-y-auto rounded p-4"
			bind:this={autoScroll.ref}
		>
			{#each messages as message, i (message.id)}
				{@const isOwn = message.username === $usernameStore}
				{@const showHeader = i === 0 || messages[i - 1].username !== message.username}
				{#if showHeader && i !== 0}
					<div class="mt-2"></div>
				{/if}
				<div class="flex {isOwn ? 'justify-end' : 'justify-start'}">
					<div class="flex max-w-[75%] gap-2 {isOwn ? 'flex-row-reverse' : 'flex-row'}">
						<!-- Avatar (only on first message of a group) -->
						{#if showHeader}
							<Avatar.Root class="mt-1 h-8 w-8 shrink-0">
								<Avatar.Fallback>{message.username[0]}</Avatar.Fallback>
							</Avatar.Root>
						{:else}
							<div class="w-8 shrink-0"></div>
						{/if}

						<div class="flex flex-col {isOwn ? 'items-end' : 'items-start'}">
							{#if showHeader}
								<div class="flex items-baseline gap-2 px-1 pb-1">
									<span class="text-sm font-semibold">{message.username}</span>
									<span class="text-muted-foreground text-xs"
										>{formatTime(message.timestamp)}</span
									>
								</div>
							{/if}

							<!-- Message bubble -->
							<div
								class="rounded-2xl px-3 py-2 {isOwn
									? 'bg-primary/18 text-foreground rounded-tr-sm'
									: 'bg-muted rounded-tl-sm'}"
							>
								{#if message.message && message.message.includes('dd8kg243vt.ufs.sh')}
									<img
										src={message.message}
										alt="Uploaded"
										class="max-h-64 max-w-full rounded-lg"
									/>
								{:else}
									<p class="whitespace-pre-wrap text-sm leading-relaxed">
										{message.message}
									</p>
								{/if}
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Input area -->
		<div class="mx-auto flex w-full max-w-3xl shrink-0 items-center pb-4">
			<div class="w-full rounded-xl">
				<form
					onsubmit={(event) => {
						event.preventDefault();
						sendMessageInternal();
					}}
					class="bg-card border-border relative flex w-full flex-col gap-2 rounded-xl border px-3 py-3 shadow-sm"
				>
					<!-- Preview of image uploaded by the user -->
					{#if imageFile}
						<div class="group relative inline-block self-start">
							<img class="max-h-12 w-auto rounded" src={imageFile.ufsUrl} alt="Uploaded File" />
							<button
								class="bg-muted text-primary-foreground absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full p-1 opacity-0 transition-opacity group-hover:opacity-100"
								onclick={() => (imageFile = null)}
							>
								<X />
							</button>
						</div>
					{/if}
					<textarea
						bind:value={messageInput}
						placeholder="Type your message here..."
						class="text-foreground placeholder:text-muted-foreground w-full resize-none bg-transparent text-sm leading-6 outline-none"
						aria-label="Message input"
						autocomplete="off"
						disabled={!!imageFile}
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
							<!-- Open modal for AI sign language recognition -->
							<button
								class="text-muted-foreground hover:bg-accent hover:text-accent-foreground inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium transition-colors max-sm:p-2"
								onclick={() => {
									gestureAIDialogOpen = true;
								}}
							>
								<Hand class="size-4 shrink-0" />
								<span class="max-sm:hidden">Gesture AI</span>
							</button>

							<!-- Attach image button -->
							<label
								class="text-muted-foreground hover:bg-accent hover:text-accent-foreground inline-flex cursor-pointer items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium transition-colors max-sm:p-2"
								aria-label="Attach a file"
							>
								<input
									class="sr-only"
									type="file"
									onchange={async (e) => {
										const file = e.currentTarget.files?.[0];
										if (!file) return;

										// Create promise for file upload
										const uploadPromise = startUpload([file]);

										// Set up the toast notifications
										toast.promise(uploadPromise, {
											loading: `Uploading ${file.name}...`,
											success: (data) => {
												// Add safety check for data
												if (data && data.length > 0) {
													const uploadedFile = data[0];
													return `${uploadedFile.name} uploaded successfully!`;
												}
												// Fallback message if data is undefined or empty
												return 'File uploaded successfully!';
											},
											error: 'Upload failed :( Try again!'
										});

										// Await the actual result
										try {
											const output = await uploadPromise;
											if (output && output.length > 0) {
												imageFile = output[0];
												messageInput = imageFile.ufsUrl;
											}
										} catch (error) {
											console.error('Upload error:', error);
										}
									}}
								/>
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
