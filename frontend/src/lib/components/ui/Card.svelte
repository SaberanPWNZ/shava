<script lang="ts">
	let { title = '', children } = $props<{ title?: string; children: import('svelte').Snippet }>();
</script>

<section
	class="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
>
	{#if title}
		<h2 class="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">{title}</h2>
	{/if}
	{@render children()}
</section>
