<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from './lib/Counter.svelte'
</script>

<main class="main-container">
  <div class="content-wrapper">
    <p class="description">This is a simple setup with custom CSS.</p>
  </div>
</main>

<style>
  .main-container {
    max-width: 80rem;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }

  .content-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .description {
    font-size: 1.125rem;
    margin-bottom: 2rem;
    color: #eab308;
  }
</style>
