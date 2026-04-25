import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// vi.mock factories are hoisted, so any variables they reference must be
// defined via vi.hoisted to be initialised before the mock factory runs.
const { gotoMock, authApiMock, gamificationMock } = vi.hoisted(() => ({
	gotoMock: vi.fn(async () => {}),
	authApiMock: {
		login: vi.fn(),
		register: vi.fn(),
		me: vi.fn(),
		updateMe: vi.fn(),
		logout: vi.fn()
	},
	gamificationMock: {
		refreshMe: vi.fn(async () => {}),
		reset: vi.fn(() => {})
	}
}));

vi.mock('$app/navigation', () => ({
	goto: gotoMock,
	invalidate: vi.fn(async () => {}),
	invalidateAll: vi.fn(async () => {}),
	preloadCode: vi.fn(async () => {}),
	preloadData: vi.fn(async () => {}),
	beforeNavigate: vi.fn(),
	afterNavigate: vi.fn(),
	disableScrollHandling: vi.fn(),
	pushState: vi.fn(),
	replaceState: vi.fn()
}));

vi.mock('$lib/api/auth.api', () => ({
	authApi: authApiMock,
	API_BASE: '/api'
}));

vi.mock('$lib/services/gamification.service', () => ({
	gamificationService: gamificationMock
}));

import { authService } from '$lib/services/auth.service';
import { authStore } from '$lib/stores/auth.svelte';
import { tokenStorage } from '$lib/api/client';
import { requireAuth, requireAdmin } from '$lib/guards/requireAuth';
import type { User } from '$lib/types/auth';

const aUser: User = {
	id: 1,
	email: 'a@b.com',
	first_name: 'A',
	last_name: 'B',
	is_staff: false
} as User;

beforeEach(() => {
	gotoMock.mockClear();
	for (const fn of Object.values(authApiMock)) fn.mockReset();
	authStore.reset();
	authStore.setHydrated(false);
	tokenStorage.clear();
});

afterEach(() => {
	vi.restoreAllMocks();
});

describe('authService.hydrate', () => {
	it('returns null and marks hydrated when no access token is stored', async () => {
		const user = await authService.hydrate();
		expect(user).toBeNull();
		expect(authStore.hydrated).toBe(true);
		expect(authApiMock.me).not.toHaveBeenCalled();
	});

	it('returns the cached user without re-fetching when already hydrated', async () => {
		authStore.setUser(aUser);
		authStore.setHydrated(true);
		const user = await authService.hydrate();
		expect(user).toEqual(aUser);
		expect(authApiMock.me).not.toHaveBeenCalled();
	});

	it('loads /me and stores the user when an access token exists', async () => {
		tokenStorage.set('access', 'refresh');
		authApiMock.me.mockResolvedValueOnce(aUser);

		const user = await authService.hydrate();

		expect(user).toEqual(aUser);
		expect(authStore.user).toEqual(aUser);
		expect(authStore.hydrated).toBe(true);
	});

	it('clears tokens and store when /me fails', async () => {
		tokenStorage.set('access', 'refresh');
		authApiMock.me.mockRejectedValueOnce(new Error('401'));

		const user = await authService.hydrate();

		expect(user).toBeNull();
		expect(tokenStorage.getAccess()).toBeNull();
		expect(authStore.hydrated).toBe(true);
	});
});

describe('authService.login', () => {
	it('calls login, fetches /me, and updates the store', async () => {
		authApiMock.login.mockResolvedValueOnce({ access: 'a', refresh: 'r' });
		authApiMock.me.mockResolvedValueOnce(aUser);

		const user = await authService.login('a@b.com', 'pw');

		expect(authApiMock.login).toHaveBeenCalledWith({ email: 'a@b.com', password: 'pw' });
		expect(user).toEqual(aUser);
		expect(authStore.user).toEqual(aUser);
		expect(authStore.hydrated).toBe(true);
	});
});

describe('authService.logout', () => {
	it('calls api.logout, resets the store, and navigates', async () => {
		authStore.setUser(aUser);
		authApiMock.logout.mockResolvedValueOnce(undefined);

		await authService.logout('/login');

		expect(authApiMock.logout).toHaveBeenCalled();
		expect(authStore.user).toBeNull();
		expect(gotoMock).toHaveBeenCalledWith('/login');
	});
});

describe('requireAuth', () => {
	it('redirects unauthenticated users to /login with `next`', async () => {
		// hydrate() will be called and find no token → unauthenticated.
		await requireAuth('/profile');
		expect(gotoMock).toHaveBeenCalledWith('/login?next=%2Fprofile');
	});

	it('does nothing when authenticated', async () => {
		authStore.setUser(aUser);
		authStore.setHydrated(true);
		await requireAuth('/profile');
		expect(gotoMock).not.toHaveBeenCalled();
	});
});

describe('requireAdmin', () => {
	it('redirects to / when authenticated but not admin', async () => {
		authStore.setUser(aUser);
		authStore.setHydrated(true);
		await requireAdmin('/admin');
		expect(gotoMock).toHaveBeenCalledWith('/');
	});

	it('lets admins through', async () => {
		authStore.setUser({ ...aUser, is_staff: true } as User);
		authStore.setHydrated(true);
		await requireAdmin('/admin');
		expect(gotoMock).not.toHaveBeenCalled();
	});
});
