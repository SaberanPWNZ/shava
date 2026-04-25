import { apiFetch } from '$lib/api/client';
import type {
	Article,
	MenuItem,
	Paginated,
	Place,
	PlaceDetail,
	PlaceFilters,
	Review
} from '$lib/types';

function buildQuery(params: Record<string, unknown>): string {
	const parts: string[] = [];
	for (const [key, value] of Object.entries(params)) {
		if (value === undefined || value === null || value === '') continue;
		parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
	}
	return parts.length ? `?${parts.join('&')}` : '';
}

export const placesApi = {
	list(filters: PlaceFilters = {}): Promise<Paginated<Place>> {
		return apiFetch<Paginated<Place>>(`/places/${buildQuery(filters as Record<string, unknown>)}`, {
			auth: false
		});
	},
	detail(id: number | string): Promise<PlaceDetail> {
		return apiFetch<PlaceDetail>(`/places/place/${id}/`, { auth: false });
	},
	create(payload: FormData | Record<string, unknown>): Promise<Place> {
		const isFormData = typeof FormData !== 'undefined' && payload instanceof FormData;
		return apiFetch<Place>('/places/create-place/', {
			method: 'POST',
			body: payload,
			rawBody: isFormData
		});
	},
	moderationList(): Promise<Paginated<Place>> {
		return apiFetch<Paginated<Place>>('/places/moderation/');
	},
	approve(id: number, reason = ''): Promise<Place> {
		return apiFetch<Place>(`/places/${id}/approve/`, { method: 'PATCH', body: { reason } });
	},
	reject(id: number, reason = ''): Promise<Place> {
		return apiFetch<Place>(`/places/${id}/reject/`, { method: 'PATCH', body: { reason } });
	},
	rate(id: number, stars: number): Promise<unknown> {
		return apiFetch(`/places/${id}/rate/`, { method: 'POST', body: { rating: stars } });
	}
};

export const menuApi = {
	list(placeId: number | string): Promise<Paginated<MenuItem>> {
		return apiFetch<Paginated<MenuItem>>(`/places/${placeId}/menu/`, { auth: false });
	},
	create(placeId: number, payload: Partial<MenuItem>): Promise<MenuItem> {
		return apiFetch<MenuItem>(`/places/${placeId}/menu/`, {
			method: 'POST',
			body: payload
		});
	},
	update(placeId: number, itemId: number, payload: Partial<MenuItem>): Promise<MenuItem> {
		return apiFetch<MenuItem>(`/places/${placeId}/menu/${itemId}/`, {
			method: 'PATCH',
			body: payload
		});
	},
	remove(placeId: number, itemId: number): Promise<void> {
		return apiFetch(`/places/${placeId}/menu/${itemId}/`, { method: 'DELETE' });
	}
};

export const reviewsApi = {
	listForPlace(placeId: number | string): Promise<Paginated<Review>> {
		return apiFetch<Paginated<Review>>(`/places/${placeId}/reviews/`, { auth: false });
	},
	create(placeId: number, payload: { score: string | number; comment?: string }): Promise<Review> {
		return apiFetch<Review>(`/places/${placeId}/reviews/`, {
			method: 'POST',
			body: payload
		});
	},
	moderationList(): Promise<Paginated<Review>> {
		return apiFetch<Paginated<Review>>('/reviews/moderation/');
	},
	approve(id: number): Promise<Review> {
		return apiFetch<Review>(`/reviews/${id}/approve/`, { method: 'PATCH' });
	},
	reject(id: number): Promise<Review> {
		return apiFetch<Review>(`/reviews/${id}/reject/`, { method: 'PATCH' });
	}
};

export const articlesApi = {
	list(filters: { category?: string; search?: string; ordering?: string } = {}): Promise<
		Paginated<Article>
	> {
		return apiFetch<Paginated<Article>>(
			`/articles/${buildQuery(filters as Record<string, unknown>)}`,
			{ auth: false }
		);
	},
	detail(slug: string): Promise<Article> {
		return apiFetch<Article>(`/articles/${slug}/`, { auth: false });
	},
	create(payload: Partial<Article>): Promise<Article> {
		return apiFetch<Article>('/articles/', { method: 'POST', body: payload });
	}
};
