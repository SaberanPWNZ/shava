<script lang="ts">
	let {
		title = '',
		subtitle = '',
		children
	} = $props<{ title?: string; subtitle?: string; children: import('svelte').Snippet }>();
</script>

<section
	class="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm sm:p-8 dark:border-stone-800 dark:bg-stone-900"
>
	{#if title}
		<h2 class="text-2xl font-bold tracking-tight text-stone-900 dark:text-stone-50">{title}</h2>
	{/if}
	{#if subtitle}
		<p class="mt-1 text-sm text-stone-500 dark:text-stone-400">{subtitle}</p>
	{/if}
	{#if title || subtitle}
		<div class="mt-6">
			{@render children()}
		</div>
	{:else}
		{@render children()}
	{/if}
</section>
