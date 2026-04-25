<script lang="ts">
	let {
		value = 0,
		interactive = false,
		onchange,
		size = 'md'
	} = $props<{
		value?: number;
		interactive?: boolean;
		onchange?: (stars: number) => void;
		size?: 'sm' | 'md' | 'lg';
	}>();

	const dims = { sm: 'h-4 w-4', md: 'h-5 w-5', lg: 'h-7 w-7' } as const;
	const stars = [1, 2, 3, 4, 5];

	function clickStar(n: number) {
		if (!interactive) return;
		onchange?.(n);
	}
</script>

<div class="inline-flex items-center gap-1" role={interactive ? 'radiogroup' : undefined} aria-label={`${value} out of 5 stars`}>
	{#each stars as n (n)}
		{@const filled = n <= Math.round(value)}
		{#if interactive}
			<button
				type="button"
				class="cursor-pointer text-zinc-300 transition hover:text-amber-400 focus:outline-none {filled ? 'text-amber-400' : ''}"
				aria-label={`${n} stars`}
				onclick={() => clickStar(n)}
			>
				<svg viewBox="0 0 24 24" fill="currentColor" class={dims[size as 'sm' | 'md' | 'lg']}>
					<path d="M12 17.3l-6.18 3.7 1.64-7.03L2 9.24l7.19-.61L12 2l2.81 6.63 7.19.61-5.46 4.73 1.64 7.03z" />
				</svg>
			</button>
		{:else}
			<svg
				viewBox="0 0 24 24"
				fill="currentColor"
				class="{dims[size as 'sm' | 'md' | 'lg']} {filled ? 'text-amber-400' : 'text-zinc-300'}"
			>
				<path d="M12 17.3l-6.18 3.7 1.64-7.03L2 9.24l7.19-.61L12 2l2.81 6.63 7.19.61-5.46 4.73 1.64 7.03z" />
			</svg>
		{/if}
	{/each}
	{#if !interactive}
		<span class="ml-1 text-sm text-zinc-600 dark:text-zinc-400">{Number(value).toFixed(1)}</span>
	{/if}
</div>
