<script lang="ts">
	import type { PlaceFilters } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { filters = $bindable<PlaceFilters>({}), onapply } = $props<{
		filters?: PlaceFilters;
		onapply?: () => void;
	}>();

	const districts = $derived([
		{ value: '', label: m.filters_all_districts() },
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
	]);

	const orderings = $derived([
		{ value: '', label: m.sort_default() },
		{ value: '-rating', label: m.sort_top_rated() },
		{ value: 'rating', label: m.sort_lowest_rating() },
		{ value: '-created_at', label: m.sort_newest() },
		{ value: 'name', label: m.sort_name_az() }
	]);

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
	class="flex flex-col gap-4 rounded-xl border border-stone-200 bg-white p-4 shadow-sm dark:border-stone-800 dark:bg-stone-900"
	onsubmit={apply}
>
	<h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">{m.filters_title()}</h3>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.filters_search()}</span>
		<input
			type="search"
			placeholder={m.filters_search_placeholder()}
			bind:value={filters.search}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.filters_city()}</span>
		<input
			type="search"
			placeholder={m.filters_city_placeholder()}
			bind:value={filters.city}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.filters_district()}</span>
		<select
			bind:value={filters.district}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		>
			{#each districts as d (d.value)}
				<option value={d.value}>{d.label}</option>
			{/each}
		</select>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.filters_min_stars()}</span>
		<select
			bind:value={filters.min_stars}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		>
			<option value={undefined}>{m.filters_any()}</option>
			<option value={1}>1+</option>
			<option value={2}>2+</option>
			<option value={3}>3+</option>
			<option value={4}>4+</option>
			<option value={5}>5</option>
		</select>
	</label>

	<label class="flex items-center gap-2 text-sm text-stone-700 dark:text-stone-300">
		<input type="checkbox" bind:checked={filters.delivery} class="rounded" />
		{m.filters_delivery_available()}
	</label>
	<label class="flex items-center gap-2 text-sm text-stone-700 dark:text-stone-300">
		<input type="checkbox" bind:checked={filters.is_featured} class="rounded" />
		{m.filters_featured_only()}
	</label>
	<label class="flex items-center gap-2 text-sm text-stone-700 dark:text-stone-300">
		<input type="checkbox" bind:checked={filters.has_menu} class="rounded" />
		{m.filters_has_menu()}
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.filters_sort()}</span>
		<select
			bind:value={filters.ordering}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		>
			{#each orderings as o (o.value)}
				<option value={o.value}>{o.label}</option>
			{/each}
		</select>
	</label>

	<div class="flex gap-2">
		<button
			type="submit"
			class="flex-1 rounded-lg bg-amber-700 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-800"
		>
			{m.filters_apply()}
		</button>
		<button
			type="button"
			onclick={reset}
			class="rounded-lg border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-200 dark:hover:bg-stone-800"
		>
			{m.filters_reset()}
		</button>
	</div>
</form>
