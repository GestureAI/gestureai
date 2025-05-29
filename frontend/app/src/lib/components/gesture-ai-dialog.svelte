<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Label } from '$lib/components/ui/label/index.js';

	let { gestureAIDialogOpen = $bindable<boolean>(false) } = $props();

	let videoElement: HTMLVideoElement;
	let stream: MediaStream | null = $state(null);

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
		} catch (error) {
			console.error('Error accessing webcam:', error);
		}
	}

	function stopWebcam() {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
	}
</script>

<Dialog.Root bind:open={gestureAIDialogOpen}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Gesture AI</Dialog.Title>
			<Dialog.Description
				>This AI reads your sign language from the webcam and converts it into text characters.</Dialog.Description
			>
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

		<Label for="gestureText">Gesture Text</Label>
		<Textarea
			id="gestureText"
			disabled
			placeholder="Your sign language text will be inputted here"
		/>

		<Dialog.Footer>
			<Button type="submit">Save</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
