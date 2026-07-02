<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { articlesApi } from '$lib/api/places.api';
	import type { Article } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let article = $state<Article | null>(null);
	let error = $state<string | null>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			article = await articlesApi.detail(page.params.slug ?? '');
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

{#if loading}
	<p class="text-sm text-stone-500">{m.loading_ellipsis()}</p>
{:else if error}
	<Alert variant="error">{error}</Alert>
{:else if article}
	<Seo
		title={article.title}
		description={article.excerpt ?? m.article_seo_fallback({ category: article.category })}
		image={article.cover_image ?? ''}
		type="article"
	/>
	<article class="mx-auto flex max-w-3xl flex-col gap-4 py-6">
		<a href="/articles" class="text-sm text-amber-700 hover:underline">{m.article_back()}</a>
		<span class="text-xs font-medium tracking-wide text-amber-700 uppercase">
			{article.category}
		</span>
		<h1 class="text-3xl font-bold text-stone-900 dark:text-stone-100">{article.title}</h1>
		<p class="text-sm text-stone-500">
			{new Date(article.published_at).toLocaleDateString()}
			{#if article.author_name}· {article.author_name}{/if}
		</p>
		{#if article.cover_image}
			<img src={article.cover_image} alt={article.title} class="rounded-xl object-cover" />
		{/if}
		<div class="prose prose-zinc dark:prose-invert max-w-none whitespace-pre-wrap">
			{article.content ?? ''}
		</div>
	</article>
{/if}
