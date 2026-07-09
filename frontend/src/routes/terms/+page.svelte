<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import { m } from '$lib/paraglide/messages';
</script>

<Seo title={m.terms_title()} description={m.terms_intro()} />

<div class="mx-auto max-w-2xl py-8">
	<Card title={m.terms_title()}>
		<div class="prose prose-stone dark:prose-invert max-w-none text-sm">
			<p>{m.terms_intro()}</p>
			<p>{m.terms_body()}</p>
		</div>
	</Card>
</div>
