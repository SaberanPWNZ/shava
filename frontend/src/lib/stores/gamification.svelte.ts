import type { AwardedBadge, MeGamification } from '$lib/types/gamification';

interface ToastEvent {
	id: number;
	kind: 'points' | 'badge' | 'level';
	message: string;
	icon?: string;
}

interface GamificationState {
	me: MeGamification | null;
	loaded: boolean;
	loading: boolean;
	toasts: ToastEvent[];
}

let toastSeq = 0;

function createGamificationStore() {
	const state = $state<GamificationState>({
		me: null,
		loaded: false,
		loading: false,
		toasts: []
	});

	function pushToast(toast: Omit<ToastEvent, 'id'>) {
		const t: ToastEvent = { id: ++toastSeq, ...toast };
		state.toasts = [...state.toasts, t];
		// Auto-dismiss after 4s.
		setTimeout(() => dismissToast(t.id), 4000);
	}

	function dismissToast(id: number) {
		state.toasts = state.toasts.filter((t) => t.id !== id);
	}

	return {
		get me() {
			return state.me;
		},
		get loaded() {
			return state.loaded;
		},
		get loading() {
			return state.loading;
		},
		get toasts() {
			return state.toasts;
		},
		setMe(me: MeGamification | null) {
			const previous = state.me;
			state.me = me;
			state.loaded = true;
			if (previous && me) {
				const delta = me.points - previous.points;
				if (delta > 0) {
					pushToast({
						kind: 'points',
						message: `+${delta} points`,
						icon: '⭐'
					});
				}
				if (me.level > previous.level) {
					pushToast({
						kind: 'level',
						message: `Level up — ${me.level_title}!`,
						icon: '🏆'
					});
				}
				const previousCodes = new Set(previous.badges.map((b) => b.code));
				for (const badge of me.badges) {
					if (!previousCodes.has(badge.code)) {
						pushToast({
							kind: 'badge',
							message: `New badge: ${badge.title}`,
							icon: badge.icon || '🏅'
						});
					}
				}
			}
		},
		setLoading(value: boolean) {
			state.loading = value;
		},
		reset() {
			state.me = null;
			state.loaded = false;
			state.toasts = [];
		},
		notifyBadges(badges: AwardedBadge[]) {
			for (const b of badges) {
				pushToast({ kind: 'badge', message: `New badge: ${b.title}`, icon: b.icon || '🏅' });
			}
		},
		dismissToast
	};
}

export const gamificationStore = createGamificationStore();
