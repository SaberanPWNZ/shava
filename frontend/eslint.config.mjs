import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("eslint:recommended"),
  {
    files: ["**/*.svelte"],
    plugins: {
      svelte: import("eslint-plugin-svelte"),
    },
    languageOptions: {
      parser: import("svelte-eslint-parser"),
      parserOptions: {
        parser: {
          ts: import("@typescript-eslint/parser"),
          js: import("espree"),
        },
      },
    },
    rules: {
      // Svelte rules go here
    },
  },
];

export default eslintConfig;
