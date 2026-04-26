<script lang="ts">
	import type { MenuItem } from '$lib/types';

	let { items = [] } = $props<{ items?: MenuItem[] }>();

	const categoryLabels: Record<string, string> = {
		shawarma: 'Shawarma',
		drinks: 'Drinks',
		sides: 'Sides',
		desserts: 'Desserts',
		other: 'Other'
	};

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
	<p class="text-sm text-zinc-500 dark:text-zinc-400">No menu items yet.</p>
{:else}
	<div class="flex flex-col gap-6">
		{#each grouped as [category, list] (category)}
			<section>
				<h3 class="mb-2 text-sm font-semibold tracking-wide text-zinc-500 uppercase">
					{categoryLabels[category] ?? category}
				</h3>
				<ul class="divide-y divide-zinc-200 dark:divide-zinc-800">
					{#each list as item (item.id)}
						<li class="flex items-start justify-between gap-3 py-2">
							<div>
								<p class="font-medium text-zinc-900 dark:text-zinc-100">
									{item.name || item.item_name || 'Item'}
								</p>
								{#if item.description}
									<p class="text-sm text-zinc-600 dark:text-zinc-400">{item.description}</p>
								{/if}
							</div>
							<span class="font-semibold text-zinc-900 dark:text-zinc-100">{item.price} ₴</span>
						</li>
					{/each}
				</ul>
			</section>
		{/each}
	</div>
{/if}
