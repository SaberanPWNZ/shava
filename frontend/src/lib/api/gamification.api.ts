import { apiFetch } from '$lib/api/client';
import type {
	Badge,
	Leaderboard,
	MeGamification,
	PointsTransactionRecord,
	PublicGamification
} from '$lib/types/gamification';
import type { Paginated } from '$lib/types';

export const gamificationApi = {
	me(): Promise<MeGamification> {
		return apiFetch<MeGamification>('/gamification/me/');
	},
	myTransactions(page = 1): Promise<Paginated<PointsTransactionRecord>> {
		return apiFetch<Paginated<PointsTransactionRecord>>(
			`/gamification/me/transactions/?page=${page}`
		);
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
