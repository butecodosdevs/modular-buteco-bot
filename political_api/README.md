# Political Position API

API microservice for managing users' political positions in the Buteco Bot ecosystem.

## Features

- Store and retrieve users' political positions on a 2D political compass
- Validate position coordinates (X and Y between -10 and 10)
- Generate graph data with all users' positions
- Full integration with PostgreSQL database
- RESTful API with JSON responses

## Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

### Set Political Position
```
POST /definir_posicao_politica
Body: {
  "usuario": "discord_id",
  "x": -2.13,
  "y": -1.95
}
```
Sets or updates a user's political position.

### Get Political Position
```
GET /ver_posicao_politica/:usuario
```
Retrieves a specific user's political position.

### Get Graph Data
```
GET /grafico_politico
```
Returns all users' political positions for graph visualization.

## Docker Compose

This service is included in the main `docker-compose.yml` and runs on port 5014.

## Environment Variables

- `DB_HOST` - PostgreSQL host (default: localhost)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name
- `PORT` - Service port (default: 5000)

## Development

```bash
npm install
npm run dev
```

## Production

```bash
npm run build
npm start
```
