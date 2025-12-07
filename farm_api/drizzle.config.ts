import "dotenv/config";
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  out: "./drizzle",
  schema: "./src/modules/database/schema.ts",
  schemaFilter: [process.env.DATABASE_SCHEMA!],
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  migrations: {
    schema: process.env.DATABASE_SCHEMA!,
  },
});
