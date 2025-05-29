import type { Socket, Peer } from '@sveltejs/kit';
import { RedisChatService, type ChatMessage } from '$lib/server/redis-chat';

// Tracks active WebSocket peers
const activePeers = new Map<Peer, { username: string; peerId: string }>();

export const socket: Socket = {
	// Handles the initial HTTP request upgrade to WebSocket
	upgrade(req) {
		console.log(`[WS Server] HTTP upgrade request for: ${req.url}`);
	},

	// Called when a new WebSocket connection is established
	async open(peer) {
		const peerId = peer.id;
		console.log(`[WS Server] Peer ${peerId} connected, waiting for username...`);

		// Initialize with empty username, will be set when client sends it
		activePeers.set(peer, { username: '', peerId });
	},

	// Called when a message is received from a client
	async message(peer, messageData) {
		const userInfo = activePeers.get(peer);
		if (!userInfo) {
			console.warn(`[WS Server] Message from unknown peer ${peer.id}. Ignoring.`);
			return;
		}
		const { username, peerId } = userInfo;

		try {
			// Try to parse as JSON first
			let data;
			try {
				data = JSON.parse(String(messageData));
			} catch {
				// If not JSON, treat as plain text message
				data = { message: String(messageData).trim() };
			}

			// Handle username setting
			if (data.type === 'set_username') {
				const newUsername = data.username;
				userInfo.username = newUsername;
				activePeers.set(peer, userInfo);

				const chatService = RedisChatService.getInstance();
				await chatService.initialize();
				await chatService.saveUser(peerId, newUsername);
				console.log(`[WS Server] User ${newUsername} (${peerId}) registered.`);

				// Subscribe to chat
				peer.subscribe('chat');
				console.log(`[WS Server] Peer ${peerId} (${newUsername}) subscribed to 'chat'.`);

				// Send message history
				const recentMessages = await chatService.getRecentMessages(50);
				const userMessagesHistory = recentMessages.filter((msg) => msg.type === 'message');
				if (userMessagesHistory.length > 0) {
					peer.send(JSON.stringify({ type: 'history', messages: userMessagesHistory }));
					console.log(
						`[WS Server] Sent ${userMessagesHistory.length} history messages to ${peerId}.`
					);
				}
				return;
			}

			// Handle regular chat messages (only if username is set)
			if (!username) {
				peer.send(JSON.stringify({ type: 'error', message: 'Please set username first.' }));
				return;
			}

			const textMessage = data.message?.trim();
			if (!textMessage) return;

			const chatService = RedisChatService.getInstance();
			const chatMsgDto: ChatMessage = {
				type: 'message',
				message: textMessage,
				username: username,
				timestamp: Date.now()
			};

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

	// Called when a client connection is closed
	async close(peer, event) {
		const userInfo = activePeers.get(peer);
		const peerId = userInfo ? userInfo.peerId : peer.id;
		console.log(
			`[WS Server] Peer ${peerId} disconnected. Code: ${event?.code}, Reason: ${event?.reason}`
		);

		if (userInfo && userInfo.username) {
			try {
				await RedisChatService.getInstance().removeUser(peerId);
				console.log(`[WS Server] User ${userInfo.username} (${peerId}) removed from Redis.`);
			} catch (error) {
				console.error(`[WS Server] Error in close handler for ${peerId} (Redis cleanup):`, error);
			}
		}
		activePeers.delete(peer);
	},

	// Called when a WebSocket error occurs for a specific peer
	error(peer, errorData) {
		const userInfo = activePeers.get(peer);
		const peerId = userInfo ? userInfo.peerId : peer.id;
		console.error(`[WS Server] Error for peer ${peerId}:`, errorData);

		if (userInfo) {
			console.log(
				`[WS Server] Removing user ${userInfo.username} (${peerId}) from tracking due to error.`
			);
		}
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
