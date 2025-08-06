<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from './lib/Counter.svelte'
  import "tailwindcss";
</script>

<main class="max-w-5xl mx-auto p-8 text-center">
  <div class="flex justify-center items-center gap-4 mb-8">
    <a href="https://vite.dev" target="_blank" rel="noreferrer">
      <img src={viteLogo} class="logo hover:drop-shadow-[0_0_2em_#646cffaa] transition-all duration-300" alt="Vite Logo" />
    </a>
    <a href="https://svelte.dev" target="_blank" rel="noreferrer">
      <img src={svelteLogo} class="logo svelte hover:drop-shadow-[0_0_2em_#ff3e00aa] transition-all duration-300" alt="Svelte Logo" />
    </a>
  </div>
  <h1 class="text-5xl font-bold mb-8 bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">Vite + Svelte</h1>

  <div class="card bg-black-100 dark:bg-gray-800 rounded-lg p-8 mb-8 shadow-lg">
    <Counter />
  </div>

  <p class="mb-4 text-lg text-gray-700 dark:text-gray-300">
    Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer" class="text-blue-500 hover:text-blue-700 underline">SvelteKit</a>, the official Svelte app framework powered by Vite!
  </p>

  <p class="text-gray-500 text-lg">
    Click on the Vite and Svelte logos to learn more
  </p>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
  }
</style>
