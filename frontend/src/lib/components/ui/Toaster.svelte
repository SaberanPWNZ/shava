<script lang="ts">
	import { toasts, type Toast } from '$lib/stores/toasts.svelte';

	const variantClass: Record<Toast['variant'], string> = {
		success:
			'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-100',
		error:
			'border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-700 dark:bg-rose-950 dark:text-rose-100',
		info: 'border-zinc-200 bg-white text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100'
	};
</script>

<!--
	Live region for screen readers: status (polite) for success/info,
	alert (assertive) for errors. Buttons are keyboard-reachable with
	visible focus rings.
-->
<div
	class="pointer-events-none fixed right-4 bottom-4 z-50 flex max-w-sm flex-col gap-2 sm:right-6 sm:bottom-6"
	aria-live="polite"
	aria-atomic="false"
>
	{#each toasts.items as toast (toast.id)}
		<div
			class="pointer-events-auto flex items-start gap-3 rounded-lg border px-4 py-3 text-sm shadow-md {variantClass[
				toast.variant
			]}"
			role={toast.variant === 'error' ? 'alert' : 'status'}
		>
			<span class="flex-1">{toast.message}</span>
			<button
				type="button"
				class="-mr-1 -mt-1 inline-flex h-7 w-7 items-center justify-center rounded-md text-lg leading-none opacity-70 hover:opacity-100 focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none"
				aria-label="Dismiss notification"
				onclick={() => toasts.dismiss(toast.id)}
			>
				×
			</button>
		</div>
	{/each}
</div>
