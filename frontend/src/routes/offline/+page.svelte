<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
</script>

<Seo title="You are offline" description="No network connection — Shava is offline." />

<section
	class="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center gap-4 text-center"
>
	<svg
		aria-hidden="true"
		class="h-16 w-16 text-orange-500"
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="1.5"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<path d="M5.633 13.5a9 9 0 0 1 12.734 0" />
		<path d="M2.808 9.787a13 13 0 0 1 18.384 0" />
		<path d="M8.46 17.213a5 5 0 0 1 7.08 0" />
		<line x1="3" y1="3" x2="21" y2="21" />
		<line x1="12" y1="20" x2="12" y2="20" />
	</svg>
	<h1 class="text-2xl font-semibold">You are offline</h1>
	<p class="text-sm text-zinc-600 dark:text-zinc-400">
		It looks like your device lost its connection. Some pages you visited
		recently may still be available.
	</p>
	<button
		type="button"
		class="rounded-md bg-orange-700 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-orange-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
		onclick={() => location.reload()}
	>
		Try again
	</button>
</section>
