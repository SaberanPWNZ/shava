/**
 * Global toast store (Svelte 5 runes flavour).
 *
 * Use anywhere in the app:
 *
 *   import { toasts } from '$lib/stores/toasts.svelte';
 *   toasts.success('Saved.');
 *   toasts.error('Could not save.');
 *
 * The single rendered host is `Toaster.svelte`, mounted in the root layout.
 */

export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
	id: number;
	message: string;
	variant: ToastVariant;
	/** Auto-dismiss timeout in ms; null disables auto-dismiss. */
	timeout: number | null;
}

const DEFAULT_TIMEOUT = 4000;

class ToastStore {
	#items = $state<Toast[]>([]);
	#nextId = 1;

	get items(): readonly Toast[] {
		return this.#items;
	}

	push(message: string, variant: ToastVariant = 'info', timeout: number | null = DEFAULT_TIMEOUT) {
		const id = this.#nextId++;
		const toast: Toast = { id, message, variant, timeout };
		this.#items = [...this.#items, toast];
		if (timeout !== null && typeof window !== 'undefined') {
			window.setTimeout(() => this.dismiss(id), timeout);
		}
		return id;
	}

	success(message: string, timeout: number | null = DEFAULT_TIMEOUT) {
		return this.push(message, 'success', timeout);
	}

	error(message: string, timeout: number | null = 6000) {
		return this.push(message, 'error', timeout);
	}

	info(message: string, timeout: number | null = DEFAULT_TIMEOUT) {
		return this.push(message, 'info', timeout);
	}

	dismiss(id: number) {
		this.#items = this.#items.filter((t) => t.id !== id);
	}

	clear() {
		this.#items = [];
	}
}

export const toasts = new ToastStore();
