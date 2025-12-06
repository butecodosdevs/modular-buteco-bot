# Challenge API

Challenge management microservice for the Buteco Bot ecosystem. This service handles user challenges, score tracking, and challenge lifecycle management.

## Features

- Create challenges between users
- Accept or reject pending challenges
- Track scores for active challenges (round-based)
- Close completed challenges
- Query challenges by user, channel, or status

## Technology Stack

- **Java 17**
- **Spring Boot 3.2**
- **PostgreSQL** (via JPA/Hibernate)
- **Maven** for dependency management

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Challenge Management
- `POST /challenge/create` - Create a new challenge
- `POST /challenge/{id}/accept` - Accept a pending challenge
- `POST /challenge/{id}/reject` - Reject a pending challenge
- `POST /challenge/{id}/increment` - Increment score for a user
- `POST /challenge/{id}/close` - Close an active challenge
- `GET /challenge/{id}` - Get challenge details
- `GET /challenge/user/{userId}/active` - Get user's active challenges
- `GET /challenge/user/{userId}/pending` - Get user's pending challenges
- `GET /challenge/user/{userId}/all` - Get all user's challenges
- `GET /challenge/channel/{channelId}/active` - Get channel's active challenges

## Running Locally

### Prerequisites
- Java 17+
- Maven 3.9+
- PostgreSQL database

### Build and Run
```bash
mvn clean package
java -jar target/challenge-api-1.0.0.jar
```

## Docker

This service is included in the main `docker-compose.yml`:

```bash
docker-compose up --build challenge-api
```

The service will be available at `http://localhost:5016`

## Environment Variables

- `DB_HOST` - PostgreSQL host (default: postgres-db)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: buteco_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

## Database Schema

The service uses a `challenge` table with the following structure:
- `id` - Primary key
- `challenger_id` - Discord user ID of challenger
- `challenged_id` - Discord user ID of challenged user
- `channel_id` - Discord channel ID
- `status` - Challenge status (PENDING, ACTIVE, COMPLETED, REJECTED)
- `challenger_score` - Score for challenger
- `challenged_score` - Score for challenged user
- `description` - Optional challenge description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `completed_at` - Completion timestamp (nullable)

## Integration with Discord Bot

The Discord bot integrates with this service through the following commands:
- `/desafiar @user [description]` - Create a challenge
- `/desafio_ponto @user` - Increment score
- `/desafio_fechar` - Close a challenge
- `/mostrar_desafio` - Show challenge details
