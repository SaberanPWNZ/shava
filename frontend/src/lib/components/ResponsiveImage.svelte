<!--
@component ResponsiveImage

Renders an `<img>` driven by the backend `*_thumbnails` payload (see
`backend/config/thumbnails.py` and `ImageThumbnails` in `$lib/types`).
Falls back to the plain `src` URL when no thumbnail bundle is
attached, so callers can pass either shape interchangeably:

```svelte
<ResponsiveImage
    thumbnails={place.main_image_thumbnails}
    src={place.main_image}
    alt={place.name}
    sizes="(min-width: 768px) 33vw, 100vw"
    class="h-40 w-full object-cover"
    loading="lazy"
/>
```

Browsers pick the smallest source that satisfies the layout width, so
mobile users no longer pay the cost of a 1024 px hero on a 320 px
screen.
-->
<script lang="ts">
	import type { ImageThumbnails } from '$lib/types';

	let {
		thumbnails = null,
		src = null,
		alt = '',
		sizes = '100vw',
		loading = 'lazy',
		decoding = 'async',
		class: cls = '',
		fallback
	}: {
		thumbnails?: ImageThumbnails | null;
		src?: string | null;
		alt?: string;
		sizes?: string;
		loading?: 'lazy' | 'eager';
		decoding?: 'async' | 'sync' | 'auto';
		class?: string;
		fallback?: import('svelte').Snippet;
	} = $props();

	const resolved = $derived(thumbnails?.src ?? src ?? null);
	const srcset = $derived(thumbnails?.srcset ?? null);
</script>

{#if resolved}
	<img
		src={resolved}
		srcset={srcset ?? undefined}
		{sizes}
		{alt}
		{loading}
		{decoding}
		class={cls}
	/>
{:else if fallback}
	{@render fallback()}
{/if}
