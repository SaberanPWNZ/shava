import type { User } from '$lib/types/auth';

interface AuthState {
	user: User | null;
	hydrated: boolean;
}

function createAuthStore() {
	const state = $state<AuthState>({ user: null, hydrated: false });

	return {
		get user() {
			return state.user;
		},
		get hydrated() {
			return state.hydrated;
		},
		get isAuthenticated() {
			return state.user !== null;
		},
		get isAdmin() {
			return state.user?.is_staff === true;
		},
		setUser(user: User | null) {
			state.user = user;
		},
		setHydrated(value: boolean) {
			state.hydrated = value;
		},
		reset() {
			state.user = null;
		}
	};
}

export const authStore = createAuthStore();
