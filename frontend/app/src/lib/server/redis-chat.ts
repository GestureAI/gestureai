import { createClient, type RedisClientType } from 'redis';
import { REDIS_URL } from '$env/static/private';

// Defines the structure for chat messages.
export interface ChatMessage {
	id?: string; // Server-generated unique ID.
	type: 'message' | 'system' | 'welcome';
	username: string;
	message: string;
	timestamp: number;
}

// Service for chat interactions with Redis, using a singleton pattern.
export class RedisChatService {
	private static instance: RedisChatService;
	private client: RedisClientType | null = null;
	private initialized = false;

	private constructor() {}

	public static getInstance(): RedisChatService {
		if (!RedisChatService.instance) {
			RedisChatService.instance = new RedisChatService();
		}
		return RedisChatService.instance;
	}

	// Connects to Redis if not already connected.
	public async initialize(): Promise<void> {
		if (this.initialized) return;
		this.client = createClient({
			url: REDIS_URL || 'redis://redis:6379'
		});
		this.client.on('error', (err) => console.error('Redis Client Error:', err));
		await this.client.connect();
		this.initialized = true;
	}

	private async getClient(): Promise<RedisClientType> {
		if (!this.initialized || !this.client) {
			await this.initialize();
		}
		return this.client!;
	}

	// Saves a message, assigning an ID and timestamp if dont present from client, and returns the full message.
	public async saveMessage(message: ChatMessage): Promise<ChatMessage> {
		const client = await this.getClient();
		if (!message.id) {
			message.id = crypto.randomUUID();
		}
		if (!message.timestamp) {
			message.timestamp = Date.now();
		}
		// Stores messages in a Redis Sorted Set, ordered by timestamp.
		await client.zAdd('chat:messages', {
			score: message.timestamp,
			value: JSON.stringify(message)
		});
		// Keeps only the last 500 messages.
		await client.zRemRangeByRank('chat:messages', 0, -501);
		return message;
	}

	public async getRecentMessages(limit = 100): Promise<ChatMessage[]> {
		const client = await this.getClient();
		const messageStrings = await client.zRange('chat:messages', -limit, -1);
		return messageStrings.map((msgStr) => JSON.parse(msgStr) as ChatMessage);
	}

	public async saveUser(peerId: string, username: string): Promise<void> {
		const client = await this.getClient();
		await client.set(`user:${peerId}`, username);
		await client.expire(`user:${peerId}`, 259200); // User data expires in 3 days.
	}

	public async getUser(peerId: string): Promise<string | null> {
		const client = await this.getClient();
		return client.get(`user:${peerId}`);
	}

	public async removeUser(peerId: string): Promise<void> {
		const client = await this.getClient();
		await client.del(`user:${peerId}`);
	}
}
