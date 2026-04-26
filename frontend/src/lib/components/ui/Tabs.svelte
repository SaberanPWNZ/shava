<script lang="ts">
	/**
	 * A small, fully keyboard-accessible tab list following the WAI-ARIA
	 * Tabs pattern (manual activation, ←/→/Home/End to move focus, Enter
	 * or click to activate).
	 *
	 * Usage:
	 *   <Tabs tabs={[{id:'a',label:'A'},{id:'b',label:'B'}]} bind:value={tab}>
	 *     {#snippet panel(id)}
	 *       {#if id === 'a'}...{/if}
	 *     {/snippet}
	 *   </Tabs>
	 */
	import type { Snippet } from 'svelte';

	export interface TabItem {
		id: string;
		label: string;
	}

	let {
		tabs,
		value = $bindable(),
		panel,
		ariaLabel = 'Tabs'
	}: {
		tabs: TabItem[];
		value: string;
		panel: Snippet<[string]>;
		ariaLabel?: string;
	} = $props();

	let buttons: HTMLButtonElement[] = $state([]);

	function focusTab(index: number) {
		const i = (index + tabs.length) % tabs.length;
		buttons[i]?.focus();
		value = tabs[i].id;
	}

	function onKey(event: KeyboardEvent, index: number) {
		switch (event.key) {
			case 'ArrowRight':
				event.preventDefault();
				focusTab(index + 1);
				break;
			case 'ArrowLeft':
				event.preventDefault();
				focusTab(index - 1);
				break;
			case 'Home':
				event.preventDefault();
				focusTab(0);
				break;
			case 'End':
				event.preventDefault();
				focusTab(tabs.length - 1);
				break;
		}
	}
</script>

<div class="flex flex-col gap-4">
	<div
		role="tablist"
		aria-label={ariaLabel}
		class="-mx-2 flex flex-wrap gap-1 overflow-x-auto border-b border-zinc-200 px-2 dark:border-zinc-800"
	>
		{#each tabs as tab, i (tab.id)}
			<button
				bind:this={buttons[i]}
				type="button"
				role="tab"
				id="tab-{tab.id}"
				aria-controls="tabpanel-{tab.id}"
				aria-selected={value === tab.id}
				tabindex={value === tab.id ? 0 : -1}
				onclick={() => (value = tab.id)}
				onkeydown={(e) => onKey(e, i)}
				class="min-h-11 px-4 py-2 text-sm font-medium whitespace-nowrap focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none {value ===
				tab.id
					? 'border-b-2 border-orange-600 text-orange-700 dark:text-orange-400'
					: 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100'}"
			>
				{tab.label}
			</button>
		{/each}
	</div>

	{#each tabs as tab (tab.id)}
		<div
			role="tabpanel"
			id="tabpanel-{tab.id}"
			aria-labelledby="tab-{tab.id}"
			hidden={value !== tab.id}
			tabindex="0"
			class="focus-visible:rounded-md focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none"
		>
			{#if value === tab.id}
				{@render panel(tab.id)}
			{/if}
		</div>
	{/each}
</div>
