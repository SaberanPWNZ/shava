import { apiFetch } from '$lib/api/client';
import type {
	Badge,
	Leaderboard,
	MeGamification,
	PublicGamification
} from '$lib/types/gamification';

export const gamificationApi = {
	me(): Promise<MeGamification> {
		return apiFetch<MeGamification>('/gamification/me/');
	},
	publicProfile(userId: number | string): Promise<PublicGamification> {
		return apiFetch<PublicGamification>(`/gamification/users/${userId}/public/`, {
			auth: false
		});
	},
	badges(): Promise<Badge[]> {
		return apiFetch<Badge[]>('/gamification/badges/', { auth: false });
	},
	leaderboard(period: 'week' | 'month' | 'all' = 'all'): Promise<Leaderboard> {
		return apiFetch<Leaderboard>(`/gamification/leaderboard/?period=${period}`, {
			auth: false
		});
	}
};

export const reviewsHelpfulApi = {
	vote(reviewId: number): Promise<{ helpful_count: number; voted: boolean }> {
		return apiFetch(`/reviews/${reviewId}/helpful/`, { method: 'POST' });
	},
	unvote(reviewId: number): Promise<{ helpful_count: number; voted: boolean }> {
		return apiFetch(`/reviews/${reviewId}/helpful/`, { method: 'DELETE' });
	}
};
