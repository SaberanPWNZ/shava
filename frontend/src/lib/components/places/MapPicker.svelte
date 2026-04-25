<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import 'leaflet/dist/leaflet.css';

	type LatLng = { lat: number; lng: number };

	let {
		value = $bindable<LatLng | null>(null),
		center = { lat: 50.4501, lng: 30.5234 },
		zoom = 12
	} = $props<{
		value?: LatLng | null;
		center?: LatLng;
		zoom?: number;
	}>();

	let containerEl: HTMLDivElement;
	let map: import('leaflet').Map | null = null;
	let marker: import('leaflet').Marker | null = null;

	onMount(async () => {
		const L = (await import('leaflet')).default;

		// Default Leaflet marker icons rely on assets bundled by Webpack/Vite,
		// which the runtime can't locate. Use a CDN fallback so the marker
		// always renders correctly without extra build configuration.
		const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
		const iconRetinaUrl =
			'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png';
		const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';
		const DefaultIcon = L.icon({
			iconUrl,
			iconRetinaUrl,
			shadowUrl,
			iconSize: [25, 41],
			iconAnchor: [12, 41],
			popupAnchor: [1, -34],
			shadowSize: [41, 41]
		});

		const initial = value ?? center;
		map = L.map(containerEl).setView([initial.lat, initial.lng], zoom);

		L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 19
		}).addTo(map);

		marker = L.marker([initial.lat, initial.lng], {
			draggable: true,
			icon: DefaultIcon
		}).addTo(map);

		marker.on('dragend', () => {
			if (!marker) return;
			const ll = marker.getLatLng();
			value = { lat: ll.lat, lng: ll.lng };
		});

		map.on('click', (event: import('leaflet').LeafletMouseEvent) => {
			if (!marker) return;
			marker.setLatLng(event.latlng);
			value = { lat: event.latlng.lat, lng: event.latlng.lng };
		});

		// If we don't yet have a value, default to the centre to expose
		// coordinates immediately.
		if (!value) {
			value = { lat: initial.lat, lng: initial.lng };
		}
	});

	$effect(() => {
		if (!map || !marker || !value) return;
		const current = marker.getLatLng();
		if (current.lat !== value.lat || current.lng !== value.lng) {
			marker.setLatLng([value.lat, value.lng]);
		}
	});

	onDestroy(() => {
		if (map) {
			map.remove();
			map = null;
			marker = null;
		}
	});
</script>

<div
	bind:this={containerEl}
	class="h-72 w-full overflow-hidden rounded-lg border border-zinc-300 dark:border-zinc-700"
	role="application"
	aria-label="Map: drag the marker or click to choose a location"
></div>
