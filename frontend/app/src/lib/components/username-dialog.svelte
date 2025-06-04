<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
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

<AlertDialog.Root bind:open={usernameDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Choose Your Username</AlertDialog.Title>
			<AlertDialog.Description>
				Please enter a username to join the chat. This will be visible to other users.
			</AlertDialog.Description>
		</AlertDialog.Header>
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

			<AlertDialog.Footer class="pt-4">
				<Button type="submit" disabled={!username.trim()}>Join Chat</Button>
			</AlertDialog.Footer>
		</form>
	</AlertDialog.Content>
</AlertDialog.Root>
