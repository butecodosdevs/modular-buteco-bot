import { relations } from "drizzle-orm";
import { integer, pgSchema, serial, varchar } from "drizzle-orm/pg-core";

export const pgFarmSchema = pgSchema(process.env.DATABASE_SCHEMA!);

export enum EFarmItemTypes {
  ANIMAL = "ANIMAL",
  LAND = "LAND",
  UTILITY = "UTILITY",
}

export const farmItemTypeEnum = pgFarmSchema.enum("farm_item_types", [
  EFarmItemTypes.ANIMAL,
  EFarmItemTypes.LAND,
  EFarmItemTypes.UTILITY,
]);

export const farmItemsTable = pgFarmSchema.table("farm_items", {
  id: serial("id").primaryKey(),
  type: farmItemTypeEnum().notNull(),
  amount: integer("amount").notNull(),
});

export type FarmItem = typeof farmItemsTable.$inferSelect;
export type NewFarmItem = typeof farmItemsTable.$inferInsert;

export const farmItemRelations = relations(farmItemsTable, ({ many }) => ({
  farms: many(farmItemsOnFarmsTable),
}));

export const farmsTable = pgFarmSchema.table("farms", {
  id: serial("id").primaryKey(),
  name: varchar("name").notNull().unique(),
});

export const farmRelations = relations(farmsTable, ({ many }) => ({
  items: many(farmItemsOnFarmsTable),
}));

export const farmItemsOnFarmsTable = pgFarmSchema.table("farm_items_on_farms", {
  farmId: integer("farm_id")
    .notNull()
    .references(() => farmsTable.id),
  itemId: integer("item_id")
    .notNull()
    .references(() => farmItemsTable.id),
});

export const farmItemsOnFarmsRelations = relations(
  farmItemsOnFarmsTable,
  ({ one }) => ({
    farm: one(farmsTable, {
      fields: [farmItemsOnFarmsTable.farmId],
      references: [farmsTable.id],
    }),
    item: one(farmItemsTable, {
      fields: [farmItemsOnFarmsTable.itemId],
      references: [farmItemsTable.id],
    }),
  })
);

export type Farm = typeof farmsTable.$inferSelect;
export type NewFarm = typeof farmsTable.$inferInsert;
