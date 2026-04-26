// Ambient module declarations for vite-plugin-pwa virtual modules.
// Kept as a script (no top-level imports/exports) so the `declare module`
// blocks register globally without needing explicit imports.

declare module 'virtual:pwa-register' {
	export interface RegisterSWOptions {
		immediate?: boolean;
		onNeedRefresh?: () => void;
		onOfflineReady?: () => void;
		onRegistered?: (registration: ServiceWorkerRegistration | undefined) => void;
		onRegisterError?: (error: unknown) => void;
	}

	export function registerSW(
		options?: RegisterSWOptions
	): (reloadPage?: boolean) => Promise<void>;
}
