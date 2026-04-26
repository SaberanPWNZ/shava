<script lang="ts">
	import { onMount } from 'svelte';
	import ArticleCard from '$lib/components/articles/ArticleCard.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { articlesApi } from '$lib/api/places.api';
	import type { Article } from '$lib/types';

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

<Seo title="Articles" description="Reviews, guides, and recipes from the Shava community." />

<section class="flex flex-col gap-6">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Articles</h1>
		<form
			class="flex flex-wrap gap-2"
			onsubmit={(e) => {
				e.preventDefault();
				void load();
			}}
		>
			<input
				type="search"
				placeholder="Search…"
				bind:value={search}
				class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
			/>
			<select
				bind:value={category}
				class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
			>
				<option value="">All categories</option>
				<option value="guide">Guide</option>
				<option value="review">Review</option>
				<option value="news">News</option>
				<option value="recipe">Recipe</option>
				<option value="other">Other</option>
			</select>
			<button
				type="submit"
				class="rounded-lg bg-orange-700 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-800"
			>
				Filter
			</button>
		</form>
	</header>

	{#if error}
		<p class="text-sm text-red-600">{error}</p>
	{/if}

	{#if loading}
		<p class="text-sm text-zinc-500">Loading…</p>
	{:else if articles.length === 0}
		<p class="text-sm text-zinc-500">No articles published yet.</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
			{#each articles as article (article.id)}
				<ArticleCard {article} />
			{/each}
		</div>
	{/if}
</section>
