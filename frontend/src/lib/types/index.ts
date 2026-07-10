export interface ImageThumbnails {
	src: string;
	srcset: string | null;
	sizes: { xs?: string; sm?: string; md?: string; lg?: string };
}

export interface City {
	id: number;
	name: string;
	slug: string;
}

export interface Place {
	id: number;
	name: string;
	city?: string;
	district: string;
	address: string;
	delivery: boolean;
	latitude?: string | null;
	longitude?: string | null;
	description?: string | null;
	status: string;
	rating: string;
	stars: number;
	ratings_count: number;
	main_image?: string | null;
	main_image_thumbnails?: ImageThumbnails | null;
	created_at: string;
	updated_at: string;
	website?: string | null;
	phone?: string;
	instagram?: string;
	opening_hours?: string | null;
	/** 1 = ₴ budget, 2 = ₴₴ mid-range, 3 = ₴₴₴ premium. */
	price_level?: 1 | 2 | 3 | null;
	is_featured: boolean;
	author?: number | null;
	moderated_by?: number | null;
	moderation_reason?: string | null;
	moderated_at?: string | null;
	google_maps_url?: string | null;
	average_rating?: string;
	reviews_count: number;
	favorites_count: number;
	/** True when the *current* user has saved this place. */
	is_favorited: boolean;
}

export interface PlaceImage {
	id: number;
	image: string;
	caption: string;
	sort_order: number;
}

export interface PlaceDetail extends Place {
	images: PlaceImage[];
	ratings: PlaceRating[];
	menu: MenuItem[];
	/** The current user's own 1–5 star rating, if they rated this place. */
	viewer_rating: number | null;
	/** Id of the current user's review of this place, if they wrote one. */
	viewer_review_id: number | null;
}

export interface PlaceRating {
	id: number;
	user: number;
	place: number;
	rating: string;
}

export interface MenuItem {
	id: number;
	place: number;
	name: string;
	description?: string | null;
	price: string;
	image?: string | null;
	category: string;
	is_available: boolean;
	item?: number | null;
	item_name?: string | null;
}

export interface Review {
	id: number;
	place: number;
	place_name?: string;
	author: number;
	author_username?: string;
	score: string;
	comment?: string | null;
	dish_image?: string | null;
	dish_image_thumbnails?: ImageThumbnails | null;
	receipt_image?: string | null;
	receipt_image_thumbnails?: ImageThumbnails | null;
	is_verified?: boolean;
	helpful_count?: number;
	/** True when the *current* user has cast a helpful vote on this review. */
	viewer_voted?: boolean;
	replies_count?: number;
	created_at: string;
	is_moderated: boolean;
}

export interface ReviewReply {
	id: number;
	review: number;
	author: number;
	author_username?: string;
	text: string;
	created_at: string;
}

export type NotificationType =
	| 'review_approved'
	| 'review_rejected'
	| 'place_approved'
	| 'place_rejected'
	| 'review_reply'
	| 'favorite_place_review'
	| 'badge_awarded';

export interface AppNotification {
	id: number;
	type: NotificationType;
	data: {
		review_id?: number;
		place_id?: number;
		place_name?: string;
		reply_author?: string;
		review_author?: string;
		text_preview?: string;
		reason?: string;
		badge_code?: string;
		badge_title?: string;
		badge_icon?: string;
	};
	is_read: boolean;
	created_at: string;
}

export interface UserPublicProfile {
	id: number;
	username?: string;
	first_name?: string;
	last_name?: string;
	bio?: string;
	city?: City | null;
	avatar?: string | null;
	avatar_thumbnails?: ImageThumbnails | null;
	member_since: string;
}

export interface Article {
	id: number;
	title: string;
	slug: string;
	excerpt?: string;
	content?: string;
	cover_image?: string | null;
	cover_image_thumbnails?: ImageThumbnails | null;
	category: string;
	author?: number | null;
	author_name?: string | null;
	published_at: string;
	is_published: boolean;
	created_at?: string;
	updated_at?: string;
}

export interface PlaceFilters {
	city?: string;
	district?: string;
	delivery?: boolean;
	is_featured?: boolean;
	min_stars?: number;
	has_menu?: boolean;
	search?: string;
	ordering?: string;
}

export type ReviewOrdering = 'newest' | 'oldest' | 'helpful' | 'top' | 'low';

export interface ReviewListParams {
	ordering?: ReviewOrdering;
	with_photos?: boolean;
	page?: number;
}

export interface Paginated<T> {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
}

export interface ModerationLogEntry {
	id: number;
	actor: number | null;
	actor_username: string;
	target_type: 'place' | 'review';
	target_id: number;
	action: 'approve' | 'reject';
	reason: string;
	created_at: string;
}
