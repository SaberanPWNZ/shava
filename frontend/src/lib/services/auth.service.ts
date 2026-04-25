import { goto } from '$app/navigation';
import { authApi } from '$lib/api/auth.api';
import { tokenStorage } from '$lib/api/client';
import { authStore } from '$lib/stores/auth.svelte';
import type { User } from '$lib/types/auth';

export const authService = {
	async hydrate(): Promise<User | null> {
		if (authStore.hydrated) return authStore.user;
		const access = tokenStorage.getAccess();
		if (!access) {
			authStore.setHydrated(true);
			return null;
		}
		try {
			const user = await authApi.me();
			authStore.setUser(user);
		} catch {
			tokenStorage.clear();
			authStore.reset();
		} finally {
			authStore.setHydrated(true);
		}
		return authStore.user;
	},

	async login(email: string, password: string): Promise<User> {
		await authApi.login({ email, password });
		const user = await authApi.me();
		authStore.setUser(user);
		authStore.setHydrated(true);
		return user;
	},

	async logout(redirectTo = '/login'): Promise<void> {
		await authApi.logout();
		authStore.reset();
		await goto(redirectTo);
	}
};
