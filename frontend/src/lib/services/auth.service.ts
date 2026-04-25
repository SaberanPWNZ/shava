import { goto } from '$app/navigation';
import { authApi } from '$lib/api/auth.api';
import { tokenStorage } from '$lib/api/client';
import { authStore } from '$lib/stores/auth.svelte';
import { gamificationService } from '$lib/services/gamification.service';
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
			void gamificationService.refreshMe();
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
		void gamificationService.refreshMe();
		return user;
	},

	async logout(redirectTo = '/login'): Promise<void> {
		await authApi.logout();
		authStore.reset();
		gamificationService.reset();
		await goto(redirectTo);
	}
};
