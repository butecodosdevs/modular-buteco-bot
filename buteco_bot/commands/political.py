import discord
from discord import app_commands
import aiohttp
from tools.utils import make_api_request
from tools.constants import POLITICAL_API_URL, CLIENT_API_URL

def political_commands(bot):
    @bot.tree.command(name="definir_posicao_politica", description="Define sua posição política no gráfico 2D")
    @app_commands.describe(
        usuario="Usuário para definir a posição política",
        x="Posição no eixo X (horizontal) entre -10 e 10",
        y="Posição no eixo Y (vertical) entre -10 e 10"
    )
    async def definir_posicao_politica(interaction: discord.Interaction, usuario: discord.User, x: float, y: float):
        """Define a posição política de um usuário no gráfico 2D."""
        await interaction.response.defer(ephemeral=True)
        
        # Validate coordinates
        if x < -10 or x > 10 or y < -10 or y > 10:
            embed = discord.Embed(
                title="❌ Coordenadas Inválidas",
                description="As coordenadas X e Y devem estar entre -10 e 10.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        async with aiohttp.ClientSession() as session:
            data = {
                "usuario": str(usuario.id),
                "x": x,
                "y": y
            }
            
            status, response = await make_api_request(
                session, 'POST', f"{POLITICAL_API_URL}/definir_posicao_politica", data
            )
            
            if status == 200:
                embed = discord.Embed(
                    title="✅ Posição Política Definida",
                    description=f"Posição política de {usuario.mention} foi definida com sucesso!",
                    color=discord.Color.green()
                )
                embed.add_field(name="📍 Coordenada X", value=f"`{response.get('x', x)}`", inline=True)
                embed.add_field(name="📍 Coordenada Y", value=f"`{response.get('y', y)}`", inline=True)
                embed.add_field(name="👤 Usuário", value=response.get('name', usuario.display_name), inline=False)
                embed.set_footer(text=f"Formato: {x};{y};{response.get('name', usuario.display_name)}")
            elif status == 404:
                embed = discord.Embed(
                    title="❌ Usuário Não Encontrado",
                    description=f"{usuario.mention} precisa se registrar primeiro usando `/registro`.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Definir Posição",
                    description="Ocorreu um erro ao definir a posição política. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="ver_posicao_politica", description="Visualiza a posição política de um usuário")
    @app_commands.describe(
        usuario="Usuário para visualizar a posição política"
    )
    async def ver_posicao_politica(interaction: discord.Interaction, usuario: discord.User):
        """Visualiza a posição política de um usuário."""
        await interaction.response.defer(ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{POLITICAL_API_URL}/ver_posicao_politica/{usuario.id}"
            )
            
            if status == 200:
                x = response.get('x', 0)
                y = response.get('y', 0)
                name = response.get('name', usuario.display_name)
                
                # Determine quadrant
                if x > 0 and y > 0:
                    quadrant = "🟦 Autoritário Direita"
                elif x < 0 and y > 0:
                    quadrant = "🟥 Autoritário Esquerda"
                elif x > 0 and y < 0:
                    quadrant = "🟨 Libertário Direita"
                else:
                    quadrant = "🟩 Libertário Esquerda"
                
                embed = discord.Embed(
                    title=f"📊 Posição Política de {name}",
                    description=f"Posição no gráfico político 2D",
                    color=discord.Color.blue()
                )
                embed.add_field(name="📍 Coordenada X (Esquerda ← → Direita)", value=f"`{x}`", inline=True)
                embed.add_field(name="📍 Coordenada Y (Libertário ↓ ↑ Autoritário)", value=f"`{y}`", inline=True)
                embed.add_field(name="🎯 Quadrante", value=quadrant, inline=False)
                embed.set_footer(text=f"Formato: {x};{y};{name}")
            elif status == 404:
                embed = discord.Embed(
                    title="❌ Posição Não Encontrada",
                    description=f"{usuario.mention} ainda não definiu sua posição política.\nUse `/definir_posicao_politica` para definir.",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Buscar Posição",
                    description="Ocorreu um erro ao buscar a posição política. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="grafico_politico", description="Mostra o gráfico com todas as posições políticas")
    async def grafico_politico(interaction: discord.Interaction):
        """Mostra todas as posições políticas em formato de gráfico visual."""
        await interaction.response.defer(ephemeral=False)
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{POLITICAL_API_URL}/grafico_politico"
            )
            
            if status == 200:
                positions = response.get('positions', [])
                count = response.get('count', 0)
                
                if count == 0:
                    embed = discord.Embed(
                        title="📊 Gráfico Político",
                        description="Nenhuma posição política foi definida ainda.\nUse `/definir_posicao_politica` para adicionar sua posição!",
                        color=discord.Color.blue()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=False)
                    return
                
                # Generate the graph image
                import matplotlib
                matplotlib.use('Agg')  # Use non-interactive backend
                import matplotlib.pyplot as plt
                import io
                
                # Create figure and axis
                fig, ax = plt.subplots(figsize=(12, 10))
                
                # Set up the plot
                ax.set_xlim(-10, 10)
                ax.set_ylim(-10, 10)
                ax.set_xlabel('Esquerda ← → Direita', fontsize=14, fontweight='bold')
                ax.set_ylabel('Libertário ↓ ↑ Autoritário', fontsize=14, fontweight='bold')
                ax.set_title('Bússola Política dos Usuários', fontsize=18, fontweight='bold', pad=20)
                
                # Add grid
                ax.grid(True, alpha=0.3, linestyle='--')
                
                # Draw axes at origin
                ax.axhline(y=0, color='black', linewidth=2, alpha=0.5)
                ax.axvline(x=0, color='black', linewidth=2, alpha=0.5)
                
                # Add quadrant labels with background
                quadrant_style = dict(fontsize=11, alpha=0.6, style='italic', weight='bold')
                ax.text(5, 5, 'Autoritário\nDireita', ha='center', va='center', **quadrant_style, color='blue')
                ax.text(-5, 5, 'Autoritário\nEsquerda', ha='center', va='center', **quadrant_style, color='red')
                ax.text(5, -5, 'Libertário\nDireita', ha='center', va='center', **quadrant_style, color='gold')
                ax.text(-5, -5, 'Libertário\nEsquerda', ha='center', va='center', **quadrant_style, color='green')
                
                # Add quadrant background colors
                ax.fill_between([-10, 0], 0, 10, alpha=0.1, color='red')
                ax.fill_between([0, 10], 0, 10, alpha=0.1, color='blue')
                ax.fill_between([-10, 0], -10, 0, alpha=0.1, color='green')
                ax.fill_between([0, 10], -10, 0, alpha=0.1, color='gold')
                
                # Plot each position
                colors = []
                for pos in positions:
                    x, y = pos.get('x', 0), pos.get('y', 0)
                    # Determine color based on quadrant
                    if x > 0 and y > 0:
                        colors.append('blue')
                    elif x < 0 and y > 0:
                        colors.append('red')
                    elif x > 0 and y < 0:
                        colors.append('gold')
                    else:
                        colors.append('green')
                
                # Extract coordinates
                x_coords = [pos.get('x', 0) for pos in positions]
                y_coords = [pos.get('y', 0) for pos in positions]
                
                # Plot points
                scatter = ax.scatter(x_coords, y_coords, c=colors, s=200, alpha=0.7, 
                                    edgecolors='black', linewidths=2, zorder=5)
                
                # Add labels for each point
                for pos in positions:
                    x, y = pos.get('x', 0), pos.get('y', 0)
                    name = pos.get('name', 'Unknown')[:10]  # Limit name length
                    ax.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points',
                               fontsize=9, fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))
                
                # Add statistics box
                quadrants = {"Auth-Dir": 0, "Auth-Esq": 0, "Lib-Dir": 0, "Lib-Esq": 0}
                for pos in positions:
                    x, y = pos.get('x', 0), pos.get('y', 0)
                    if x > 0 and y > 0:
                        quadrants["Auth-Dir"] += 1
                    elif x < 0 and y > 0:
                        quadrants["Auth-Esq"] += 1
                    elif x > 0 and y < 0:
                        quadrants["Lib-Dir"] += 1
                    else:
                        quadrants["Lib-Esq"] += 1
                
                stats_text = f"Total: {count} usuários\n"
                stats_text += f"🟦 Auth-Dir: {quadrants['Auth-Dir']}\n"
                stats_text += f"🟥 Auth-Esq: {quadrants['Auth-Esq']}\n"
                stats_text += f"🟨 Lib-Dir: {quadrants['Lib-Dir']}\n"
                stats_text += f"🟩 Lib-Esq: {quadrants['Lib-Esq']}"
                
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                # Adjust layout
                plt.tight_layout()
                
                # Save to bytes buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                plt.close(fig)
                
                # Create Discord file
                file = discord.File(buf, filename='grafico_politico.png')
                
                embed = discord.Embed(
                    title="📊 Gráfico Político - Bússola Política",
                    description=f"Posições políticas de {count} usuário(s)",
                    color=discord.Color.blue()
                )
                embed.set_image(url="attachment://grafico_politico.png")
                embed.set_footer(text="Use /definir_posicao_politica para adicionar ou atualizar sua posição")
                
                await interaction.followup.send(embed=embed, file=file, ephemeral=False)
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Buscar Gráfico",
                    description="Ocorreu um erro ao buscar o gráfico político. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=False)
