<script lang="ts">
	import { onMount } from 'svelte';
	import ArticleCard from '$lib/components/articles/ArticleCard.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { articlesApi } from '$lib/api/places.api';
	import type { Article } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let articles = $state<Article[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let search = $state('');
	let category = $state('');

	async function load() {
		loading = true;
		error = null;
		try {
			const result = await articlesApi.list({ search, category });
			articles = result.results;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(load);
</script>

<Seo title={m.articles_title()} description={m.articles_seo_description()} />

<section class="flex flex-col gap-6">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="text-2xl font-bold text-stone-900 dark:text-stone-100">{m.articles_title()}</h1>
		<form
			class="flex flex-wrap gap-2"
			onsubmit={(e) => {
				e.preventDefault();
				void load();
			}}
		>
			<input
				type="search"
				placeholder={m.articles_search_placeholder()}
				bind:value={search}
				class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
			/>
			<select
				bind:value={category}
				class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
			>
				<option value="">{m.articles_all_categories()}</option>
				<option value="guide">{m.article_category_guide()}</option>
				<option value="review">{m.article_category_review()}</option>
				<option value="news">{m.article_category_news()}</option>
				<option value="recipe">{m.article_category_recipe()}</option>
				<option value="other">{m.article_category_other()}</option>
			</select>
			<button
				type="submit"
				class="rounded-lg bg-amber-700 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-800"
			>
				{m.articles_filter()}
			</button>
		</form>
	</header>

	{#if error}
		<p class="text-sm text-red-600">{error}</p>
	{/if}

	{#if loading}
		<p class="text-sm text-stone-500">{m.loading_ellipsis()}</p>
	{:else if articles.length === 0}
		<p class="text-sm text-stone-500">{m.articles_empty()}</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
			{#each articles as article (article.id)}
				<ArticleCard {article} />
			{/each}
		</div>
	{/if}
</section>
