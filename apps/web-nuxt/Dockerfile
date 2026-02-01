FROM node:20-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
# Enable corepack for pnpm support if needed, though we see package-lock.json so npm is likely used.
# We will stick to npm based on package-lock.json presence.

WORKDIR /app

# Build stage
FROM base AS builder

COPY package.json package-lock.json ./
# Install dependencies (clean install)
RUN npm ci

COPY . .

# Build the application
RUN npm run build

# Production stage
FROM base AS runner

ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

COPY --from=builder /app/.output /app/.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
