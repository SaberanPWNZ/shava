<script lang="ts">
	type Variant = 'success' | 'error' | 'info' | 'warning';
	let { variant = 'info' as Variant, children } = $props<{
		variant?: Variant;
		children: import('svelte').Snippet;
	}>();

	const styles: Record<Variant, string> = {
		success:
			'border-green-200 bg-green-50 text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200',
		error: 'border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200',
		info: 'border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-200',
		warning:
			'border-yellow-200 bg-yellow-50 text-yellow-800 dark:border-yellow-900 dark:bg-yellow-950 dark:text-yellow-200'
	};
</script>

<div class="mb-3 rounded-lg border px-4 py-3 text-sm {styles[variant as Variant]}">
	{@render children()}
</div>
