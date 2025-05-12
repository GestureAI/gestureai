import { RedisService } from '$lib/server/redis-service';
import { json, type RequestEvent } from '@sveltejs/kit';

export async function GET({ url }: RequestEvent) {
	const key = url.searchParams.get('key');

	if (!key) {
		return json({ error: 'Key parameter is required' }, { status: 400 });
	}

	try {
		const value = await RedisService.get(key);

		if (value === null) {
			return json({ error: 'Key not found' }, { status: 404 });
		}

		return json({ key, value });
	} catch (error) {
		console.error('Redis error:', error);
		return json({ error: 'Server error' }, { status: 500 });
	}
}

export async function POST({ request }: RequestEvent) {
	try {
		const { key, value, expiry } = await request.json();

		if (!key || value === undefined) {
			return json({ error: 'Key and value are required' }, { status: 400 });
		}

		await RedisService.set(key, value, { expiry });

		return json({ success: true, key, value });
	} catch (error) {
		console.error('Redis error:', error);
		return json({ error: 'Server error' }, { status: 500 });
	}
}

export async function DELETE({ url }: RequestEvent) {
	const key = url.searchParams.get('key');

	if (!key) {
		return json({ error: 'Key parameter is required' }, { status: 400 });
	}

	try {
		const deleted = await RedisService.delete(key);

		return json({ success: true, deleted });
	} catch (error) {
		console.error('Redis error:', error);
		return json({ error: 'Server error' }, { status: 500 });
	}
}
