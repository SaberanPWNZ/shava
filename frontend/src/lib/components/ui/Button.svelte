<script lang="ts">
	type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
	type Size = 'sm' | 'md' | 'lg';
	let {
		type = 'button',
		variant = 'primary' as Variant,
		size = 'md' as Size,
		block = false,
		loading = false,
		disabled = false,
		onclick,
		children
	} = $props<{
		type?: 'button' | 'submit' | 'reset';
		variant?: Variant;
		size?: Size;
		block?: boolean;
		loading?: boolean;
		disabled?: boolean;
		onclick?: (e: MouseEvent) => void;
		children: import('svelte').Snippet;
	}>();

	const variants: Record<Variant, string> = {
		primary:
			'bg-gradient-to-br from-amber-500 to-orange-600 text-white shadow-sm hover:from-amber-600 hover:to-orange-700 focus-visible:ring-amber-500',
		secondary:
			'border border-stone-300 bg-white text-stone-800 shadow-sm hover:border-amber-400 hover:text-amber-700 focus-visible:ring-amber-500 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100 dark:hover:border-amber-600 dark:hover:text-amber-400',
		danger: 'bg-red-600 text-white shadow-sm hover:bg-red-700 focus-visible:ring-red-500',
		ghost:
			'text-stone-700 hover:bg-stone-100 focus-visible:ring-amber-500 dark:text-stone-200 dark:hover:bg-stone-800'
	};

	const sizes: Record<Size, string> = {
		sm: 'min-h-9 px-3 py-1.5 text-sm',
		md: 'min-h-11 px-4 py-2 text-sm',
		lg: 'min-h-12 px-6 py-3 text-base'
	};
</script>

<button
	{type}
	disabled={disabled || loading}
	{onclick}
	class="inline-flex items-center justify-center rounded-xl font-semibold transition focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:focus-visible:ring-offset-stone-950 {variants[
		variant as Variant
	]} {sizes[size as Size]} {block ? 'w-full' : ''}"
>
	{#if loading}
		<span
			class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent opacity-80"
			aria-hidden="true"
		></span>
	{/if}
	{@render children()}
</button>
