<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<div class="text-2xl font-bold text-orange-600">🌯 ShaurmaRadar</div>
				</div>
				<nav class="hidden md:flex space-x-8">
					<a href="/places" class="text-gray-700 hover:text-orange-600 transition-colors">Places Rating</a>
					<a href="/users" class="text-gray-700 hover:text-orange-600 transition-colors">TOP Users</a>
					<a href="/news" class="text-gray-700 hover:text-orange-600 transition-colors">News</a>
					<a href="/map" class="text-gray-700 hover:text-orange-600 transition-colors">Map</a>
					<a href="/about" class="text-gray-700 hover:text-orange-600 transition-colors">About</a>
				</nav>
				<button class="md:hidden p-2" aria-label="Open menu">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
					</svg>
				</button>
			</div>
		</div>
	</header>

	<!-- Banner Section -->
	<section class="bg-gradient-to-r from-orange-500 to-red-500 text-white py-20">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<h1 class="text-4xl md:text-6xl font-bold mb-6">Find the Best Shawarma Near You</h1>
			<p class="text-xl md:text-2xl mb-8 opacity-90">Discover, rate, and share amazing shawarma places with our community</p>
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<button class="bg-white text-orange-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
					Explore Places
				</button>
				<button class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-orange-600 transition-colors">
					View Map
				</button>
			</div>
		</div>
	</section>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		
		<!-- Best Places Section -->
		<section class="mb-16">
			<h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">🏆 Best Places This Month</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each Array(6) as _, i}
				<div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
					<div class="h-48 bg-gradient-to-br from-orange-400 to-red-400"></div>
					<div class="p-6">
						<h3 class="text-xl font-semibold mb-2">Shawarma Paradise {i + 1}</h3>
						<p class="text-gray-600 mb-3">Delicious authentic Middle Eastern cuisine</p>
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<span class="text-yellow-500">★★★★★</span>
								<span class="text-gray-600 ml-2">4.{9-i}</span>
							</div>
							<span class="text-sm text-gray-500">{150 + i * 20} reviews</span>
						</div>
						<div class="mt-4">
							<span class="text-sm text-gray-500">📍 Downtown Area</span>
						</div>
					</div>
				</div>
				{/each}
			</div>
		</section>

		<!-- TOP Users Section -->
		<section class="mb-16">
			<h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">👑 TOP Reviewers</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				{#each Array(4) as _, i}
				<div class="bg-white rounded-lg shadow-md p-6 text-center hover:shadow-lg transition-shadow">
					<div class="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white font-bold text-xl">
						{String.fromCharCode(65 + i)}
					</div>
					<h3 class="font-semibold text-lg mb-2">User{i + 1}23</h3>
					<p class="text-gray-600 text-sm mb-3">{50 - i * 5} reviews</p>
					<div class="flex justify-center items-center">
						<span class="text-yellow-500">★</span>
						<span class="text-gray-600 ml-1">4.{8-i} avg</span>
					</div>
				</div>
				{/each}
			</div>
		</section>

		<!-- News Section -->
		<section class="mb-16">
			<h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">📰 Latest News</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each Array(3) as _, i}
				<article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
					<div class="h-40 bg-gradient-to-br from-green-400 to-blue-500"></div>
					<div class="p-6">
						<h3 class="text-xl font-semibold mb-2">New Shawarma Spot Opens Downtown</h3>
						<p class="text-gray-600 mb-4">A new authentic Middle Eastern restaurant has opened its doors, promising the best shawarma in the city...</p>
						<div class="flex items-center justify-between text-sm text-gray-500">
							<span>2 days ago</span>
							<span>Read more →</span>
						</div>
					</div>
				</article>
				{/each}
			</div>
		</section>

		<!-- Map Preview Section -->
		<section class="mb-16">
			<h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">🗺️ Interactive Map</h2>
			<div class="bg-white rounded-lg shadow-md overflow-hidden">
				<div class="h-96 bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center">
					<div class="text-center">
						<div class="text-4xl mb-4">🗺️</div>
						<p class="text-gray-600 text-lg">Interactive Google Map</p>
						<p class="text-gray-500">Click to explore shawarma locations</p>
						<button class="mt-4 bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition-colors">
							View Full Map
						</button>
					</div>
				</div>
			</div>
		</section>

		<!-- About Preview -->
		<section class="text-center bg-white rounded-lg shadow-md p-12">
			<h2 class="text-3xl font-bold text-gray-900 mb-4">About ShaurmaRadar</h2>
			<p class="text-gray-600 text-lg max-w-3xl mx-auto">
				ShaurmaRadar is your ultimate guide to finding the best shawarma places in your city. 
				Join our community of food lovers, share reviews, and discover hidden gems that serve 
				the most delicious Middle Eastern cuisine.
			</p>
			<button class="mt-6 bg-orange-600 text-white px-8 py-3 rounded-lg hover:bg-orange-700 transition-colors">
				Learn More
			</button>
		</section>

	</main>

	<!-- Footer -->
	<footer class="bg-gray-800 text-white py-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<div class="text-2xl font-bold text-orange-400 mb-4">🌯 ShaurmaRadar</div>
			<p class="text-gray-400 mb-6">Connecting food lovers with the best shawarma experiences</p>
			<div class="text-gray-500">
				© 2024 ShaurmaRadar. All rights reserved.
			</div>
		</div>
	</footer>
</div>
