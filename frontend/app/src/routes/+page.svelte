<script lang="ts">
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
		return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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

	function handleKeydown(e: KeyboardEvent): void {
		if (e.key === 'Enter') {
			e.preventDefault();
			sendMessageInternal();
		}
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
</script>

<h1>Global Chat</h1>

<div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
{#if currentUser}
	<div>Username: {currentUser.username}</div>
{/if}

<div class="mb-3 h-64 overflow-y-auto border p-10">
	{#each messages as message (message.id)}
		<div>
			<b>{message.username}</b> ({formatTime(message.timestamp)}): {message.message}
		</div>
	{/each}
</div>

<div>
	<input
		type="text"
		bind:value={messageInput}
		placeholder="Type a message..."
		onkeydown={handleKeydown}
		disabled={!isConnected}
	/>
	<button onclick={sendMessageInternal} disabled={!isConnected || !messageInput.trim()}>Send</button
	>
</div>
