/**
 * Server-side Sentry initialisation for the SvelteKit Node adapter.
 *
 * As on the client, this is a complete no-op when ``PUBLIC_SENTRY_DSN`` is
 * unset. The DSN is intentionally a *public* env var (PUBLIC_* prefix) so
 * the same value is available to client and server bundles — Sentry DSNs
 * are designed to be public.
 */
import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/public';
import { handleErrorWithSentry, sentryHandle } from '@sentry/sveltekit';
import { sequence } from '@sveltejs/kit/hooks';
import type { Handle, HandleServerError } from '@sveltejs/kit';

const dsn = env.PUBLIC_SENTRY_DSN;

if (dsn) {
	Sentry.init({
		dsn,
		environment: env.PUBLIC_SENTRY_ENVIRONMENT || 'production',
		release: env.PUBLIC_GIT_SHA || undefined,
		tracesSampleRate: Number(env.PUBLIC_SENTRY_TRACES_SAMPLE_RATE ?? '0') || 0,
		sendDefaultPii: false
	});
}

// ``sentryHandle`` is safe to install even when the SDK isn't configured —
// it just falls through to the next handler.
export const handle: Handle = sequence(sentryHandle());

export const handleError: HandleServerError = handleErrorWithSentry();
