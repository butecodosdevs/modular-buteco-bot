"""
Enhanced AI Commands with UI Components
"""

from discord import app_commands
import discord
import aiohttp
from typing import Optional
from tools.utils import get_or_create_user, make_api_request, requires_registration
from tools.constants import AI_API_URL, BALANCE_API_URL
from ui.modals import AIPromptModal
from ui.views import ConfirmationView
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


def ai_commands(bot):
    """Register AI commands with UI enhancements"""

    @bot.tree.command(
        name="mestre_dos_magos", description="Consulte a IA usando interface modal"
    )
    @app_commands.describe(provider="Modelo de IA (openai, gemini, etc)")
    async def mestre(interaction: discord.Interaction, provider: Optional[str] = None):
        """Ask AI using modal interface"""

        async def handle_ai_prompt(
            interaction: discord.Interaction,
            prompt: str,
            provider: Optional[str],
            system_prompt: Optional[str],
        ):
            """Handle AI prompt from modal"""
            await interaction.response.defer()

            sender = await get_or_create_user(
                str(interaction.user.id), interaction.user.display_name
            )

            amount = int(os.getenv("AI_USAGE_COST", 100))
            data = {
                "clientId": sender["id"],
                "amount": amount,
                "description": "Pagamento por uso do serviço de IA",
            }

            async with aiohttp.ClientSession() as session:
                status, balance_data = await make_api_request(
                    session, "GET", f"{BALANCE_API_URL}/balance/{sender['id']}"
                )

                if status != 200:
                    embed = discord.Embed(
                        title="❌ Saldo Insuficiente",
                        description=f"Você precisa de **{amount} moedas** para usar a IA.\\nUse `/ver_coins` para verificar seu saldo.",
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed)
                    return

            if balance_data["balance"] < amount:
                embed = discord.Embed(
                    title="❌ Saldo Insuficiente",
                    description=f"Você precisa de **{amount} moedas** para usar a IA.\nUse `/ver_coins_ui` para verificar seu saldo.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            async with aiohttp.ClientSession() as session_payment:
                status, response = await make_api_request(
                    session_payment, "POST", f"{BALANCE_API_URL}/balance/subtract", data
                )

            if status != 200:
                embed = discord.Embed(
                    title="❌ Saldo Insuficiente",
                    description=f"Você precisa de **{amount} moedas** para usar a IA.\\nUse `/ver_coins` para verificar seu saldo.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return

            payload = {"prompt": prompt}
            if provider:
                payload["provider"] = provider
            if system_prompt:
                payload["systemPrompt"] = system_prompt

            async with aiohttp.ClientSession() as session_ai:
                status, response = await make_api_request(
                    session_ai, "POST", f"{AI_API_URL}/GenAI/generate", payload
                )

            if (
                status == 200
                and response
                and isinstance(response, dict)
                and response.get("text")
            ):
                response_text = response.get("text", "Falha ao obter resposta da IA.")

                # Split long responses into multiple embeds if needed
                max_length = 4000
                if len(response_text) > max_length:
                    # Send first part
                    embed = discord.Embed(
                        title="🤖 Resposta da IA (Parte 1)",
                        description=response_text[:max_length],
                        color=discord.Color.blue(),
                    )
                    embed.add_field(
                        name="💬 Seu Prompt", value=prompt[:1024], inline=False
                    )
                    if system_prompt:
                        embed.add_field(
                            name="🎯 Orientação",
                            value=system_prompt[:1024],
                            inline=False,
                        )
                    embed.set_footer(
                        text=f"Custo: {amount} moedas | Provider: {provider or 'padrão'}"
                    )
                    await interaction.followup.send(embed=embed)

                    # Send remaining parts
                    remaining = response_text[max_length:]
                    part = 2
                    while remaining:
                        chunk = remaining[:max_length]
                        remaining = remaining[max_length:]

                        embed = discord.Embed(
                            title=f"🤖 Resposta da IA (Parte {part})",
                            description=chunk,
                            color=discord.Color.blue(),
                        )
                        await interaction.followup.send(embed=embed)
                        part += 1
                else:
                    embed = discord.Embed(
                        title="🤖 Resposta da IA",
                        description=response_text,
                        color=discord.Color.blue(),
                    )
                    embed.add_field(
                        name="💬 Seu Prompt", value=prompt[:1024], inline=False
                    )
                    if system_prompt:
                        embed.add_field(
                            name="🎯 Orientação",
                            value=system_prompt[:1024],
                            inline=False,
                        )
                    embed.set_footer(
                        text=f"Custo: {amount} moedas | Provider: {provider or 'padrão'}"
                    )
                    await interaction.followup.send(embed=embed)
            else:
                error_msg = (
                    response.get("error", "Erro desconhecido")
                    if isinstance(response, dict)
                    else str(response)
                )
                embed = discord.Embed(
                    title="❌ Erro na IA",
                    description=f"Falha ao obter resposta da IA: {error_msg}",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)

        # Show AI prompt modal
        modal = AIPromptModal(provider=provider, callback=handle_ai_prompt)
        await interaction.response.send_modal(modal)
