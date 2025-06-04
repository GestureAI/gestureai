import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const formData = await request.formData();

		const response = await fetch('https://gestureai.chat/api/check', {
			method: 'POST',
			body: formData
		});

		const result = await response.json();
		console.log('Gesture API Response:', result);

		return json(result);
	} catch (error) {
		console.error('Error proxying to gesture API:', error);
		return json({ error: 'Failed to process gesture' }, { status: 500 });
	}
};
