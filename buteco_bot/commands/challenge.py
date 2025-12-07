"""
Challenge Commands - Manage user challenges with scoring
"""

from discord import app_commands
import discord
import aiohttp
from tools.utils import make_api_request, requires_registration
from tools.constants import CHALLENGE_API_URL
from ui.views import ConfirmationView
import logging

logger = logging.getLogger(__name__)


def challenge_commands(bot):
    """Register challenge management commands"""

    @bot.tree.command(
        name="desafiar", description="Desafiar outro usuário para uma competição"
    )
    @app_commands.describe(
        user="Usuário que você quer desafiar",
        description="Descrição do desafio (opcional)",
    )
    @requires_registration()
    async def desafiar(
        interaction: discord.Interaction, user: discord.User, description: str = None
    ):
        """Challenge another user to a competition"""
        await interaction.response.defer(ephemeral=True)

        challenger_id = str(interaction.user.id)
        challenged_id = str(user.id)
        channel_id = str(interaction.channel_id)

        # Prevent self-challenge
        if challenger_id == challenged_id:
            embed = discord.Embed(
                title="❌ Erro",
                description="Você não pode desafiar a si mesmo!",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        async with aiohttp.ClientSession() as session:
            challenge_data = {
                "challengerId": challenger_id,
                "challengedId": challenged_id,
                "channelId": channel_id,
                "description": description,
            }

            status, response = await make_api_request(
                session, "POST", f"{CHALLENGE_API_URL}/challenge/create", challenge_data
            )

            if status == 201:
                challenge_id = response.get("id")

                # Send confirmation to challenger
                embed = discord.Embed(
                    title="🎯 Desafio Criado!",
                    description=f"Você desafiou {user.mention}!",
                    color=discord.Color.blue(),
                )
                if description:
                    embed.add_field(name="Descrição", value=description, inline=False)
                embed.add_field(
                    name="ID do Desafio", value=f"`{challenge_id}`", inline=False
                )
                embed.set_footer(text="Aguardando resposta do oponente...")

                await interaction.followup.send(embed=embed, ephemeral=True)

                # Send challenge notification to challenged user with buttons
                async def handle_accept(button_interaction: discord.Interaction):
                    """Handle challenge acceptance"""
                    await button_interaction.response.defer()

                    async with aiohttp.ClientSession() as session:
                        status, response = await make_api_request(
                            session,
                            "POST",
                            f"{CHALLENGE_API_URL}/challenge/{challenge_id}/accept",
                            {},
                        )

                        if status == 200:
                            accept_embed = discord.Embed(
                                title="✅ Desafio Aceito!",
                                description=f"{user.mention} aceitou o desafio de {interaction.user.mention}!",
                                color=discord.Color.green(),
                            )
                            if description:
                                accept_embed.add_field(
                                    name="Descrição", value=description, inline=False
                                )
                            accept_embed.add_field(
                                name="Placar", value="0 - 0", inline=False
                            )
                            accept_embed.set_footer(text=f"ID: {challenge_id}")

                            await button_interaction.followup.send(embed=accept_embed)
                        else:
                            error_msg = response.get("detail", "Erro desconhecido")
                            error_embed = discord.Embed(
                                title="❌ Erro",
                                description=error_msg,
                                color=discord.Color.red(),
                            )
                            await button_interaction.followup.send(
                                embed=error_embed, ephemeral=True
                            )

                async def handle_reject(button_interaction: discord.Interaction):
                    """Handle challenge rejection"""
                    await button_interaction.response.defer()

                    async with aiohttp.ClientSession() as session:
                        status, response = await make_api_request(
                            session,
                            "POST",
                            f"{CHALLENGE_API_URL}/challenge/{challenge_id}/reject",
                            {},
                        )

                        if status == 200:
                            reject_embed = discord.Embed(
                                title="❌ Desafio Recusado",
                                description=f"{user.mention} recusou o desafio de {interaction.user.mention}.",
                                color=discord.Color.red(),
                            )
                            await button_interaction.followup.send(embed=reject_embed)
                        else:
                            error_msg = response.get("detail", "Erro desconhecido")
                            error_embed = discord.Embed(
                                title="❌ Erro",
                                description=error_msg,
                                color=discord.Color.red(),
                            )
                            await button_interaction.followup.send(
                                embed=error_embed, ephemeral=True
                            )

                # Create notification embed for challenged user
                notification_embed = discord.Embed(
                    title="🎯 Você Foi Desafiado!",
                    description=f"{interaction.user.mention} desafiou você!",
                    color=discord.Color.orange(),
                )
                if description:
                    notification_embed.add_field(
                        name="Descrição", value=description, inline=False
                    )
                notification_embed.set_footer(text="Aceite ou recuse o desafio abaixo")

                # Create view with accept/reject buttons
                view = ConfirmationView(
                    on_confirm=handle_accept, on_cancel=handle_reject
                )

                try:
                    await user.send(embed=notification_embed, view=view)
                except discord.Forbidden:
                    # If can't DM, send in channel
                    await interaction.channel.send(
                        f"{user.mention}", embed=notification_embed, view=view
                    )

            elif status == 400:
                error_msg = response.get("detail", "Erro ao criar desafio")
                embed = discord.Embed(
                    title="❌ Erro", description=error_msg, color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao criar desafio. Tente novamente mais tarde.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="desafio_ponto", description="Adicionar ponto em um desafio ativo"
    )
    @app_commands.describe(user="Usuário que ganhou o ponto")
    @requires_registration()
    async def desafio_ponto(interaction: discord.Interaction, user: discord.User):
        """Increment score for a user in an active challenge"""
        await interaction.response.defer(ephemeral=True)

        current_user_id = str(interaction.user.id)
        target_user_id = str(user.id)

        async with aiohttp.ClientSession() as session:
            # Get active challenges for current user
            status, response = await make_api_request(
                session,
                "GET",
                f"{CHALLENGE_API_URL}/challenge/user/{current_user_id}/active",
            )

            if status != 200 or not response:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Você não tem desafios ativos.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Find challenge with the target user
            active_challenges = response
            matching_challenge = None

            for challenge in active_challenges:
                if (
                    challenge["challengerId"] == target_user_id
                    or challenge["challengedId"] == target_user_id
                ):
                    matching_challenge = challenge
                    break

            if not matching_challenge:
                embed = discord.Embed(
                    title="❌ Erro",
                    description=f"Você não tem um desafio ativo com {user.mention}.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Increment score
            challenge_id = matching_challenge["id"]
            increment_data = {"challengeId": challenge_id, "userId": target_user_id}

            status, response = await make_api_request(
                session,
                "POST",
                f"{CHALLENGE_API_URL}/challenge/{challenge_id}/increment",
                increment_data,
            )

            if status == 200:
                updated_challenge = response
                challenger_score = updated_challenge["challengerScore"]
                challenged_score = updated_challenge["challengedScore"]

                # Get user mentions
                challenger = await bot.fetch_user(
                    int(updated_challenge["challengerId"])
                )
                challenged = await bot.fetch_user(
                    int(updated_challenge["challengedId"])
                )

                embed = discord.Embed(
                    title="🎯 Ponto Adicionado!",
                    description=f"Ponto para {user.mention}!",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name="Placar Atual",
                    value=f"{challenger.mention}: **{challenger_score}** - {challenged.mention}: **{challenged_score}**",
                    inline=False,
                )
                if updated_challenge.get("description"):
                    embed.add_field(
                        name="Desafio",
                        value=updated_challenge["description"],
                        inline=False,
                    )

                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                error_msg = response.get("detail", "Erro ao adicionar ponto")
                embed = discord.Embed(
                    title="❌ Erro", description=error_msg, color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="desafio_fechar", description="Encerrar um desafio ativo")
    @requires_registration()
    async def desafio_fechar(interaction: discord.Interaction):
        """Close an active challenge"""
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)

        async with aiohttp.ClientSession() as session:
            # Get active challenges
            status, response = await make_api_request(
                session, "GET", f"{CHALLENGE_API_URL}/challenge/user/{user_id}/active"
            )

            if status != 200 or not response:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Você não tem desafios ativos.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            active_challenges = response

            if len(active_challenges) == 0:
                embed = discord.Embed(
                    title="ℹ️ Sem Desafios",
                    description="Você não tem desafios ativos para fechar.",
                    color=discord.Color.blue(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # If only one challenge, close it directly
            if len(active_challenges) == 1:
                challenge = active_challenges[0]
                challenge_id = challenge["id"]

                status, response = await make_api_request(
                    session,
                    "POST",
                    f"{CHALLENGE_API_URL}/challenge/{challenge_id}/close",
                    {},
                )

                if status == 200:
                    closed_challenge = response
                    challenger_score = closed_challenge["challengerScore"]
                    challenged_score = closed_challenge["challengedScore"]

                    # Get user mentions
                    challenger = await bot.fetch_user(
                        int(closed_challenge["challengerId"])
                    )
                    challenged = await bot.fetch_user(
                        int(closed_challenge["challengedId"])
                    )

                    # Determine winner
                    if challenger_score > challenged_score:
                        winner = challenger.mention
                    elif challenged_score > challenger_score:
                        winner = challenged.mention
                    else:
                        winner = "Empate!"

                    embed = discord.Embed(
                        title="🏁 Desafio Encerrado!",
                        description=f"Vencedor: {winner}",
                        color=discord.Color.gold(),
                    )
                    embed.add_field(
                        name="Placar Final",
                        value=f"{challenger.mention}: **{challenger_score}** - {challenged.mention}: **{challenged_score}**",
                        inline=False,
                    )
                    if closed_challenge.get("description"):
                        embed.add_field(
                            name="Desafio",
                            value=closed_challenge["description"],
                            inline=False,
                        )

                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    error_msg = response.get("detail", "Erro ao fechar desafio")
                    embed = discord.Embed(
                        title="❌ Erro",
                        description=error_msg,
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                # Multiple challenges - show selection
                embed = discord.Embed(
                    title="🎯 Seus Desafios Ativos",
                    description="Você tem múltiplos desafios ativos. Use `/mostrar_desafio` para ver detalhes e fechar um específico.",
                    color=discord.Color.blue(),
                )

                for i, challenge in enumerate(active_challenges[:5], 1):
                    opponent_id = (
                        challenge["challengedId"]
                        if challenge["challengerId"] == user_id
                        else challenge["challengerId"]
                    )
                    try:
                        opponent = await bot.fetch_user(int(opponent_id))
                        opponent_name = opponent.display_name
                    except:
                        opponent_name = "Usuário Desconhecido"

                    score_text = f"{challenge['challengerScore']} - {challenge['challengedScore']}"
                    embed.add_field(
                        name=f"{i}. vs {opponent_name}",
                        value=f"Placar: {score_text}\nID: `{challenge['id']}`",
                        inline=False,
                    )

                await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="mostrar_desafio", description="Mostrar detalhes de um desafio"
    )
    @requires_registration()
    async def mostrar_desafio(interaction: discord.Interaction):
        """Show challenge details with option to broadcast"""
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)

        async with aiohttp.ClientSession() as session:
            # Get active challenges
            status, response = await make_api_request(
                session, "GET", f"{CHALLENGE_API_URL}/challenge/user/{user_id}/active"
            )

            if status != 200 or not response:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Você não tem desafios ativos.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            active_challenges = response

            if len(active_challenges) == 0:
                embed = discord.Embed(
                    title="ℹ️ Sem Desafios",
                    description="Você não tem desafios ativos.",
                    color=discord.Color.blue(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Show first challenge (or could implement selection)
            challenge = active_challenges[0]
            challenger_score = challenge["challengerScore"]
            challenged_score = challenge["challengedScore"]

            # Get user mentions
            challenger = await bot.fetch_user(int(challenge["challengerId"]))
            challenged = await bot.fetch_user(int(challenge["challengedId"]))

            embed = discord.Embed(
                title="🎯 Detalhes do Desafio",
                description=f"{challenger.mention} vs {challenged.mention}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Placar",
                value=f"{challenger.mention}: **{challenger_score}** - {challenged.mention}: **{challenged_score}**",
                inline=False,
            )
            if challenge.get("description"):
                embed.add_field(
                    name="Descrição", value=challenge["description"], inline=False
                )
            embed.add_field(name="ID", value=f"`{challenge['id']}`", inline=False)
            embed.set_footer(text="Clique no botão abaixo para mostrar no canal")

            # Create broadcast button
            async def handle_broadcast(button_interaction: discord.Interaction):
                """Broadcast challenge to channel"""
                await button_interaction.response.defer()

                broadcast_embed = discord.Embed(
                    title="🎯 Desafio em Andamento",
                    description=f"{challenger.mention} vs {challenged.mention}",
                    color=discord.Color.gold(),
                )
                broadcast_embed.add_field(
                    name="Placar",
                    value=f"{challenger.mention}: **{challenger_score}** - {challenged.mention}: **{challenged_score}**",
                    inline=False,
                )
                if challenge.get("description"):
                    broadcast_embed.add_field(
                        name="Descrição", value=challenge["description"], inline=False
                    )
                broadcast_embed.set_footer(
                    text=f"Compartilhado por {interaction.user.display_name}"
                )

                await interaction.channel.send(embed=broadcast_embed)

                confirm_embed = discord.Embed(
                    title="✅ Compartilhado!",
                    description="O desafio foi mostrado no canal.",
                    color=discord.Color.green(),
                )
                await button_interaction.followup.send(
                    embed=confirm_embed, ephemeral=True
                )

            # Create view with broadcast button
            view = discord.ui.View()
            broadcast_button = discord.ui.Button(
                label="📢 Mostrar no Canal", style=discord.ButtonStyle.primary
            )
            broadcast_button.callback = handle_broadcast
            view.add_item(broadcast_button)

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
