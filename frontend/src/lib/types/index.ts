export interface ImageThumbnails {
	src: string;
	srcset: string | null;
	sizes: { xs?: string; sm?: string; md?: string; lg?: string };
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
	additional_images?: string | null;
	created_at: string;
	updated_at: string;
	website?: string | null;
	opening_hours?: string | null;
	is_featured: boolean;
	author?: number | null;
	moderated_by?: number | null;
	moderation_reason?: string | null;
	moderated_at?: string | null;
	google_maps_url?: string | null;
	average_rating?: string;
	reviews_count: number;
}

export interface PlaceDetail extends Place {
	ratings: PlaceRating[];
	menu: MenuItem[];
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
	created_at: string;
	is_moderated: boolean;
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

export interface Paginated<T> {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
}
