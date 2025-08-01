type DynamicRoutes = {
	
};

type Layouts = {
	"/": undefined;
	"/about": undefined;
	"/contact": undefined
};

export type RouteId = "/" | "/about" | "/contact";

export type RouteParams<T extends RouteId> = T extends keyof DynamicRoutes ? DynamicRoutes[T] : Record<string, never>;

export type LayoutParams<T extends RouteId> = Layouts[T] | Record<string, never>;

export type Pathname = "/" | "/about" | "/contact";

export type ResolvedPathname = `${"" | `/${string}`}${Pathname}`;

export type Asset = "/file.svg" | "/globe.svg" | "/next.svg" | "/robots.txt" | "/svelte.svg" | "/vercel.svg" | "/window.svg";