import discord
import aiohttp
from discord import app_commands
from tools.constants import (
    BALANCE_API_URL,
    CLIENT_API_URL,
    COIN_API_URL,
    BET_API_URL,
    AI_API_URL,
    POLITICAL_API_URL,
    CHALLENGE_API_URL,
)
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def help_commands(bot):
    @bot.tree.command(
        name="health_check", description="Verifique o status de todos os microserviços"
    )
    async def health(interaction: discord.Interaction):
        """Check the health status of all microservices."""
        await interaction.response.defer(ephemeral=True)

        services = [
            ("Balance API", f"{BALANCE_API_URL}/health"),
            ("Client API", f"{CLIENT_API_URL}/health"),
            ("Coin API", f"{COIN_API_URL}/health"),
            ("Bet API", f"{BET_API_URL}/health"),
            ("AI API", f"{AI_API_URL}/health"),
            ("Political API", f"{POLITICAL_API_URL}/health"),
            ("Challenge API", f"{CHALLENGE_API_URL}/health"),
        ]

        embed = discord.Embed(title="🔧 Status do Sistema", color=discord.Color.blue())

        async with aiohttp.ClientSession() as session:
            for service_name, health_url in services:
                try:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            status_emoji = "🟢"
                            status_text = "Online"
                        else:
                            status_emoji = "🟡"
                            status_text = f"Status: {response.status}"
                except Exception as e:
                    logger.error(f"Failed to check service health: {e}")
                    status_emoji = "🔴"
                    status_text = "Offline"

                embed.add_field(
                    name=f"{status_emoji} {service_name}",
                    value=status_text,
                    inline=True,
                )

        embed.add_field(name="🤖 Status do Bot", value="🟢 Online", inline=True)

        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="help", description="Mostre todos os comandos disponíveis")
    async def help(interaction: discord.Interaction):
        """Show help information."""
        logger.info(
            f"Help command requested by {interaction.user.display_name} ({interaction.user.id})"
        )
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🤖 Buteco Bot - Comandos",
            description="Aqui estão todos os comandos slash disponíveis:",
            color=discord.Color.blue(),
        )

        commands_info = [
            ("👤 **Comandos de Usuário**", ""),
            ("/registrar", "Registre-se no sistema"),
            ("/ver_coins [usuário]", "Verifique seu saldo ou de outro usuário"),
            ("", ""),
            ("💰 **Comandos de Economia**", ""),
            ("/daily_coins", "Colete suas moedas diárias"),
            ("/fazer_transferencia <usuário>", "Transfira moedas para outro usuário"),
            ("/extrato", "Veja seu histórico de transações"),
            ("/coin_history", "Veja seu histórico de coletas diárias"),
            ("/faria_limers", "Ranking dos usuários mais ricos"),
            ("", ""),
            ("🎰 **Comandos de Apostas**", ""),
            ("/criar_evento", "Criar novo evento de aposta (Admin)"),
            ("/eventos_listar", "Listar eventos ativos"),
            ("/apostar <event_id>", "Fazer uma aposta em um evento"),
            ("/evento_admin <event_id>", "Gerenciar evento (Admin)"),
            ("", ""),
            ("🗳️ **Comandos Políticos**", ""),
            ("/definir_posicao_politica <usuário>", "Define posição política"),
            ("/ver_posicao_politica <usuário>", "Visualiza posição política"),
            ("/grafico_politico", "Mostra gráfico com todas as posições"),
            ("", ""),
            ("🎯 **Desafios**", ""),
            ("/desafiar <usuário> [descrição]", "Desafiar outro usuário"),
            ("/desafio_ponto <usuário>", "Adicionar ponto em um desafio"),
            ("/desafio_fechar", "Encerrar um desafio ativo"),
            ("/mostrar_desafio", "Mostrar detalhes de um desafio"),
            ("", ""),
            ("🤖 **Inteligência Artificial**", ""),
            ("/mestre_dos_magos [provider]", "Consulte a IA (OpenAI, Gemini, etc)"),
            ("", ""),
            ("🔧 **Comandos do Sistema**", ""),
            ("/health_check", "Verifique o status dos microserviços"),
            ("/codigo_fonte", "Link para o repositório do bot"),
            ("/help", "Mostre esta mensagem de ajuda"),
        ]

        description_lines = []
        for command, desc in commands_info:
            if command and desc:
                description_lines.append(f"**{command}**\n{desc}")
            elif command:
                description_lines.append(f"\n{command}")

        embed.description = "\n".join(description_lines)

        embed.add_field(
            name="💡 Dicas",
            value="• Use `/register` antes de usar comandos de economia\n• Moedas diárias resetam à meia-noite UTC\n• Apostas só podem ser feitas uma vez por evento\n• Verifique `/status` se algo não estiver funcionando",
            inline=False,
        )

        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(
                f"Successfully sent help command response to {interaction.user.display_name}"
            )
        except Exception as e:
            logger.error(f"Failed to send help command response: {e}")
            try:
                await interaction.followup.send(
                    "Comando de ajuda temporariamente indisponível. Tente novamente mais tarde.",
                    ephemeral=True,
                )
            except Exception as e:
                logger.error(f"Failed to send help command response: {e}")
                pass

    @bot.tree.command(
        name="codigo_fonte", description="Pega o repositório do bot no GitHub"
    )
    async def codigo(interaction: discord.Interaction):
        """Get the bot's source code repository."""
        await interaction.response.defer()

        embed = discord.Embed(
            title="📂 Código do Bot",
            description="Você pode encontrar o código fonte do Bot do Buteco no GitHub:",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Repositório",
            value="[Buteco Bot no GitHub](https://github.com/butecodosdevs/modular-buteco-bot)",
            inline=False,
        )
        embed.set_thumbnail(url="https://github.com/butecodosdevs/modular-buteco-bot")
        embed.set_footer(
            text="Aceita Contribuições em qualquer linguagem \n\nLeia o README.md e siga o MICROSERVICE_GUIDE.md !"
        )
        await interaction.followup.send(embed=embed)

    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle application command errors."""
        command_name = interaction.command.name if interaction.command else "unknown"
        user_info = f"{interaction.user.display_name} ({interaction.user.id})"
        logger.error(
            f"Command '{command_name}' raised an exception: {error} (User: {user_info})"
        )

        embed = discord.Embed(
            title="❌ Erro no Comando",
            description="Ocorreu um erro ao processar seu comando.",
            color=discord.Color.red(),
        )

        if isinstance(error, app_commands.CommandOnCooldown):
            embed.description = f"Comando em cooldown. Tente novamente em {error.retry_after:.2f} segundos."
        elif isinstance(error, app_commands.MissingPermissions):
            embed.description = "Você não tem permissão para usar este comando."
        else:
            embed.description = (
                "Ocorreu um erro inesperado. Tente novamente mais tarde."
            )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")
            pass
