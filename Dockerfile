FROM node:latest AS base

WORKDIR /app

COPY package*.json ./

RUN npm install --no-optional --no-fund --no-audit

COPY . .

FROM base AS dev

EXPOSE 5173

CMD ["npx", "vite", "dev", "--host", "0.0.0.0"]
