<script lang="ts">
	/**
	 * Minimal, accessible pagination for `?page=N`-style cursorless paged
	 * APIs. Renders Prev / "Page X of Y" / Next; both buttons disable when
	 * there's no neighbour. Pure presentation — the parent owns state and
	 * the `onchange` callback fetches the new page.
	 */
	let {
		page,
		count,
		pageSize = 10,
		onchange
	}: {
		page: number;
		count: number;
		pageSize?: number;
		onchange: (next: number) => void;
	} = $props();

	let totalPages = $derived(Math.max(1, Math.ceil(count / pageSize)));
	let canPrev = $derived(page > 1);
	let canNext = $derived(page < totalPages);
</script>

{#if count > pageSize}
	<nav
		class="mt-4 flex items-center justify-between gap-3"
		aria-label="Pagination"
	>
		<button
			type="button"
			class="min-h-11 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
			onclick={() => canPrev && onchange(page - 1)}
			disabled={!canPrev}
		>
			← Prev
		</button>
		<span class="text-sm text-zinc-600 dark:text-zinc-400" aria-live="polite">
			Page {page} of {totalPages}
		</span>
		<button
			type="button"
			class="min-h-11 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
			onclick={() => canNext && onchange(page + 1)}
			disabled={!canNext}
		>
			Next →
		</button>
	</nav>
{/if}
