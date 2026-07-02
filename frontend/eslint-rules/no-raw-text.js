/**
 * Local equivalent of a `svelte/no-raw-text` rule: forbids hard-coded,
 * user-visible strings in Svelte templates so all UI copy goes through
 * Paraglide messages (`m.*`).
 *
 * Flags:
 *  - text nodes containing letters (`SvelteText`)
 *  - string literals in user-facing attributes (placeholder, title, alt,
 *    aria-label, label)
 *
 * Symbols, emoji, and punctuation-only text (·, ×, →, ★, ₴, 🌯 …) are allowed.
 */
const HAS_LETTERS = /\p{L}/u;
const USER_FACING_ATTRS = new Set(['placeholder', 'title', 'alt', 'aria-label', 'label']);

export default {
	meta: {
		type: 'suggestion',
		docs: {
			description: 'disallow hard-coded UI text; use Paraglide messages instead'
		},
		schema: [],
		messages: {
			rawText: 'Hard-coded UI text {{text}} — use a Paraglide message (m.*) instead.'
		}
	},
	create(context) {
		return {
			SvelteText(node) {
				const text = node.value.trim();
				if (HAS_LETTERS.test(text)) {
					context.report({ node, messageId: 'rawText', data: { text: JSON.stringify(text) } });
				}
			},
			SvelteLiteral(node) {
				const attr = node.parent;
				if (attr?.type !== 'SvelteAttribute') return;
				const name = attr.key?.name;
				if (!USER_FACING_ATTRS.has(name)) return;
				if (HAS_LETTERS.test(node.value)) {
					context.report({
						node,
						messageId: 'rawText',
						data: { text: JSON.stringify(node.value) }
					});
				}
			}
		};
	}
};
