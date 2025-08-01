# Shava Project - Frontend

This is the frontend for the Shava project, built with SvelteKit and Tailwind CSS.

## Development

```bash

npm run dev


npm run build

# Preview production build
npm run preview
```

## Docker

The project includes Docker configuration for development and production environments:

```bash
# Build and run using Docker
docker build -t shava-frontend .
docker run -p 3000:3000 shava-frontend
```

## Technologies

- SvelteKit
- Tailwind CSS
- TypeScript
- Node.js
