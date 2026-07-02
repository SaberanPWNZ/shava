<script lang="ts">
	import RegisterForm from '$lib/components/forms/RegisterForm.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { m } from '$lib/paraglide/messages';
</script>

<Seo title={m.register_seo_title()} description={m.register_seo_description()} />

<div class="grid min-h-[70vh] items-center gap-10 lg:grid-cols-2">
	<div
		class="hidden h-full flex-col justify-between rounded-3xl bg-gradient-to-br from-amber-500 via-orange-500 to-orange-700 p-10 text-white lg:flex"
	>
		<p class="text-lg font-semibold">{m.app_name()}</p>
		<div class="space-y-4">
			<p class="text-4xl leading-tight font-extrabold tracking-tight">
				{m.register_brand_title()}
			</p>
			<ul class="space-y-3 text-lg text-amber-100">
				<li class="flex items-center gap-3">
					<span aria-hidden="true">⭐</span>
					{m.register_perk_rate()}
				</li>
				<li class="flex items-center gap-3">
					<span aria-hidden="true">🏆</span>
					{m.register_perk_points()}
				</li>
				<li class="flex items-center gap-3">
					<span aria-hidden="true">📍</span>
					{m.register_perk_spots()}
				</li>
			</ul>
		</div>
		<p class="text-sm text-amber-100/80">🌯 {m.register_brand_footer()}</p>
	</div>

	<div class="mx-auto w-full max-w-md">
		<h1 class="text-3xl font-bold tracking-tight text-stone-900 dark:text-stone-50">
			{m.register_title()}
		</h1>
		<p class="mt-1 text-sm text-stone-500 dark:text-stone-400">
			{m.register_subtitle()}
		</p>
		<div class="mt-8">
			<RegisterForm />
		</div>
		<p class="mt-6 text-center text-sm text-stone-600 dark:text-stone-400">
			{m.register_have_account()}
			<a href="/login" class="font-semibold text-amber-700 hover:underline dark:text-amber-400">
				{m.login_submit()}
			</a>
		</p>
	</div>
</div>
