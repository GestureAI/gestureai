import { createClient, type RedisClientType } from 'redis';
import { REDIS_URL } from '$env/static/private';

// Define client type
let client: RedisClientType;

// Initialize client
const initializeClient = (): RedisClientType => {
	if (!client) {
		client = createClient({
			url: REDIS_URL || 'redis://redis:6379'
		});

		// Connection handling
		client.on('error', (err) => console.error('Redis Client Error:', err));
		client.on('connect', () => console.log('Redis Client Connected'));
	}

	return client;
};

// Get connected client
async function getClient(): Promise<RedisClientType> {
	const redisClient = initializeClient();

	if (!redisClient.isOpen) {
		await redisClient.connect();
	}

	return redisClient;
}

export { getClient };
