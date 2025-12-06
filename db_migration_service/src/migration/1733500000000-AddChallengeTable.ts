import { MigrationInterface, QueryRunner } from "typeorm";

export class AddChallengeTable1733500000000 implements MigrationInterface {
    name = 'AddChallengeTable1733500000000'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`
            CREATE TABLE "challenge" (
                "id" SERIAL NOT NULL,
                "challenger_id" character varying NOT NULL,
                "challenged_id" character varying NOT NULL,
                "channel_id" character varying NOT NULL,
                "status" character varying(20) NOT NULL DEFAULT 'PENDING',
                "challenger_score" integer NOT NULL DEFAULT 0,
                "challenged_score" integer NOT NULL DEFAULT 0,
                "description" character varying(500),
                "created_at" TIMESTAMP NOT NULL DEFAULT now(),
                "updated_at" TIMESTAMP NOT NULL DEFAULT now(),
                "completed_at" TIMESTAMP,
                CONSTRAINT "PK_5f31455ad09ea6a836a06871b7a" PRIMARY KEY ("id")
            )
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "challenge"`);
    }
}
