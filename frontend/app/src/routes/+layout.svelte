<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';
	import AppSidebar from '$lib/components/app-sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { usernameStore } from '$lib/stores';
	import UsernameDialog from '$lib/components/username-dialog.svelte';
	let { children } = $props();
</script>

<ModeWatcher />
{#if $usernameStore}
	<div class="flex max-h-screen">
		<Sidebar.Provider>
			<AppSidebar />
			<Sidebar.Inset>
				{@render children()}
			</Sidebar.Inset>
		</Sidebar.Provider>
	</div>
{:else}
	<UsernameDialog usernameDialogOpen={true} />
{/if}
