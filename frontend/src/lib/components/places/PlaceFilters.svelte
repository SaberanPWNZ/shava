<script lang="ts">
	import type { PlaceFilters } from '$lib/types';

	let { filters = $bindable<PlaceFilters>({}), onapply } = $props<{
		filters?: PlaceFilters;
		onapply?: () => void;
	}>();

	const districts = [
		{ value: '', label: 'All districts' },
		{ value: 'Dnipro', label: 'Дніпровський' },
		{ value: 'Desna', label: 'Деснянський' },
		{ value: 'Solomyanka', label: "Солом'янський" },
		{ value: 'Shevchenko', label: 'Шевченківський' },
		{ value: 'Pechersk', label: 'Печерський' },
		{ value: 'Obolon', label: 'Оболонський' },
		{ value: 'Podil', label: 'Подільський' },
		{ value: 'Svyatoshyn', label: 'Святошинський' },
		{ value: 'Holosiiv', label: 'Голосіївський' },
		{ value: 'Darnytsia', label: 'Дарницький' }
	];

	const orderings = [
		{ value: '', label: 'Default' },
		{ value: '-rating', label: 'Top rated' },
		{ value: 'rating', label: 'Lowest rating' },
		{ value: '-created_at', label: 'Newest' },
		{ value: 'name', label: 'Name A-Z' }
	];

	function apply(event: Event) {
		event.preventDefault();
		onapply?.();
	}

	function reset() {
		filters.city = '';
		filters.district = '';
		filters.delivery = false;
		filters.is_featured = false;
		filters.has_menu = false;
		filters.min_stars = undefined;
		filters.search = '';
		filters.ordering = '';
		onapply?.();
	}
</script>

<form
	class="flex flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
	onsubmit={apply}
>
	<h3 class="text-base font-semibold text-zinc-900 dark:text-zinc-100">Filters</h3>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">Search</span>
		<input
			type="search"
			placeholder="Name or description"
			bind:value={filters.search}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">City</span>
		<input
			type="search"
			placeholder="e.g. Київ, Львів, kyiv"
			bind:value={filters.city}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">District</span>
		<select
			bind:value={filters.district}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		>
			{#each districts as d (d.value)}
				<option value={d.value}>{d.label}</option>
			{/each}
		</select>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">Minimum stars</span>
		<select
			bind:value={filters.min_stars}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		>
			<option value={undefined}>Any</option>
			<option value={1}>1+</option>
			<option value={2}>2+</option>
			<option value={3}>3+</option>
			<option value={4}>4+</option>
			<option value={5}>5</option>
		</select>
	</label>

	<label class="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
		<input type="checkbox" bind:checked={filters.delivery} class="rounded" />
		Delivery available
	</label>
	<label class="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
		<input type="checkbox" bind:checked={filters.is_featured} class="rounded" />
		Featured only
	</label>
	<label class="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
		<input type="checkbox" bind:checked={filters.has_menu} class="rounded" />
		Has menu
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">Sort</span>
		<select
			bind:value={filters.ordering}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		>
			{#each orderings as o (o.value)}
				<option value={o.value}>{o.label}</option>
			{/each}
		</select>
	</label>

	<div class="flex gap-2">
		<button
			type="submit"
			class="flex-1 rounded-lg bg-orange-700 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-800"
		>
			Apply
		</button>
		<button
			type="button"
			onclick={reset}
			class="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-800"
		>
			Reset
		</button>
	</div>
</form>
