import openapi from "@elysiajs/openapi";
import { Elysia } from "elysia";
import { BalanceService } from "./modules/balance/balance.service";

const app = new Elysia()
  .use(openapi())
  .decorate("balanceService", new BalanceService())
  .get("/health", () => ({
    status: "healthy",
    service: Bun.env.DATABASE_SCHEMA ?? "unknown",
  }))

  .listen(3000);

console.log(
  `🦊 Elysia is running at ${app.server?.hostname}:${
    app.server?.port
  } [${new Date()}]`
);
