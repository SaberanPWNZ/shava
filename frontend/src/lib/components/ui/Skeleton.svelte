<script lang="ts">
	/**
	 * A bare-bones loading placeholder. Animated `pulse` background + Tailwind
	 * sizing classes via `class`. Use `lines={n}` for a multi-line text block,
	 * or pass a single instance for a custom shape.
	 *
	 * Always rendered with `aria-hidden="true"` and an off-screen "Loading…"
	 * label so assistive tech doesn't flag the placeholder as content.
	 */
	let {
		class: className = '',
		lines = 1,
		rounded = 'md',
		label = 'Loading'
	}: {
		class?: string;
		lines?: number;
		rounded?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
		label?: string;
	} = $props();

	const roundedClass = $derived(
		{
			sm: 'rounded',
			md: 'rounded-md',
			lg: 'rounded-lg',
			xl: 'rounded-xl',
			full: 'rounded-full'
		}[rounded]
	);
</script>

<span class="sr-only" role="status">{label}…</span>
{#if lines > 1}
	<div class="flex flex-col gap-2" aria-hidden="true">
		{#each Array.from({ length: lines }, (_, i) => i) as i (i)}
			<div
				class="h-3 animate-pulse bg-zinc-200/80 dark:bg-zinc-800 {roundedClass} {className}"
				style:width={i === lines - 1 ? '60%' : '100%'}
			></div>
		{/each}
	</div>
{:else}
	<div
		class="animate-pulse bg-zinc-200/80 dark:bg-zinc-800 {roundedClass} {className}"
		aria-hidden="true"
	></div>
{/if}
