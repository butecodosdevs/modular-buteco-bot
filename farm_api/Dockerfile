FROM oven/bun AS base

WORKDIR /app

COPY package.json package.json
COPY bun.lock bun.lock

RUN bun install

COPY ./src ./src
COPY ./drizzle ./drizzle
COPY ./scripts ./scripts
COPY ./drizzle.config.ts ./drizzle.config.ts

ENV NODE_ENV=production

FROM base AS builder

RUN bun build \
  --compile \
  --minify-whitespace \
  --minify-syntax \
  --outfile server \
  src/index.ts

FROM base AS migrator

CMD ["./scripts/migrate.sh"]

FROM gcr.io/distroless/base

WORKDIR /app

COPY --from=builder /app/server server

ENV NODE_ENV=production

CMD ["./server"]

EXPOSE 3000