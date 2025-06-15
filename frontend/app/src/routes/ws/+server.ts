import type { Socket, Peer } from '@sveltejs/kit';
import { RedisChatService, type ChatMessage } from '$lib/server/redis-chat';

// In-memory tracking of active WebSocket connections
// Maps Peer objects to user information
const activePeers = new Map<Peer, { username: string; peerId: string }>();

export const socket: Socket = {
	// Step 1: HTTP to WebSocket upgrade - called before connection opens
	upgrade(req) {
		console.log(`[WS Server] HTTP upgrade request for: ${req.url}`);
	},

	// Step 2: New connection established - called after successful upgrade
	// Flow: Client connects -> open() -> wait for username -> subscribe to chat
	async open(peer) {
		const peerId = peer.id;
		console.log(`[WS Server] Peer ${peerId} connected, waiting for username...`);

		// Register peer with empty username - will be populated by 'set_username' message
		activePeers.set(peer, { username: '', peerId });
	},

	// Step 3: Message handling - called for every message from clients
	// Flow: Client sends -> message() -> parse -> save to Redis -> broadcast
	async message(peer, messageData) {
		const userInfo = activePeers.get(peer);
		if (!userInfo) {
			console.warn(`[WS Server] Message from unknown peer ${peer.id}. Ignoring.`);
			return;
		}
		const { username, peerId } = userInfo;

		try {
			// Message parsing - handles both JSON and plain text
			let data;
			try {
				data = JSON.parse(String(messageData));
			} catch {
				// Fallback for plain text messages from client
				data = { message: String(messageData).trim() };
			}

			// Username registration flow - first message from client
			if (data.type === 'set_username') {
				const newUsername = data.username;
				userInfo.username = newUsername;
				activePeers.set(peer, userInfo);

				// Initialize Redis service and save user
				const chatService = RedisChatService.getInstance();
				await chatService.initialize();
				await chatService.saveUser(peerId, newUsername);
				console.log(`[WS Server] User ${newUsername} (${peerId}) registered.`);

				// Subscribe to chat channel for real-time messages
				peer.subscribe('chat');
				console.log(`[WS Server] Peer ${peerId} (${newUsername}) subscribed to 'chat'.`);

				// Send chat history to new user
				const recentMessages = await chatService.getRecentMessages(100);
				const userMessagesHistory = recentMessages.filter((msg) => msg.type === 'message');
				if (userMessagesHistory.length > 0) {
					peer.send(JSON.stringify({ type: 'history', messages: userMessagesHistory }));
					console.log(
						`[WS Server] Sent ${userMessagesHistory.length} history messages to ${peerId}.`
					);
				}
				return;
			}

			// Regular message handling - requires username to be set first
			if (!username) {
				peer.send(JSON.stringify({ type: 'error', message: 'Please set username first.' }));
				return;
			}

			const textMessage = data.message?.trim();
			if (!textMessage) return;

			// Message processing pipeline: create -> save to Redis -> broadcast
			const chatService = RedisChatService.getInstance();
			const chatMsgDto: ChatMessage = {
				type: 'message',
				message: textMessage,
				username: username,
				timestamp: Date.now()
			};

			// Save to Redis and broadcast to all subscribed clients
			const savedMessage = await chatService.saveMessage(chatMsgDto);
			peer.publish('chat', JSON.stringify(savedMessage));
			console.log(`[WS Server] Msg from ${username} (ID: ${savedMessage.id}) saved & published.`);
		} catch (error) {
			console.error(`[WS Server] Error in message handler for ${peerId}:`, error);
			try {
				peer.send(JSON.stringify({ type: 'error', message: 'Error processing message.' }));
			} catch (e) {
				console.error(e);
			}
		}
	},

	// Step 4: Connection cleanup - called when client disconnects
	// Flow: Client disconnects -> close() -> remove from activePeers
	async close(peer, event) {
		const userInfo = activePeers.get(peer);
		const peerId = userInfo ? userInfo.peerId : peer.id;
		console.log(
			`[WS Server] Peer ${peerId} disconnected. Code: ${event?.code}, Reason: ${event?.reason}`
		);

		// Remove from active tracking
		activePeers.delete(peer);
	},

	// Error handling - called when WebSocket errors occur
	// Flow: Error occurs -> error() -> cleanup -> force close connection
	error(peer, errorData) {
		const userInfo = activePeers.get(peer);
		const peerId = userInfo ? userInfo.peerId : peer.id;
		console.error(`[WS Server] Error for peer ${peerId}:`, errorData);

		if (userInfo) {
			console.log(
				`[WS Server] Removing user ${userInfo.username} (${peerId}) from tracking due to error.`
			);
		}
		// Force cleanup on error
		activePeers.delete(peer);

		try {
			if (peer && typeof peer.close === 'function') {
				peer.close(1011, 'Unrecoverable server-side WebSocket error');
			}
		} catch (e) {
			console.error(e);
		}
	}
};
