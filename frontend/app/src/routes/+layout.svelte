<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';
	import Navbar from '$lib/components/navbar.svelte';

	let { children } = $props();
</script>

<ModeWatcher />

<div class="relative flex min-h-screen w-screen flex-col overflow-hidden">
	<Navbar />
	{@render children()}
</div>
