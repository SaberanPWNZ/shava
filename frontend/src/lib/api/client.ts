import { browser } from '$app/environment';
import { ApiError, type FieldErrors } from '$lib/types/auth';

// Re-export schema-derived types from a single place so callers can import
// strongly-typed DTOs as ``import { type Schemas } from '$lib/api/client'``.
// This also ensures ``types.gen.ts`` is part of the import graph (so it is
// emitted by the bundler and kept in sync via ``npm run generate:api*``).
export type { paths, components, operations, Schemas } from './schema';

// Tokens live in HttpOnly cookies set by the backend — JavaScript never
// sees or stores them. ``sessionFlags`` only remembers *whether* a session
// likely exists, so anonymous page loads can skip the /me round-trip.
const HAS_SESSION_KEY = 'shava.hasSession';
// Legacy localStorage token keys from the pre-cookie era — always purge.
const LEGACY_KEYS = ['shava.access', 'shava.refresh'];

function resolveApiBase(): string {
	const env = (import.meta as unknown as { env?: Record<string, string> }).env;
	const fromEnv = env?.VITE_API_BASE_URL;
	if (fromEnv) return fromEnv;
	if (browser) {
		const fromWindow = (window as unknown as { __API_BASE?: string }).__API_BASE;
		if (fromWindow) return fromWindow;
	}
	// Versioned prefix — see ROADMAP 3.2. The legacy unversioned ``/api``
	// mount is still served by Django for one release window with a
	// ``Deprecation`` header but new clients target ``/api/v1`` directly.
	return '/api/v1';
}

export const API_BASE: string = resolveApiBase();

export const sessionFlags = {
	hasSession(): boolean {
		if (!browser) return false;
		return localStorage.getItem(HAS_SESSION_KEY) === '1';
	},
	markSession() {
		if (!browser) return;
		localStorage.setItem(HAS_SESSION_KEY, '1');
	},
	clear() {
		if (!browser) return;
		localStorage.removeItem(HAS_SESSION_KEY);
	}
};

if (browser) {
	for (const key of LEGACY_KEYS) localStorage.removeItem(key);
}

interface RequestOptions extends Omit<RequestInit, 'body'> {
	body?: unknown;
	auth?: boolean;
	rawBody?: boolean;
}

async function refreshSession(): Promise<boolean> {
	try {
		// The refresh token travels in an HttpOnly cookie; the backend rotates
		// the pair and re-sets both cookies on success.
		const resp = await fetch(`${API_BASE}/token/refresh/`, {
			method: 'POST',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' },
			body: '{}'
		});
		return resp.ok;
	} catch {
		return false;
	}
}

function buildHeaders(options: RequestOptions): Headers {
	const headers = new Headers(options.headers ?? {});
	if (!options.rawBody && !headers.has('Content-Type')) {
		headers.set('Content-Type', 'application/json');
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
	const fieldErrors: FieldErrors = {};
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

export async function apiFetch<T = unknown>(
	path: string,
	options: RequestOptions = {}
): Promise<T> {
	const url = path.startsWith('http') ? path : `${API_BASE}${path}`;

	const send = async (): Promise<Response> => {
		return fetch(url, {
			...options,
			credentials: 'include',
			headers: buildHeaders(options),
			body: serializeBody(options)
		});
	};

	let response = await send();

	if (response.status === 401 && options.auth !== false) {
		if (await refreshSession()) {
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
