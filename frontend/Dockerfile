# Dockerfile for Svelte + Tailwind frontend
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Development image
FROM base AS dev
CMD ["npm", "run", "dev", "--", "--host"]

# Production image
FROM base AS prod
RUN npm run build
CMD ["npm", "run", "preview", "--", "--host"]

# Set default target
FROM dev
