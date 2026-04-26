import { apiFetch, tokenStorage, API_BASE } from '$lib/api/client';
import type { AuthTokens, User } from '$lib/types/auth';

interface LoginInput {
	email: string;
	password: string;
}

interface RegisterInput {
	email: string;
	password: string;
	first_name?: string;
	last_name?: string;
}

interface MeUpdateInput {
	first_name?: string;
	last_name?: string;
}

export const authApi = {
	async login(input: LoginInput): Promise<AuthTokens> {
		const tokens = await apiFetch<AuthTokens>('/token/', {
			method: 'POST',
			body: input,
			auth: false
		});
		tokenStorage.set(tokens.access, tokens.refresh);
		return tokens;
	},

	async register(input: RegisterInput): Promise<User> {
		return apiFetch<User>('/users/register/', {
			method: 'POST',
			body: input,
			auth: false
		});
	},

	async me(): Promise<User> {
		return apiFetch<User>('/users/me/');
	},

	async updateMe(input: MeUpdateInput): Promise<User> {
		return apiFetch<User>('/users/me/', {
			method: 'PATCH',
			body: input
		});
	},

	async logout(): Promise<void> {
		try {
			await apiFetch('/users/logout/', { method: 'POST' });
		} catch {
			// best-effort logout
		} finally {
			tokenStorage.clear();
		}
	},

	async requestVerifyEmail(): Promise<void> {
		await apiFetch('/users/verify-email/request/', { method: 'POST' });
	},

	async confirmVerifyEmail(token: string): Promise<User> {
		return apiFetch<User>('/users/verify-email/confirm/', {
			method: 'POST',
			body: { token },
			auth: false
		});
	},

	async requestPasswordReset(email: string): Promise<void> {
		await apiFetch('/users/password-reset/request/', {
			method: 'POST',
			body: { email },
			auth: false
		});
	},

	async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
		await apiFetch('/users/password-reset/confirm/', {
			method: 'POST',
			body: { token, new_password: newPassword },
			auth: false
		});
	}
};

export { API_BASE };
