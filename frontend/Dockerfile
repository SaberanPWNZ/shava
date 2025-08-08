# --- Base image ---
FROM node:20-alpine AS base
WORKDIR /app

COPY package.json ./

RUN npm install && \
    npm install tailwindcss@latest @tailwindcss/vite@latest @sveltejs/vite-plugin-svelte@latest

COPY . .
FROM base AS dev
CMD ["npm", "run", "dev", "--", "--host"]

FROM base AS prod
RUN npm run build
CMD ["npm", "run", "preview", "--", "--host"]

FROM dev
