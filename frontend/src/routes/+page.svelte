<div class="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
	<main class="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
		<div class="text-center sm:text-left">
			<h1 class="text-4xl font-bold mb-4 text-gray-900 dark:text-white">
				Welcome to Shava
			</h1>
			<p class="text-lg text-gray-700 dark:text-gray-300 mb-8">
				A modern SvelteKit application with Tailwind CSS and routing
			</p>
		</div>

		<img 
			class="dark:invert" 
			src="/svelte.svg" 
			alt="Svelte logo" 
			width="180" 
			height="38" 
		/>

		<div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900 dark:to-purple-900 p-6 rounded-lg max-w-md">
			<h2 class="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
				🚀 Project Features
			</h2>
			<ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
				<li>✅ SvelteKit with file-based routing</li>
				<li>✅ Tailwind CSS for styling</li>
				<li>✅ TypeScript support</li>
				<li>✅ Responsive design</li>
				<li>✅ Modern web framework</li>
			</ul>
		</div>

		<nav class="flex gap-4 items-center flex-col sm:flex-row">
			<a
				href="/about"
				class="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 text-white gap-2 hover:bg-blue-700 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
			>
				About Us
			</a>
			<a
				href="/contact"
				class="rounded-full border border-solid border-blue-600 transition-colors flex items-center justify-center hover:bg-blue-50 dark:hover:bg-blue-900 text-blue-600 dark:text-blue-400 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto"
			>
				Contact Us
			</a>
		</nav>

		<div class="flex gap-4 items-center flex-col sm:flex-row">
			<a
				class="rounded-full border border-solid border-gray-300 dark:border-gray-600 transition-colors flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-800 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 text-gray-700 dark:text-gray-300"
				href="https://svelte.dev/docs/kit"
				target="_blank"
				rel="noopener noreferrer"
			>
				📚 SvelteKit Docs
			</a>
			<a
				class="rounded-full border border-solid border-gray-300 dark:border-gray-600 transition-colors flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-800 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 text-gray-700 dark:text-gray-300"
				href="https://tailwindcss.com/docs"
				target="_blank"
				rel="noopener noreferrer"
			>
				🎨 Tailwind Docs
			</a>
		</div>
	</main>
	<footer class="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
		<a
			class="flex items-center gap-2 hover:underline hover:underline-offset-4"
			href="https://svelte.dev/tutorial"
			target="_blank"
			rel="noopener noreferrer"
		>
			<img
				aria-hidden="true"
				src="/file.svg"
				alt="File icon"
				width="16"
				height="16"
			/>
			Learn
		</a>
		<a
			class="flex items-center gap-2 hover:underline hover:underline-offset-4"
			href="https://svelte.dev/examples"
			target="_blank"
			rel="noopener noreferrer"
		>
			<img
				aria-hidden="true"
				src="/window.svg"
				alt="Window icon"
				width="16"
				height="16"
			/>
			Examples
		</a>
		<a
			class="flex items-center gap-2 hover:underline hover:underline-offset-4"
			href="https://svelte.dev"
			target="_blank"
			rel="noopener noreferrer"
		>
			<img
				aria-hidden="true"
				src="/globe.svg"
				alt="Globe icon"
				width="16"
				height="16"
			/>
			Go to svelte.dev →
		</a>
	</footer>
</div>
