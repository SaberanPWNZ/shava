/**
 * Re-exports from the auto-generated OpenAPI types.
 *
 * Always import schema-derived types from this barrel — never reach into
 * ``types.gen.ts`` directly. That keeps the generated file an
 * implementation detail and makes it trivial to swap the generator in
 * the future without touching every call site.
 *
 * Regenerate with:
 *
 * ```bash
 * # From backend/ (no running server needed):
 * DJANGO_SECRET_KEY=test python manage.py spectacular --file openapi-schema.yaml
 *
 * # From frontend/:
 * npm run generate:api:offline
 * ```
 */
import type { paths, components, operations } from './types.gen';

export type { paths, components, operations };

/** Convenience alias for ``components["schemas"]`` — the named DTOs. */
export type Schemas = components['schemas'];
