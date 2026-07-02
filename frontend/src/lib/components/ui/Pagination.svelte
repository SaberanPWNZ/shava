<script lang="ts">
	import { m } from '$lib/paraglide/messages';

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
	<nav class="mt-4 flex items-center justify-between gap-3" aria-label={m.pagination_label()}>
		<button
			type="button"
			class="min-h-11 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:bg-stone-800"
			onclick={() => canPrev && onchange(page - 1)}
			disabled={!canPrev}
		>
			{m.pagination_prev()}
		</button>
		<span class="text-sm text-stone-600 dark:text-stone-400" aria-live="polite">
			{m.pagination_page_of({ page, total: totalPages })}
		</span>
		<button
			type="button"
			class="min-h-11 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:bg-stone-800"
			onclick={() => canNext && onchange(page + 1)}
			disabled={!canNext}
		>
			{m.pagination_next()}
		</button>
	</nav>
{/if}
