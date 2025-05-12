import { getClient } from './redis';

export interface CacheOptions {
	expiry?: number;
}

export class RedisService {
	// Get a value from Redis
	static async get<T>(key: string): Promise<T | null> {
		const client = await getClient();
		const data = await client.get(key);

		if (!data) return null;

		try {
			return JSON.parse(data) as T;
		} catch {
			return data as unknown as T;
		}
	}

	// Set a value in Redis
	static async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
		const client = await getClient();
		const stringValue = typeof value === 'string' ? value : JSON.stringify(value);

		if (options.expiry) {
			await client.set(key, stringValue, { EX: options.expiry });
		} else {
			await client.set(key, stringValue);
		}
	}

	// Delete a key from Redis
	static async delete(key: string): Promise<boolean> {
		const client = await getClient();
		const result = await client.del(key);
		return result > 0;
	}

	// Check if a key exists
	static async exists(key: string): Promise<boolean> {
		const client = await getClient();
		const result = await client.exists(key);
		return result === 1;
	}
}
