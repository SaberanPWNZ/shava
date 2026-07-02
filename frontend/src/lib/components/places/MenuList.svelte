<script lang="ts">
	import type { MenuItem } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { items = [] } = $props<{ items?: MenuItem[] }>();

	const categoryLabels = $derived<Record<string, string>>({
		shawarma: m.menu_category_shawarma(),
		drinks: m.menu_category_drinks(),
		sides: m.menu_category_sides(),
		desserts: m.menu_category_desserts(),
		other: m.menu_category_other()
	});

	let grouped = $derived.by(() => {
		const map: Record<string, MenuItem[]> = {};
		for (const item of items) {
			const key = item.category || 'other';
			(map[key] ??= []).push(item);
		}
		return Object.entries(map);
	});
</script>

{#if items.length === 0}
	<p class="text-sm text-stone-500 dark:text-stone-400">{m.menu_empty()}</p>
{:else}
	<div class="flex flex-col gap-6">
		{#each grouped as [category, list] (category)}
			<section>
				<h3 class="mb-2 text-sm font-semibold tracking-wide text-stone-500 uppercase">
					{categoryLabels[category] ?? category}
				</h3>
				<ul class="divide-y divide-stone-200 dark:divide-stone-800">
					{#each list as item (item.id)}
						<li class="flex items-start justify-between gap-3 py-2">
							<div>
								<p class="font-medium text-stone-900 dark:text-stone-100">
									{item.name || item.item_name || m.menu_item_fallback()}
								</p>
								{#if item.description}
									<p class="text-sm text-stone-600 dark:text-stone-400">{item.description}</p>
								{/if}
							</div>
							<span class="font-semibold text-stone-900 dark:text-stone-100">{item.price} ₴</span>
						</li>
					{/each}
				</ul>
			</section>
		{/each}
	</div>
{/if}
