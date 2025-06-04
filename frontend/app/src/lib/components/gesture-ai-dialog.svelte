<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';

	let { gestureAIDialogOpen = $bindable<boolean>(false), finalText = $bindable<string>('') } =
		$props();

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let stream: MediaStream | null = $state(null);
	let captureInterval: ReturnType<typeof setInterval> | null = $state(null);
	let gestureText = $state('');
	let chars = $state<string[]>([]);
	let charGuess = $state<string>('');

	function save() {
		finalText = gestureText;
		gestureAIDialogOpen = false;
	}

	// Start webcam when dialog opens
	$effect(() => {
		if (gestureAIDialogOpen && videoElement) {
			startWebcam();
		} else if (!gestureAIDialogOpen && stream) {
			stopWebcam();
		}
	});

	async function startWebcam() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({
				video: true
			});
			videoElement.srcObject = stream;

			// Start capturing frames once video is playing
			videoElement.onloadedmetadata = () => {
				startFrameCapture();
			};
		} catch (error) {
			console.error('Error accessing webcam:', error);
		}
	}

	function stopWebcam() {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
		stopFrameCapture();
	}

	function startFrameCapture() {
		if (captureInterval) return;

		captureInterval = setInterval(async () => {
			await captureAndSendFrame();
		}, 500);
	}

	function stopFrameCapture() {
		if (captureInterval) {
			clearInterval(captureInterval);
			captureInterval = null;
		}
	}

	async function captureAndSendFrame() {
		if (!videoElement || !canvasElement) return;

		const canvas = canvasElement;
		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		// Set canvas dimensions to match video
		canvas.width = videoElement.videoWidth;
		canvas.height = videoElement.videoHeight;

		// Draw current video frame to canvas
		ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

		// Convert canvas to blob
		canvas.toBlob(
			async (blob) => {
				if (!blob) return;

				try {
					const formData = new FormData();
					formData.append('file', blob, 'proxy-image.jpeg');

					// Use local proxy endpoint instead of direct API call to bypass cors (temp)
					const response = await fetch('/api/gesture', {
						method: 'POST',
						body: formData
					});

					const result = await response.json();
					if (chars.length >= 10) {
						chars.shift();
					}

					if (result.is_recognized) {
						chars.push(result.char);
						charGuess = result.char;
					} else if (chars.length > 0) {
						const mostFrequentChar = chars.sort(
							(a, b) => chars.filter((v) => v === b).length - chars.filter((v) => v === a).length
						)[0];
						gestureText += mostFrequentChar;
						chars.length = 0;
						charGuess = '';
					}
				} catch (error) {
					console.error('Error sending frame to API:', error);
				}
			},
			'image/jpeg',
			0.8
		);
	}
</script>

<Dialog.Root bind:open={gestureAIDialogOpen}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Gesture AI</Dialog.Title>
			<Dialog.Description>
				This AI reads your sign language from the webcam and converts it into text characters.
			</Dialog.Description>
		</Dialog.Header>

		<!-- Webcam Preview -->
		<div class="mb-4 flex justify-center">
			<video
				bind:this={videoElement}
				autoplay
				muted
				playsinline
				class="w-full rounded-lg border bg-muted object-cover"
			></video>
		</div>

		<!-- Hidden canvas for frame capture -->
		<canvas bind:this={canvasElement} style="display: none;"></canvas>

		<p class="mx-auto text-2xl font-medium uppercase">{charGuess}</p>

		<Label for="gestureText">Gesture Text</Label>
		<Textarea
			id="gestureText"
			bind:value={gestureText}
			placeholder="Your sign language text will be inputted here"
		/>

		<Dialog.Footer>
			<Button type="submit" onclick={save}>Save</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
