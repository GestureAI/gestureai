import { createClient, type RedisClientType } from 'redis';
import { REDIS_URL } from '$env/static/private';

// Message structure - standardizes chat message format across the app
export interface ChatMessage {
	id?: string; // Server-generated unique ID.
	type: 'message' | 'system' | 'welcome';
	username: string;
	message: string;
	timestamp: number;
}

// Singleton service class - manages all Redis chat operations
// Ensures single Redis connection for chat functionality
export class RedisChatService {
	private static instance: RedisChatService;
	private client: RedisClientType | null = null;
	private initialized = false;

	private constructor() {}

	// Singleton pattern - ensures only one instance exists across the app
	// Called by WebSocket server to get the service instance
	public static getInstance(): RedisChatService {
		if (!RedisChatService.instance) {
			RedisChatService.instance = new RedisChatService();
		}
		return RedisChatService.instance;
	}

	// Initialization - sets up Redis connection with error handling
	// Called once when first accessing the service
	public async initialize(): Promise<void> {
		if (this.initialized) return;
		this.client = createClient({
			url: REDIS_URL || 'redis://redis:6379'
		});
		this.client.on('error', (err) => console.error('Redis Client Error:', err));
		await this.client.connect();
		this.initialized = true;
	}

	// Internal helper - ensures client is ready before operations
	// Called by all public methods before Redis operations
	private async getClient(): Promise<RedisClientType> {
		if (!this.initialized || !this.client) {
			await this.initialize();
		}
		return this.client!;
	}

	// Core message storage - called when WebSocket receives new messages
	// Flow: WebSocket message -> saveMessage -> Redis ZADD -> return enhanced message
	public async saveMessage(message: ChatMessage): Promise<ChatMessage> {
		const client = await this.getClient();
		// Server enriches message with ID and timestamp if missing
		if (!message.id) {
			message.id = crypto.randomUUID();
		}
		if (!message.timestamp) {
			message.timestamp = Date.now();
		}
		// Redis Sorted Set stores messages ordered by timestamp (score)
		await client.zAdd('chat:messages', {
			score: message.timestamp,
			value: JSON.stringify(message)
		});
		// Memory management - keeps only recent 500 messages
		await client.zRemRangeByRank('chat:messages', 0, -501);
		return message;
	}

	// Message retrieval - called when new users connect to get chat history
	// Flow: WebSocket open -> getRecentMessages -> send to client
	public async getRecentMessages(limit = 100): Promise<ChatMessage[]> {
		const client = await this.getClient();
		// Gets latest messages from Redis Sorted Set (highest scores = newest)
		const messageStrings = await client.zRange('chat:messages', -limit, -1);
		return messageStrings.map((msgStr) => JSON.parse(msgStr) as ChatMessage);
	}

	// User session management - stores username associated with peer ID
	// Called when WebSocket receives 'set_username' message
	public async saveUser(peerId: string, username: string): Promise<void> {
		const client = await this.getClient();
		await client.set(`user:${peerId}`, username);
		await client.expire(`user:${peerId}`, 259200); // User data expires in 3 days.
	}

	// User retrieval - gets username for a given peer ID
	// Used for message attribution and user management
	public async getUser(peerId: string): Promise<string | null> {
		const client = await this.getClient();
		return client.get(`user:${peerId}`);
	}

	// Cleanup
	public async removeUser(peerId: string): Promise<void> {
		const client = await this.getClient();
		await client.del(`user:${peerId}`);
	}
}
