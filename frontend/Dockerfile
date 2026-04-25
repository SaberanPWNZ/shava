# syntax=docker/dockerfile:1.7
# ----- Frontend (development) -----
# SvelteKit + Vite dev server with hot reload.
FROM node:20-alpine AS dev

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY package*.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# Run as the unprivileged "node" user shipped with the official image.
RUN chown -R node:node /app
USER node

EXPOSE 5173

CMD ["npx", "vite", "dev", "--host", "0.0.0.0", "--port", "5173"]
