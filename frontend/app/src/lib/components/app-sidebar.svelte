<script lang="ts" module>
	import { LifeBuoy, Send, MessageSquare } from '@lucide/svelte';

	const data = {
		user: {
			name: 'shadcn',
			avatar: ''
		},
		navMain: [
			{
				title: 'Public',
				url: '#',
				icon: MessageSquare,
				isActive: true,
				items: [
					{
						title: 'Global Chat',
						url: '#'
					},
					{
						title: 'Temporary Chat',
						url: '#'
					},
					{
						title: "User525's Chat",
						url: '#'
					},
					{
						title: "User526's Chat",
						url: '#'
					}
				]
			},
			{
				title: 'Private',
				url: '#',
				icon: MessageSquare,
				isActive: true,
				items: [
					{
						title: 'Group Chat 1',
						url: '#'
					},
					{
						title: 'Group Chat 2',
						url: '#'
					},
					{
						title: 'Group Chat 3',
						url: '#'
					},
					{
						title: 'Group Chat 4',
						url: '#'
					}
				]
			}
		],
		navSecondary: [
			{
				title: 'Support',
				url: '#',
				icon: LifeBuoy
			},
			{
				title: 'Feedback',
				url: '#',
				icon: Send
			}
		]
	};
</script>

<script lang="ts">
	import NavMain from '$lib/components/nav-main.svelte';
	import NavSecondary from '$lib/components/nav-secondary.svelte';
	import NavUser from '$lib/components/nav-user.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import Command from '@lucide/svelte/icons/command';
	import type { ComponentProps } from 'svelte';

	let { ref = $bindable(null), ...restProps }: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<Sidebar.Root bind:ref variant="inset" {...restProps}>
	<Sidebar.Header>
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg">
					{#snippet child({ props })}
						<a href="##" {...props}>
							<div
								class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
							>
								<Command class="size-4" />
							</div>
							<div class="grid flex-1 text-left text-sm leading-tight">
								<span class="truncate font-semibold">GestureAI</span>
								<span class="truncate text-xs">Enterprise</span>
							</div>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>
	<Sidebar.Content>
		<NavMain items={data.navMain} />
		<NavSecondary items={data.navSecondary} class="mt-auto" />
	</Sidebar.Content>
	<Sidebar.Footer>
		<NavUser user={data.user} />
	</Sidebar.Footer>
</Sidebar.Root>
