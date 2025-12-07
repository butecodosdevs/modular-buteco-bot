"""
Enhanced Political Commands with UI Components
"""

from discord import app_commands
import discord
import aiohttp
import io
from tools.utils import make_api_request
from tools.constants import POLITICAL_API_URL
from ui.modals import PoliticalPositionModal
import logging
from tools.utils import get_or_create_user
from tools.political_graph import PoliticalGraph
import math

logger = logging.getLogger(__name__)


def political_commands(bot):
    """Register political commands with UI enhancements"""

    @bot.tree.command(
        name="definir_posicao_politica",
        description="Defina sua posição política usando interface modal",
    )
    @app_commands.describe(usuario="Usuário para definir a posição política")
    async def definir_posicao_politica(
        interaction: discord.Interaction, usuario: discord.User
    ):
        """Set political position using modal interface"""

        async def handle_position_set(
            interaction: discord.Interaction, user: discord.User, x: float, y: float
        ):
            """Handle political position from modal"""
            await interaction.response.defer(ephemeral=True)

            await get_or_create_user(str(user.id), user.display_name)

            async with aiohttp.ClientSession() as session:
                data = {"usuario": str(user.id), "x": x, "y": y}

                status, response = await make_api_request(
                    session,
                    "POST",
                    f"{POLITICAL_API_URL}/definir_posicao_politica",
                    data,
                )

                if status == 200:
                    if x > 0 and y > 0:
                        quadrant = "🟦 Autoritário Direita"
                        color = discord.Color.blue()
                    elif x < 0 and y > 0:
                        quadrant = "🟥 Autoritário Esquerda"
                        color = discord.Color.red()
                    elif x > 0 and y < 0:
                        quadrant = "🟨 Libertário Direita"
                        color = discord.Color.gold()
                    else:
                        quadrant = "🟩 Libertário Esquerda"
                        color = discord.Color.green()

                    embed = discord.Embed(
                        title="✅ Posição Política Definida!",
                        description=f"Posição política de {user.mention} foi definida com sucesso!",
                        color=color,
                    )
                    embed.add_field(
                        name="📍 Coordenada X (Esquerda ← → Direita)",
                        value=f"`{x}`",
                        inline=True,
                    )
                    embed.add_field(
                        name="📍 Coordenada Y (Libertário ↓ ↑ Autoritário)",
                        value=f"`{y}`",
                        inline=True,
                    )
                    embed.add_field(name="🎯 Quadrante", value=quadrant, inline=False)
                    embed.add_field(
                        name="📊 Ver Gráfico",
                        value="Use `/grafico_politico` para ver todas as posições!",
                        inline=False,
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)
                    embed.set_footer(
                        text=f"Formato: {x};{y};{response.get('name', user.display_name)}"
                    )
                elif status == 404:
                    embed = discord.Embed(
                        title="❌ Usuário Não Encontrado",
                        description=f"{user.mention} precisa se registrar primeiro usando `/registrar`.",
                        color=discord.Color.red(),
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Erro ao Definir Posição",
                        description="Ocorreu um erro ao definir a posição política. Tente novamente mais tarde.",
                        color=discord.Color.red(),
                    )

            await interaction.followup.send(embed=embed, ephemeral=True)

        modal = PoliticalPositionModal(user=usuario, callback=handle_position_set)
        await interaction.response.send_modal(modal)

    @bot.tree.command(
        name="ver_posicao_politica",
        description="Visualize a posição política com interface aprimorada",
    )
    @app_commands.describe(usuario="Usuário para visualizar a posição política")
    async def ver_posicao_politica(
        interaction: discord.Interaction, usuario: discord.User
    ):
        """View political position with enhanced UI"""
        await interaction.response.defer(ephemeral=True)

        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, "GET", f"{POLITICAL_API_URL}/ver_posicao_politica/{usuario.id}"
            )

            if status == 200:
                x = response.get("x", 0)
                y = response.get("y", 0)
                name = response.get("name", usuario.display_name)

                if x > 0 and y > 0:
                    quadrant = "🟦 Autoritário Direita"
                    color = discord.Color.blue()
                    description = "Favorece autoridade e políticas de direita"
                elif x < 0 and y > 0:
                    quadrant = "🟥 Autoritário Esquerda"
                    color = discord.Color.red()
                    description = "Favorece autoridade e políticas de esquerda"
                elif x > 0 and y < 0:
                    quadrant = "🟨 Libertário Direita"
                    color = discord.Color.gold()
                    description = "Favorece liberdade individual e políticas de direita"
                else:
                    quadrant = "🟩 Libertário Esquerda"
                    color = discord.Color.green()
                    description = (
                        "Favorece liberdade individual e políticas de esquerda"
                    )

                distance = math.sqrt(x**2 + y**2)
                intensity = (
                    "Moderado"
                    if distance < 5
                    else "Forte"
                    if distance < 8
                    else "Extremo"
                )

                embed = discord.Embed(
                    title=f"📊 Posição Política de {name}",
                    description=description,
                    color=color,
                )
                embed.add_field(name="📍 Coordenada X", value=f"`{x}`", inline=True)
                embed.add_field(name="📍 Coordenada Y", value=f"`{y}`", inline=True)
                embed.add_field(name="🎯 Quadrante", value=quadrant, inline=False)
                embed.add_field(name="💪 Intensidade", value=intensity, inline=True)
                embed.add_field(
                    name="📏 Distância do Centro", value=f"{distance:.2f}", inline=True
                )
                embed.set_thumbnail(url=usuario.display_avatar.url)
                embed.set_footer(
                    text=f"Formato: {x};{y};{name} | Use /grafico_politico para ver o gráfico completo"
                )
            elif status == 404:
                embed = discord.Embed(
                    title="❌ Posição Não Encontrada",
                    description=f"{usuario.mention} ainda não definiu sua posição política.\\n\\nUse `/definir_posicao_politica` para definir!",
                    color=discord.Color.orange(),
                )
                embed.add_field(
                    name="🧭 Como Descobrir Sua Posição?",
                    value="Faça o teste em: [politicalcompass.org/test/pt-pt](https://www.politicalcompass.org/test/pt-pt)",
                    inline=False,
                )
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Buscar Posição",
                    description="Ocorreu um erro ao buscar a posição política. Tente novamente mais tarde.",
                    color=discord.Color.red(),
                )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="grafico_politico",
        description="Mostra o gráfico com todas as posições políticas",
    )
    async def grafico_politico(interaction: discord.Interaction):
        """Mostra todas as posições políticas em formato de gráfico visual."""
        await interaction.response.defer(ephemeral=False)

        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, "GET", f"{POLITICAL_API_URL}/grafico_politico"
            )

            if status == 200:
                positions_data = response.get("positions", [])
                count = response.get("count", 0)

                if count == 0:
                    embed = discord.Embed(
                        title="📊 Gráfico Político",
                        description="Nenhuma posição política foi definida ainda.\nUse `/definir_posicao_politica` para adicionar sua posição!",
                        color=discord.Color.blue(),
                    )
                    await interaction.followup.send(embed=embed, ephemeral=False)
                    return

                points = []
                for pos in positions_data:
                    points.append(
                        (pos.get("x", 0), pos.get("y", 0), pos.get("name", "Unknown"))
                    )

                political_graph = PoliticalGraph()
                fig = political_graph.create_figure(points)

                img_bytes = fig.to_image(format="png", width=1600, height=1200, scale=2)
                file = discord.File(
                    io.BytesIO(img_bytes), filename="grafico_politico.png"
                )

                embed = discord.Embed(
                    title="📊 Gráfico Político - Bússola Política",
                    description=f"Posições políticas de {count} usuário(s)",
                    color=discord.Color.blue(),
                )
                embed.set_image(url="attachment://grafico_politico.png")
                embed.set_footer(
                    text=(
                        "Use /definir_posicao_politica para adicionar ou atualizar sua posição\n"
                        "Caso sua posição não esteja presente e você tenha feito no python legado, "
                        "pegue os valores aqui: github.com/butecodosdevs/buteco-political-compass\n"
                        "Caso não tenha feito o teste, utilize: politicalcompass.org/test/pt-pt"
                    )
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=False)
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Buscar Gráfico",
                    description="Ocorreu um erro ao buscar o gráfico político. Tente novamente mais tarde.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=False)
