# Buteco Bot Ecosystem

A comprehensive Discord bot ecosystem built with Docker containers, featuring economy management, daily rewards, user transfers, AI integration, and a robust microservices architecture.

## 🎮 Discord Bot Features

The Buteco Bot provides a complete economy system and AI assistant through Discord slash commands:

## 🚀 Quick Start

1. **Setup the system:**
   ```bash
   ./setup.sh
   ```

2. **Configure Discord bot:**
   - Get bot token from [Discord Developer Portal](https://discord.com/developers/applications)
   - Edit `.env` file with your `DISCORD_TOKEN` and any AI API keys
   - Invite bot to your server with slash command permissions

3. **Start using:**
   ```
   /register    # Join the economy
   /daily       # Get your first coins
   /balance     # Check your wealth
   /ai          # Use the AI assistant
   ```

## Architecture

The system uses a microservices architecture with Docker containers communicating through a shared network. Each container is independently deployable and scalable, making it easy to add new features or support additional programming languages.

for implement your microsservice see the [MICROSERVICE_GUIDE](MICROSERVICE_GUIDE.md) 

## Features

- Virtual coin system with daily rewards
- Peer-to-peer coin transfers
- Betting system
- AI assistant (OpenAI, Gemini, etc.)
- Leaderboard and transaction history
- Comprehensive command system
- Rich embed responses
- Error handling and status monitoring
- User-friendly help system

## Microservices

Each microservice has its own README with usage and endpoints:
- `client_api/README.md` - User management
- `balance_api/README.md` - Balance and transactions
- `coin_api/README.md` - Daily coins
- `bet_api/README.md` - Betting system
- `ai_api/README.md` - AI assistant
- `political_api/README.md` - Political system

```mermaid
graph TD
    %% Define Nodes with Icons (Using default Mermaid shapes for containers)
    subgraph Services
        A[db-migration-service]
        B[ai-api]
        C[buteco-bot]
        D[coin-api]
        E[balance-api]
        F[client-api]
        G[bet-api]
        H[political-api]
    end

    H{db}

    %% Connections
    A --> H
    B --> H
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H

```

## Development & Contribution
- Test API endpoints and bot commands
- See each microservice's README for details

## Troubleshooting

- Check the troubleshooting section in each README
- View container logs:
  ```bash
  docker-compose logs [service-name]
  ```
- Health check example:
  ```bash
  curl http://localhost:8005/health
  ```

## License

This project is open source and available under the MIT License.

---
*Built with ❤️*
