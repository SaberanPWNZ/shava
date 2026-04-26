<script lang="ts">
	import Card from '$lib/components/ui/Card.svelte';
	import LoginForm from '$lib/components/forms/LoginForm.svelte';
</script>

<div class="mx-auto max-w-md py-12">
	<Card title="Welcome back">
		<LoginForm />
		<p class="mt-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
			Don't have an account?
			<a href="/register" class="font-medium text-orange-700 hover:underline">Create one</a>
		</p>
	</Card>
</div>
