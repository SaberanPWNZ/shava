<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<title>Shava - SvelteKit App</title>
	<meta name="description" content="A modern SvelteKit application with Tailwind CSS and routing" />
</svelte:head>

<div class="antialiased">
	{@render children?.()}
</div>
