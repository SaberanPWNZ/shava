<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
</script>

<Seo
	title="Shava"
	description="Discover the best shawarma places in town, leave reviews, and keep your favourites at hand."
/>

<section class="flex flex-col items-start gap-6 py-12">
	<h1
		class="text-4xl font-extrabold tracking-tight text-zinc-900 sm:text-5xl dark:text-zinc-50"
	>
		Order shawarma you'll <span class="text-orange-600">love</span>.
	</h1>
	<p class="max-w-2xl text-lg text-zinc-600 dark:text-zinc-300">
		Discover the best shawarma places in town, leave reviews, and keep your favourites at hand.
	</p>
	<div class="flex flex-wrap gap-3">
		<a
			href="/register"
			class="rounded-lg bg-orange-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-orange-700"
		>
			Get started
		</a>
		<a
			href="/login"
			class="rounded-lg border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
		>
			Sign in
		</a>
	</div>
</section>
