<script lang="ts">
	import type { Article } from '$lib/types';

	let { article } = $props<{ article: Article }>();
</script>

<a
	href={`/articles/${article.slug}`}
	class="block overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm transition hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
>
	{#if article.cover_image}
		<img
			src={article.cover_image}
			alt={article.title}
			class="h-44 w-full object-cover"
			loading="lazy"
		/>
	{/if}
	<div class="p-4">
		<span class="text-xs font-medium tracking-wide text-orange-600 uppercase">
			{article.category}
		</span>
		<h3 class="mt-1 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
			{article.title}
		</h3>
		{#if article.excerpt}
			<p class="mt-1 line-clamp-3 text-sm text-zinc-600 dark:text-zinc-400">
				{article.excerpt}
			</p>
		{/if}
		<p class="mt-3 text-xs text-zinc-500 dark:text-zinc-500">
			{new Date(article.published_at).toLocaleDateString()}
			{#if article.author_name}· {article.author_name}{/if}
		</p>
	</div>
</a>
