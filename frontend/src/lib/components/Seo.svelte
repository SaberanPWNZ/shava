<script lang="ts">
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';

	let {
		title,
		description = 'Discover the best shawarma places in town, leave reviews, and keep your favourites at hand.',
		image = '',
		type = 'website',
		canonical = ''
	}: {
		title: string;
		description?: string;
		image?: string;
		type?: 'website' | 'article' | 'profile';
		canonical?: string;
	} = $props();

	// Source of truth for the public origin used in canonical / OG URLs.
	// Falls back to the request origin so SSR works without configuration
	// in dev / preview environments.
	const siteUrl = $derived(
		(env.PUBLIC_SITE_URL ?? '').replace(/\/$/, '') || page.url.origin
	);
	const fullTitle = $derived(title.endsWith('Shava') ? title : `${title} · Shava`);
	const canonicalUrl = $derived(canonical || `${siteUrl}${page.url.pathname}`);
	const ogImage = $derived(
		image ? (image.startsWith('http') ? image : `${siteUrl}${image}`) : ''
	);
</script>

<svelte:head>
	<title>{fullTitle}</title>
	<meta name="description" content={description} />
	<link rel="canonical" href={canonicalUrl} />

	<!-- Open Graph -->
	<meta property="og:type" content={type} />
	<meta property="og:title" content={fullTitle} />
	<meta property="og:description" content={description} />
	<meta property="og:url" content={canonicalUrl} />
	<meta property="og:site_name" content="Shava" />
	{#if ogImage}
		<meta property="og:image" content={ogImage} />
	{/if}

	<!-- Twitter / X -->
	<meta name="twitter:card" content={ogImage ? 'summary_large_image' : 'summary'} />
	<meta name="twitter:title" content={fullTitle} />
	<meta name="twitter:description" content={description} />
	{#if ogImage}
		<meta name="twitter:image" content={ogImage} />
	{/if}
</svelte:head>
