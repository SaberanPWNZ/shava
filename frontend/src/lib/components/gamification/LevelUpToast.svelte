<script lang="ts">
	import { gamificationStore } from '$lib/stores/gamification.svelte';

	const variantClass: Record<string, string> = {
		points: 'bg-orange-600 text-white',
		level: 'bg-amber-500 text-white',
		badge: 'bg-emerald-600 text-white'
	};
</script>

{#if gamificationStore.toasts.length}
	<div
		class="pointer-events-none fixed bottom-4 right-4 z-50 flex flex-col gap-2"
		aria-live="polite"
	>
		{#each gamificationStore.toasts as toast (toast.id)}
			<div
				class="pointer-events-auto flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold shadow-lg {variantClass[
					toast.kind
				] ?? 'bg-zinc-800 text-white'}"
				role="status"
			>
				<span aria-hidden="true">{toast.icon ?? '⭐'}</span>
				<span>{toast.message}</span>
				<button
					type="button"
					class="ml-2 text-white/80 hover:text-white"
					aria-label="Dismiss notification"
					onclick={() => gamificationStore.dismissToast(toast.id)}
				>
					×
				</button>
			</div>
		{/each}
	</div>
{/if}
