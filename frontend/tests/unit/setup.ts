import { beforeEach, vi } from 'vitest';

// Reset DOM-side state and any global stubs between tests so the suite
// stays deterministic regardless of order.
beforeEach(() => {
	if (typeof localStorage !== 'undefined') {
		localStorage.clear();
	}
	vi.unstubAllGlobals();
	vi.restoreAllMocks();
});
