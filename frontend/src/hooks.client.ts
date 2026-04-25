/**
 * Client-side Sentry initialisation.
 *
 * Activates only when the runtime exposes ``PUBLIC_SENTRY_DSN`` — local
 * development and CI keep it unset, so the SDK is a complete no-op there
 * (no network calls, no global error-handler hooks beyond what SvelteKit
 * already installs).
 */
import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/public';
import { handleErrorWithSentry } from '@sentry/sveltekit';
import type { HandleClientError } from '@sveltejs/kit';

const dsn = env.PUBLIC_SENTRY_DSN;

if (dsn) {
	Sentry.init({
		dsn,
		environment: env.PUBLIC_SENTRY_ENVIRONMENT || 'production',
		release: env.PUBLIC_GIT_SHA || undefined,
		// Performance / replay tracing — opt-in via env, off by default so
		// we don't burn through a free Sentry tier on day one.
		tracesSampleRate: Number(env.PUBLIC_SENTRY_TRACES_SAMPLE_RATE ?? '0') || 0,
		// Privacy: never attach IP / cookies / request bodies by default.
		sendDefaultPii: false
	});
}

// SvelteKit's ``handleError`` hook — wrapped so unhandled client errors
// are captured automatically. The wrapper is a no-op when the SDK isn't
// initialised, so it's safe to export unconditionally.
export const handleError: HandleClientError = handleErrorWithSentry();
