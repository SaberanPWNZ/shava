import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
const replacements = {
  translate: /* @__PURE__ */ new Map([
    [true, "yes"],
    [false, "no"]
  ])
};
function attr(name, value, is_boolean = false) {
  if (is_boolean) return "";
  const normalized = name in replacements && replacements[name].get(value) || value;
  const assignment = is_boolean ? "" : `="${escape_html(normalized, true)}"`;
  return ` ${name}${assignment}`;
}
function _page($$payload) {
  let name = "";
  let email = "";
  let message = "";
  $$payload.out.push(`<div class="font-sans min-h-screen p-8 pb-20 gap-16 sm:p-20"><main class="max-w-4xl mx-auto"><nav class="mb-8"><a href="/" class="text-blue-600 hover:text-blue-800 hover:underline mr-4">← Back to Home</a></nav> <h1 class="text-4xl font-bold mb-6 text-gray-900 dark:text-white">Contact Us</h1> <div class="grid md:grid-cols-2 gap-8"><div><h2 class="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">Get in Touch</h2> <p class="text-gray-700 dark:text-gray-300 mb-6">We'd love to hear from you. Send us a message and we'll respond as soon as possible.</p> <div class="space-y-4"><div class="flex items-center"><div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mr-3"><span class="text-blue-600 dark:text-blue-400">📧</span></div> <span class="text-gray-700 dark:text-gray-300">contact@shava.dev</span></div> <div class="flex items-center"><div class="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mr-3"><span class="text-green-600 dark:text-green-400">📱</span></div> <span class="text-gray-700 dark:text-gray-300">+1 (555) 123-4567</span></div> <div class="flex items-center"><div class="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mr-3"><span class="text-purple-600 dark:text-purple-400">📍</span></div> <span class="text-gray-700 dark:text-gray-300">San Francisco, CA</span></div></div></div> <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg"><form class="space-y-4"><div><label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label> <input id="name" type="text"${attr("value", name)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="Your name"/></div> <div><label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label> <input id="email" type="email"${attr("value", email)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="your@email.com"/></div> <div><label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message</label> <textarea id="message" rows="4" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="Your message here...">`);
  const $$body = escape_html(message);
  if ($$body) {
    $$payload.out.push(`${$$body}`);
  }
  $$payload.out.push(`</textarea></div> <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors">Send Message</button></form></div></div> <div class="mt-8 flex gap-4"><a href="/about" class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors">About Us</a> <a href="/" class="border border-gray-300 hover:border-gray-400 text-gray-700 dark:text-gray-300 px-6 py-2 rounded-lg transition-colors">Go Home</a></div></main></div>`);
}
export {
  _page as default
};
