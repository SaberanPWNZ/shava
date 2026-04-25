import { describe, expect, it, vi } from 'vitest';
import { tokenStorage, apiFetch } from '$lib/api/client';
import { ApiError } from '$lib/types/auth';

describe('tokenStorage', () => {
	it('starts empty', () => {
		expect(tokenStorage.getAccess()).toBeNull();
		expect(tokenStorage.getRefresh()).toBeNull();
	});

	it('persists access + refresh tokens', () => {
		tokenStorage.set('a-token', 'r-token');
		expect(tokenStorage.getAccess()).toBe('a-token');
		expect(tokenStorage.getRefresh()).toBe('r-token');
	});

	it('clear() removes both tokens', () => {
		tokenStorage.set('a', 'r');
		tokenStorage.clear();
		expect(tokenStorage.getAccess()).toBeNull();
		expect(tokenStorage.getRefresh()).toBeNull();
	});
});

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('apiFetch', () => {
	it('sends Authorization header when an access token is stored', async () => {
		tokenStorage.set('the-access', 'the-refresh');
		const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(200, { ok: true }));
		vi.stubGlobal('fetch', fetchMock);

		await apiFetch('/me/');

		expect(fetchMock).toHaveBeenCalledOnce();
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		const headers = init.headers as Headers;
		expect(headers.get('Authorization')).toBe('Bearer the-access');
		expect(headers.get('Content-Type')).toBe('application/json');
	});

	it('omits Authorization when auth: false', async () => {
		tokenStorage.set('the-access', 'the-refresh');
		const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(200, {}));
		vi.stubGlobal('fetch', fetchMock);

		await apiFetch('/public/', { auth: false });

		const init = fetchMock.mock.calls[0][1] as RequestInit;
		const headers = init.headers as Headers;
		expect(headers.has('Authorization')).toBe(false);
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

	it('refreshes the access token on 401 and retries the request', async () => {
		tokenStorage.set('expired', 'good-refresh');
		const fetchMock = vi
			.fn()
			// First call: protected endpoint returns 401.
			.mockResolvedValueOnce(jsonResponse(401, { detail: 'expired' }))
			// Second call: token/refresh returns a fresh access token.
			.mockResolvedValueOnce(jsonResponse(200, { access: 'new-access', refresh: 'new-refresh' }))
			// Third call: retried original request succeeds.
			.mockResolvedValueOnce(jsonResponse(200, { id: 1 }));
		vi.stubGlobal('fetch', fetchMock);

		const data = await apiFetch<{ id: number }>('/me/');

		expect(data).toEqual({ id: 1 });
		expect(fetchMock).toHaveBeenCalledTimes(3);
		expect(tokenStorage.getAccess()).toBe('new-access');
		expect(tokenStorage.getRefresh()).toBe('new-refresh');
	});

	it('does not retry when the refresh call itself fails', async () => {
		tokenStorage.set('expired', 'bad-refresh');
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
