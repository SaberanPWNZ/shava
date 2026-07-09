import { describe, expect, it, vi } from 'vitest';
import { sessionFlags, apiFetch } from '$lib/api/client';
import { ApiError } from '$lib/types/auth';

describe('sessionFlags', () => {
	it('starts without a session', () => {
		expect(sessionFlags.hasSession()).toBe(false);
	});

	it('remembers that a session was established', () => {
		sessionFlags.markSession();
		expect(sessionFlags.hasSession()).toBe(true);
	});

	it('clear() forgets the session', () => {
		sessionFlags.markSession();
		sessionFlags.clear();
		expect(sessionFlags.hasSession()).toBe(false);
	});
});

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('apiFetch', () => {
	it('sends cookies (credentials: include) and JSON content type', async () => {
		const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(200, { ok: true }));
		vi.stubGlobal('fetch', fetchMock);

		await apiFetch('/me/');

		expect(fetchMock).toHaveBeenCalledOnce();
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.credentials).toBe('include');
		const headers = init.headers as Headers;
		// Tokens live in HttpOnly cookies — never in an Authorization header.
		expect(headers.has('Authorization')).toBe(false);
		expect(headers.get('Content-Type')).toBe('application/json');
	});

	it('parses field errors into ApiError', async () => {
		const fetchMock = vi.fn(async () =>
			jsonResponse(400, { detail: 'Bad', email: ['Already taken'] })
		);
		vi.stubGlobal('fetch', fetchMock);

		await expect(apiFetch('/register/', { method: 'POST', body: {} })).rejects.toMatchObject({
			constructor: ApiError,
			status: 400,
			message: 'Bad',
			fieldErrors: { email: ['Already taken'] }
		});
	});

	it('refreshes the session on 401 and retries the request', async () => {
		const fetchMock = vi
			.fn()
			// First call: protected endpoint returns 401.
			.mockResolvedValueOnce(jsonResponse(401, { detail: 'expired' }))
			// Second call: token/refresh succeeds (cookies rotated server-side).
			.mockResolvedValueOnce(jsonResponse(200, { access: 'new-access' }))
			// Third call: retried original request succeeds.
			.mockResolvedValueOnce(jsonResponse(200, { id: 1 }));
		vi.stubGlobal('fetch', fetchMock);

		const data = await apiFetch<{ id: number }>('/me/');

		expect(data).toEqual({ id: 1 });
		expect(fetchMock).toHaveBeenCalledTimes(3);
		const refreshInit = fetchMock.mock.calls[1][1] as RequestInit;
		expect(refreshInit.credentials).toBe('include');
	});

	it('does not retry when the refresh call itself fails', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(jsonResponse(401, { detail: 'expired' }))
			.mockResolvedValueOnce(jsonResponse(401, { detail: 'invalid refresh' }));
		vi.stubGlobal('fetch', fetchMock);

		await expect(apiFetch('/me/')).rejects.toBeInstanceOf(ApiError);
		expect(fetchMock).toHaveBeenCalledTimes(2);
	});

	it('returns undefined for 204 responses', async () => {
		const fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
		vi.stubGlobal('fetch', fetchMock);

		const data = await apiFetch('/logout/', { method: 'POST', auth: false });
		expect(data).toBeUndefined();
	});
});
