import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity()
export class Challenge {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column({ name: "challenger_id" })
    challengerId!: string;

    @Column({ name: "challenged_id" })
    challengedId!: string;

    @Column({ name: "channel_id" })
    channelId!: string;

    @Column({ type: "varchar", length: 20, default: "PENDING" })
    status!: string;

    @Column({ name: "challenger_score", type: "int", default: 0 })
    challengerScore!: number;

    @Column({ name: "challenged_score", type: "int", default: 0 })
    challengedScore!: number;

    @Column({ type: "varchar", length: 500, nullable: true })
    description!: string;

    @CreateDateColumn({ name: "created_at" })
    createdAt!: Date;

    @UpdateDateColumn({ name: "updated_at" })
    updatedAt!: Date;

    @Column({ name: "completed_at", type: "timestamp", nullable: true })
    completedAt!: Date;
}
