// Test stub for SvelteKit's `$app/environment` virtual module.
// `browser` is mutable so individual tests can flip it.
export let browser = true;
export const dev = true;
export const building = false;
export const version = 'test';

export function __setBrowser(value: boolean): void {
	browser = value;
}
