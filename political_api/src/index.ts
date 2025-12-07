import express, { Request, Response } from 'express';
import { Pool } from 'pg';
import cors from 'cors';
import * as dotenv from 'dotenv';
import { PoliticalPositionRequest, PoliticalPositionResponse, GraphDataPoint } from './models/types';

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Database connection
const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
});

// Logging
const log = (message: string) => {
    console.log(`[${new Date().toISOString()}] ${message}`);
};

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
    log('Health check requested');
    res.json({ status: 'healthy', service: 'political-api' });
});

// Define political position
app.post('/definir_posicao_politica', async (req: Request, res: Response) => {
    const { usuario, x, y } = req.body as PoliticalPositionRequest;

    log(`Attempting to set political position for user: ${usuario}, x: ${x}, y: ${y}`);

    // Validate input
    if (!usuario || x === undefined || y === undefined) {
        log('Validation failed: missing required fields');
        return res.status(400).json({ detail: 'Missing required fields: usuario, x, y' });
    }

    if (x < -10 || x > 10 || y < -10 || y > 10) {
        log('Validation failed: coordinates out of range');
        return res.status(400).json({ detail: 'Coordinates must be between -10 and 10' });
    }

    try {
        // First, get the user ID from discord ID
        const userResult = await pool.query(
            'SELECT id, "discordId", name FROM "user" WHERE "discordId" = $1',
            [usuario]
        );

        if (userResult.rows.length === 0) {
            log(`User not found with discordId: ${usuario}`);
            return res.status(404).json({ detail: 'User not found. Please register first using /registro' });
        }

        const userId = userResult.rows[0].id;
        const userName = userResult.rows[0].name;
        log(`Found user: ${userId} (${userName})`);

        // Check if position already exists
        const existingPosition = await pool.query(
            'SELECT id FROM political_position WHERE "userId" = $1',
            [userId]
        );

        let result;
        if (existingPosition.rows.length > 0) {
            // Update existing position
            log(`Updating existing position for user: ${userId}`);
            result = await pool.query(
                `UPDATE political_position 
                 SET "positionX" = $1, "positionY" = $2, "updatedAt" = NOW()
                 WHERE "userId" = $3
                 RETURNING id, "userId", "positionX", "positionY", "createdAt", "updatedAt"`,
                [x, y, userId]
            );
        } else {
            // Insert new position
            log(`Creating new position for user: ${userId}`);
            result = await pool.query(
                `INSERT INTO political_position ("userId", "positionX", "positionY", "createdAt", "updatedAt")
                 VALUES ($1, $2, $3, NOW(), NOW())
                 RETURNING id, "userId", "positionX", "positionY", "createdAt", "updatedAt"`,
                [userId, x, y]
            );
        }

        const position = result.rows[0];
        log(`Successfully set political position: ${position.id}`);

        const response: PoliticalPositionResponse = {
            id: position.id,
            usuario: usuario,
            discordId: usuario,
            name: userName,
            x: parseFloat(position.positionX),
            y: parseFloat(position.positionY),
            createdAt: position.createdAt,
            updatedAt: position.updatedAt
        };

        res.json(response);
    } catch (error) {
        log(`Error setting political position: ${error}`);
        res.status(500).json({ detail: 'Internal server error' });
    }
});

// Get political position by user
app.get('/ver_posicao_politica/:usuario', async (req: Request, res: Response) => {
    const { usuario } = req.params;
    log(`Fetching political position for user: ${usuario}`);

    try {
        const result = await pool.query(
            `SELECT pp.id, pp."userId", pp."positionX", pp."positionY", pp."createdAt", pp."updatedAt",
                    u."discordId", u.name
             FROM political_position pp
             JOIN "user" u ON pp."userId" = u.id
             WHERE u."discordId" = $1`,
            [usuario]
        );

        if (result.rows.length === 0) {
            log(`Political position not found for user: ${usuario}`);
            return res.status(404).json({ detail: 'Political position not found for this user' });
        }

        const position = result.rows[0];
        log(`Successfully retrieved political position: ${position.id}`);

        const response: PoliticalPositionResponse = {
            id: position.id,
            usuario: position.discordId,
            discordId: position.discordId,
            name: position.name,
            x: parseFloat(position.positionX),
            y: parseFloat(position.positionY),
            createdAt: position.createdAt,
            updatedAt: position.updatedAt
        };

        res.json(response);
    } catch (error) {
        log(`Error fetching political position: ${error}`);
        res.status(500).json({ detail: 'Internal server error' });
    }
});

// Get all political positions for graph
app.get('/grafico_politico', async (req: Request, res: Response) => {
    log('Fetching all political positions for graph');

    try {
        const result = await pool.query(
            `SELECT u."discordId" as usuario, u.name, pp."positionX" as x, pp."positionY" as y
             FROM political_position pp
             JOIN "user" u ON pp."userId" = u.id
             ORDER BY u.name`
        );

        log(`Retrieved ${result.rows.length} political positions`);

        const graphData: GraphDataPoint[] = result.rows.map(row => ({
            usuario: row.usuario,
            name: row.name,
            x: parseFloat(row.x),
            y: parseFloat(row.y)
        }));

        res.json({ positions: graphData, count: graphData.length });
    } catch (error) {
        log(`Error fetching graph data: ${error}`);
        res.status(500).json({ detail: 'Internal server error' });
    }
});

// Start server
app.listen(port, () => {
    log(`Political API service listening on port ${port}`);
});
