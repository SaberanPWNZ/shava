import { goto } from '$app/navigation';
import { authService } from '$lib/services/auth.service';
import { authStore } from '$lib/stores/auth.svelte';

export async function requireAuth(currentPath = '/'): Promise<void> {
	if (!authStore.hydrated) {
		await authService.hydrate();
	}
	if (!authStore.isAuthenticated) {
		const next = encodeURIComponent(currentPath);
		await goto(`/login?next=${next}`);
	}
}

export async function requireAdmin(currentPath = '/'): Promise<void> {
	await requireAuth(currentPath);
	if (!authStore.isAdmin) {
		await goto('/');
	}
}
