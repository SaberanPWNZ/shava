<script lang="ts">
	import ResponsiveImage from '$lib/components/ResponsiveImage.svelte';
	import type { Article } from '$lib/types';

	let { article } = $props<{ article: Article }>();
</script>

<a
	href={`/articles/${article.slug}`}
	class="block overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm transition hover:shadow-md dark:border-stone-800 dark:bg-stone-900"
>
	<ResponsiveImage
		thumbnails={article.cover_image_thumbnails}
		src={article.cover_image}
		alt={article.title}
		sizes="(min-width: 768px) 33vw, 100vw"
		class="h-44 w-full object-cover"
	/>
	<div class="p-4">
		<span class="text-xs font-medium tracking-wide text-amber-700 uppercase">
			{article.category}
		</span>
		<h3 class="mt-1 text-lg font-semibold text-stone-900 dark:text-stone-100">
			{article.title}
		</h3>
		{#if article.excerpt}
			<p class="mt-1 line-clamp-3 text-sm text-stone-600 dark:text-stone-400">
				{article.excerpt}
			</p>
		{/if}
		<p class="mt-3 text-xs text-stone-500 dark:text-stone-500">
			{new Date(article.published_at).toLocaleDateString()}
			{#if article.author_name}· {article.author_name}{/if}
		</p>
	</div>
</a>
