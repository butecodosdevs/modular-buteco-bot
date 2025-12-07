CREATE SCHEMA IF NOT EXISTS "farm_api";
--> statement-breakpoint
CREATE TYPE "farm_api"."farm_item_types" AS ENUM('ANIMAL', 'LAND', 'UTILITY');--> statement-breakpoint
CREATE TABLE "farm_api"."farm_items_on_farms" (
	"farm_id" integer NOT NULL,
	"item_id" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "farm_api"."farm_items" (
	"id" serial PRIMARY KEY NOT NULL,
	"type" "farm_api"."farm_item_types" NOT NULL,
	"amount" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "farm_api"."farms" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT "farms_name_unique" UNIQUE("name")
);
--> statement-breakpoint
ALTER TABLE "farm_api"."farm_items_on_farms" ADD CONSTRAINT "farm_items_on_farms_farm_id_farms_id_fk" FOREIGN KEY ("farm_id") REFERENCES "farm_api"."farms"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "farm_api"."farm_items_on_farms" ADD CONSTRAINT "farm_items_on_farms_item_id_farm_items_id_fk" FOREIGN KEY ("item_id") REFERENCES "farm_api"."farm_items"("id") ON DELETE no action ON UPDATE no action;