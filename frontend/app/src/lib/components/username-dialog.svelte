<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { usernameStore } from '$lib/stores';

	let { usernameDialogOpen = $bindable<boolean>(false) } = $props();
	let username = $state<string>('');

	function handleSubmit() {
		const trimmed = username.trim();
		if (trimmed) {
			usernameStore.set(trimmed);
			usernameDialogOpen = false;
		}
	}
</script>

<Dialog.Root bind:open={usernameDialogOpen}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Choose Your Username</Dialog.Title>
			<Dialog.Description>
				Please enter a username to join the chat. This will be visible to other users.
			</Dialog.Description>
		</Dialog.Header>
		<form onsubmit={handleSubmit}>
			<Label for="username">Username</Label>
			<Input
				id="username"
				placeholder="e.g., ChattyPatty14"
				required
				autofocus
				maxlength={20}
				bind:value={username}
			/>

			<Dialog.Footer class="pt-4">
				<Button type="submit" disabled={!username.trim()}>Join Chat</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
