import { w as head } from "../../chunks/index.js";
function _layout($$payload, $$props) {
  let { children } = $$props;
  head($$payload, ($$payload2) => {
    $$payload2.title = `<title>Shava - SvelteKit App</title>`;
    $$payload2.out.push(`<meta name="description" content="A modern SvelteKit application with Tailwind CSS and routing"/>`);
  });
  $$payload.out.push(`<div class="antialiased">`);
  children?.($$payload);
  $$payload.out.push(`<!----></div>`);
}
export {
  _layout as default
};
