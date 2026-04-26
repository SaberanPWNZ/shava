<script lang="ts">
	import Card from '$lib/components/ui/Card.svelte';
	import RegisterForm from '$lib/components/forms/RegisterForm.svelte';
</script>

<div class="mx-auto max-w-md py-12">
	<Card title="Create your account">
		<RegisterForm />
		<p class="mt-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
			Already a member?
			<a href="/login" class="font-medium text-orange-700 hover:underline">Sign in</a>
		</p>
	</Card>
</div>
