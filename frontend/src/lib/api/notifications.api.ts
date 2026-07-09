import { apiFetch } from '$lib/api/client';
import type { AppNotification, Paginated } from '$lib/types';

export const notificationsApi = {
	list(page = 1): Promise<Paginated<AppNotification>> {
		return apiFetch<Paginated<AppNotification>>(`/notifications/?page=${page}`);
	},
	unreadCount(): Promise<{ unread: number }> {
		return apiFetch<{ unread: number }>('/notifications/unread-count/');
	},
	markRead(ids?: number[]): Promise<{ marked: number }> {
		return apiFetch<{ marked: number }>('/notifications/mark-read/', {
			method: 'POST',
			body: ids ? { ids } : {}
		});
	}
};
