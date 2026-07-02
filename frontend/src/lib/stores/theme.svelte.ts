import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

const STORAGE_KEY = 'shava-theme';

function initialTheme(): Theme {
	if (!browser) return 'light';
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored === 'light' || stored === 'dark') return stored;
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function apply(theme: Theme) {
	if (!browser) return;
	document.documentElement.classList.toggle('dark', theme === 'dark');
	const meta = document.querySelector('meta[name="theme-color"]');
	meta?.setAttribute('content', theme === 'dark' ? '#1c1917' : '#d97706');
}

class ThemeStore {
	current = $state<Theme>(initialTheme());

	constructor() {
		apply(this.current);
	}

	toggle() {
		this.current = this.current === 'dark' ? 'light' : 'dark';
		if (browser) localStorage.setItem(STORAGE_KEY, this.current);
		apply(this.current);
	}
}

export const themeStore = new ThemeStore();
