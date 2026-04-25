import { browser } from '$app/environment';
import { ApiError, type FieldErrors } from '$lib/types/auth';

const ACCESS_KEY = 'shava.access';
const REFRESH_KEY = 'shava.refresh';

export const API_BASE: string =
	(browser
		? (window as unknown as { __API_BASE?: string }).__API_BASE
		: undefined) || (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE_URL || '/api';

export const tokenStorage = {
	getAccess(): string | null {
		if (!browser) return null;
		return localStorage.getItem(ACCESS_KEY);
	},
	getRefresh(): string | null {
		if (!browser) return null;
		return localStorage.getItem(REFRESH_KEY);
	},
	set(access: string, refresh: string) {
		if (!browser) return;
		localStorage.setItem(ACCESS_KEY, access);
		localStorage.setItem(REFRESH_KEY, refresh);
	},
	clear() {
		if (!browser) return;
		localStorage.removeItem(ACCESS_KEY);
		localStorage.removeItem(REFRESH_KEY);
	}
};

interface RequestOptions extends Omit<RequestInit, 'body'> {
	body?: unknown;
	auth?: boolean;
	rawBody?: boolean;
}

async function refreshAccessToken(): Promise<string | null> {
	const refresh = tokenStorage.getRefresh();
	if (!refresh) return null;
	try {
		const resp = await fetch(`${API_BASE}/token/refresh/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ refresh })
		});
		if (!resp.ok) return null;
		const data = (await resp.json()) as { access: string; refresh?: string };
		const newRefresh = data.refresh ?? refresh;
		tokenStorage.set(data.access, newRefresh);
		return data.access;
	} catch {
		return null;
	}
}

async function buildHeaders(options: RequestOptions): Promise<Headers> {
	const headers = new Headers(options.headers ?? {});
	if (!options.rawBody && !headers.has('Content-Type')) {
		headers.set('Content-Type', 'application/json');
	}
	if (options.auth !== false) {
		const access = tokenStorage.getAccess();
		if (access) headers.set('Authorization', `Bearer ${access}`);
	}
	return headers;
}

function serializeBody(options: RequestOptions): BodyInit | undefined {
	if (options.body === undefined || options.body === null) return undefined;
	if (options.rawBody) return options.body as BodyInit;
	return JSON.stringify(options.body);
}

async function parseError(resp: Response): Promise<ApiError> {
	let message = `Request failed (${resp.status})`;
	let fieldErrors: FieldErrors = {};
	try {
		const data = await resp.json();
		if (data?.detail) message = data.detail;
		if (data && typeof data === 'object' && !Array.isArray(data)) {
			const known = new Set(['detail', 'code', 'message']);
			for (const k of Object.keys(data)) {
				if (!known.has(k)) fieldErrors[k] = data[k];
			}
		}
	} catch {
		// ignore body parse failures
	}
	return new ApiError(message, resp.status, fieldErrors);
}

export async function apiFetch<T = unknown>(path: string, options: RequestOptions = {}): Promise<T> {
	const url = path.startsWith('http') ? path : `${API_BASE}${path}`;

	const send = async (): Promise<Response> => {
		return fetch(url, {
			...options,
			headers: await buildHeaders(options),
			body: serializeBody(options)
		});
	};

	let response = await send();

	if (response.status === 401 && options.auth !== false) {
		const newAccess = await refreshAccessToken();
		if (newAccess) {
			response = await send();
		}
	}

	if (!response.ok) {
		throw await parseError(response);
	}

	if (response.status === 204) return undefined as T;
	const contentType = response.headers.get('content-type') ?? '';
	if (contentType.includes('application/json')) return (await response.json()) as T;
	return (await response.text()) as unknown as T;
}
