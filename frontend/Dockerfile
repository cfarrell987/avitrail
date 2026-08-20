# Build stage
FROM node:20-alpine AS builder

RUN corepack enable

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

# Baked into the built JS at build time (Vite convention) — override via
# `docker compose build --build-arg VITE_API_BASE_URL=...` for a deployment
# where the backend isn't reachable at localhost:8000 from the browser.
ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN pnpm build

# Runtime stage
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
