import { apiFetch, sessionFlags, API_BASE } from '$lib/api/client';
import type { User } from '$lib/types/auth';
import type { UserPublicProfile } from '$lib/types';

interface LoginInput {
	email: string;
	password: string;
}

interface RegisterInput {
	email: string;
	password: string;
	first_name?: string;
	last_name?: string;
	phone?: string;
	city?: number;
	terms_accepted: boolean;
	marketing_opt_in?: boolean;
}

interface MeUpdateInput {
	first_name?: string;
	last_name?: string;
	phone?: string;
	bio?: string;
	city?: number | null;
	marketing_opt_in?: boolean;
}

export const authApi = {
	async login(input: LoginInput): Promise<void> {
		// Tokens arrive as HttpOnly cookies; the body copy is ignored so the
		// browser never handles raw tokens in JavaScript.
		await apiFetch('/token/', {
			method: 'POST',
			body: input,
			auth: false
		});
		sessionFlags.markSession();
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
			// The refresh token is read from the HttpOnly cookie server-side;
			// the response blacklists it and clears both cookies.
			await apiFetch('/users/logout/', { method: 'POST' });
		} catch {
			// best-effort logout
		} finally {
			sessionFlags.clear();
		}
	},

	async changePassword(oldPassword: string, newPassword: string): Promise<void> {
		await apiFetch('/users/me/change-password/', {
			method: 'POST',
			body: { old_password: oldPassword, new_password: newPassword }
		});
	},

	async deleteAccount(password: string): Promise<void> {
		// The backend clears the auth cookies on the 204 response.
		await apiFetch('/users/me/delete/', {
			method: 'POST',
			body: { password }
		});
		sessionFlags.clear();
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
	},

	publicProfile(userId: number | string): Promise<UserPublicProfile> {
		return apiFetch<UserPublicProfile>(`/users/${userId}/public/`, { auth: false });
	}
};

export { API_BASE };
