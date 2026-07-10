<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { toasts, type Toast } from '$lib/stores/toasts.svelte';

	const variantClass: Record<Toast['variant'], string> = {
		success:
			'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-100',
		error:
			'border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-700 dark:bg-rose-950 dark:text-rose-100',
		info: 'border-stone-200 bg-white text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100'
	};
</script>

<div
	class="pointer-events-none fixed right-4 bottom-4 z-50 flex max-w-sm flex-col gap-2 sm:right-6 sm:bottom-6"
	aria-live="polite"
	aria-atomic="false"
>
	{#each toasts.items as toast (toast.id)}
		<div
			class="pointer-events-auto flex items-start gap-3 rounded-lg border shadow-md {variantClass[
				toast.variant
			]} {toast.size === 'lg' ? 'max-w-md px-5 py-4 text-base' : 'px-4 py-3 text-sm'}"
			role={toast.variant === 'error' ? 'alert' : 'status'}
		>
			<span class="flex-1 {toast.size === 'lg' ? 'font-medium' : ''}">{toast.message}</span>
			<button
				type="button"
				class="-mr-1 -mt-1 inline-flex h-7 w-7 items-center justify-center rounded-md text-lg leading-none opacity-70 hover:opacity-100 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none"
				aria-label={m.toast_dismiss()}
				onclick={() => toasts.dismiss(toast.id)}
			>
				×
			</button>
		</div>
	{/each}
</div>
