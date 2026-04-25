export interface Badge {
	code: string;
	title: string;
	description: string;
	icon: string;
	tier: 'bronze' | 'silver' | 'gold';
	points_reward: number;
}

export interface AwardedBadge extends Omit<Badge, 'points_reward'> {
	awarded_at: string;
}

export interface PointsTransactionRecord {
	id: number;
	amount: number;
	reason: string;
	ref_type: string;
	ref_id: number;
	created_at: string;
}

export interface MeGamification {
	points: number;
	level: number;
	level_title: string;
	next_threshold: number | null;
	progress_pct: number;
	badges: AwardedBadge[];
	recent_transactions: PointsTransactionRecord[];
}

export interface PublicGamification {
	user_id: number;
	username: string;
	points: number;
	level: number;
	level_title: string;
	next_threshold: number | null;
	progress_pct: number;
	badges: AwardedBadge[];
}

export interface LeaderboardEntry {
	user_id: number;
	username: string;
	points: number;
	level: number;
	level_title: string;
}

export interface Leaderboard {
	period: 'week' | 'month' | 'all';
	results: LeaderboardEntry[];
}
