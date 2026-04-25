import { describe, expect, it } from 'vitest';
import { authStore } from '$lib/stores/auth.svelte';
import type { User } from '$lib/types/auth';

const fakeUser: User = {
	id: 1,
	email: 'a@b.com',
	first_name: 'A',
	last_name: 'B',
	is_staff: false
} as User;

const adminUser: User = { ...fakeUser, id: 2, is_staff: true } as User;

describe('authStore', () => {
	it('starts unauthenticated and not hydrated', () => {
		// Reset to a known state because the store is a module-level
		// singleton that persists across imports.
		authStore.reset();
		authStore.setHydrated(false);

		expect(authStore.user).toBeNull();
		expect(authStore.isAuthenticated).toBe(false);
		expect(authStore.isAdmin).toBe(false);
		expect(authStore.hydrated).toBe(false);
	});

	it('setUser flips isAuthenticated', () => {
		authStore.setUser(fakeUser);
		expect(authStore.user).toEqual(fakeUser);
		expect(authStore.isAuthenticated).toBe(true);
		expect(authStore.isAdmin).toBe(false);
	});

	it('isAdmin tracks the is_staff flag', () => {
		authStore.setUser(adminUser);
		expect(authStore.isAdmin).toBe(true);
	});

	it('setHydrated toggles the hydrated flag without touching the user', () => {
		authStore.setUser(fakeUser);
		authStore.setHydrated(true);
		expect(authStore.hydrated).toBe(true);
		expect(authStore.user).toEqual(fakeUser);
	});

	it('reset() clears the user but leaves hydrated untouched', () => {
		authStore.setUser(fakeUser);
		authStore.setHydrated(true);
		authStore.reset();
		expect(authStore.user).toBeNull();
		expect(authStore.isAuthenticated).toBe(false);
		// hydrated is intentionally sticky — see store implementation.
		expect(authStore.hydrated).toBe(true);
	});
});
