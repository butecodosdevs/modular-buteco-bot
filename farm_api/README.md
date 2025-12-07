# Farm API

## Local development
```bash
bun install
bun run dev
```

## Database migrations
Set `DATABASE_URL` and `DATABASE_SCHEMA` (see repository `.env.example`), then run:
```bash
# generate SQL from schema changes (optional)
bun run db:generate

# run pending migrations
bun run db:migrate
```

Inside Docker, the service exposes `scripts/migrate.sh`, which invokes the same Drizzle command and is used by the `farm-migrator` container.