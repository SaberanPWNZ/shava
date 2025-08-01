# Development Dockerfile
FROM node:20-alpine

ENV NODE_ENV=development

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./

# Install all dependencies including dev dependencies
RUN npm install

# Copy source code
COPY . .

# Create user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 sveltekit
RUN chown -R sveltekit:nodejs /app

USER sveltekit

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]