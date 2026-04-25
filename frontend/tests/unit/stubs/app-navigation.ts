// Test stub for SvelteKit's `$app/navigation` virtual module.
// Tests that need to assert navigation can spy on these via `vi.spyOn`.
export const goto = async (_url: string): Promise<void> => {};
export const invalidate = async (): Promise<void> => {};
export const invalidateAll = async (): Promise<void> => {};
export const preloadCode = async (): Promise<void> => {};
export const preloadData = async (): Promise<void> => {};
export const beforeNavigate = (): void => {};
export const afterNavigate = (): void => {};
export const disableScrollHandling = (): void => {};
export const pushState = (): void => {};
export const replaceState = (): void => {};
