
FROM node:20-slim AS base

WORKDIR /app

COPY package*.json ./

RUN npm install --no-optional

RUN npm install -g vite

COPY . .

FROM base AS dev

EXPOSE 5173

CMD ["npx", "vite", "dev", "--host", "0.0.0.0"]
