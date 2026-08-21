# Build stage
FROM node:20-alpine AS builder

RUN corepack enable

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

# Compiled-in fallback (Vite bakes import.meta.env.* at build time). The
# real per-deployment override is the $API_BASE_URL *runtime* env var below
# (see runtime-config-entrypoint.sh) — this only matters if that's unset.
ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN pnpm build

# Runtime stage
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY runtime-config-entrypoint.sh /runtime-config-entrypoint.sh
RUN chmod +x /runtime-config-entrypoint.sh

EXPOSE 80

# Generates runtime-config.js from $API_BASE_URL on every container start,
# then hands off to nginx's own official entrypoint chain (kept intact —
# this doesn't replace it, just runs first).
ENTRYPOINT ["/runtime-config-entrypoint.sh"]
CMD ["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"]
