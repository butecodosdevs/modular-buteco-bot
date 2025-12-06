"""
Enhanced Coins Commands with UI Components
"""
from discord import app_commands
import discord
import aiohttp
from typing import Optional
from tools.utils import get_or_create_user, make_api_request, requires_registration
from tools.constants import BALANCE_API_URL, COIN_API_URL
from ui.views import ConfirmationView, PaginationView
import logging

logger = logging.getLogger(__name__)


def coins_commands(bot):
    """Register coins commands with UI enhancements"""
    
    @bot.tree.command(name="coins", description="Colete suas moedas diárias com interface interativa")
    @requires_registration()
    async def coins(interaction: discord.Interaction):
        """Claim daily coins with interactive UI"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        user_data = await get_or_create_user(discord_id, interaction.user.display_name)
        
        async with aiohttp.ClientSession() as session:
            claim_data = {"clientId": user_data['id']}
            status, response = await make_api_request(
                session, 'POST', f"{COIN_API_URL}/daily-coins", claim_data
            )
            
            if status == 200:
                amount = response.get('amount', 0)
                
                # Get updated balance
                status_balance, balance_data = await make_api_request(
                    session, 'GET', f"{BALANCE_API_URL}/balance/{user_data['id']}"
                )
                current_balance = balance_data.get('balance', 0) if status_balance == 200 else 0
                
                embed = discord.Embed(
                    title="🎉 Moedas Diárias Coletadas!",
                    description=f"Você recebeu **{amount:,} moedas**! 🪙",
                    color=discord.Color.gold()
                )
                embed.add_field(name="💰 Saldo Atual", value=f"{current_balance:,} moedas", inline=True)
                embed.add_field(name="⏰ Próxima Coleta", value="Volte amanhã!", inline=True)
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text=f"Continue coletando diariamente para acumular moedas!")
                
            elif status == 400:
                embed = discord.Embed(
                    title="⏰ Já Coletado Hoje",
                    description="Você já coletou suas moedas diárias hoje!\\n\\nVolte amanhã para coletar novamente! ⏰",
                    color=discord.Color.orange()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
            else:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao coletar moedas diárias. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="ver_coins", description="Verifique seu saldo com interface visual")
    @requires_registration()
    async def ver_coins(interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check balance with enhanced UI"""
        await interaction.response.defer(ephemeral=True)
        
        target_user = user if user else interaction.user
        discord_id = str(target_user.id)
        
        user_data = await get_or_create_user(discord_id, target_user.display_name)
        
        async with aiohttp.ClientSession() as session:
            status, balance_data = await make_api_request(
                session, 'GET', f"{BALANCE_API_URL}/balance/{user_data['id']}"
            )
            
            if status == 200:
                balance_amount = balance_data.get('balance', 0)
                
                # Get coin history for stats
                status_history, history_data = await make_api_request(
                    session, 'GET', f"{COIN_API_URL}/daily-coins/history/{user_data['id']}?limit=30"
                )
                
                total_claims = history_data.get('totalClaims', 0) if status_history == 200 else 0
                total_earned = history_data.get('totalCoinsEarned', 0) if status_history == 200 else 0
                
                embed = discord.Embed(
                    title=f"💰 Carteira de {target_user.display_name}",
                    description=f"Informações financeiras completas",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="💵 Saldo Atual",
                    value=f"**{balance_amount:,} moedas** 🪙",
                    inline=False
                )
                
                if total_claims > 0:
                    embed.add_field(name="📅 Total de Coletas", value=f"{total_claims} dias", inline=True)
                    embed.add_field(name="🎁 Total Coletado", value=f"{total_earned:,} moedas", inline=True)
                    avg_per_day = total_earned / total_claims if total_claims > 0 else 0
                    embed.add_field(name="📊 Média por Dia", value=f"{avg_per_day:.0f} moedas", inline=True)
                
                embed.set_thumbnail(url=target_user.display_avatar.url)
                embed.set_footer(text="Use /coins_ui para coletar suas moedas diárias!")
            else:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter informações do saldo.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="historico_de_coins", description="Veja seu histórico de coletas com paginação")
    @requires_registration()
    async def historico_de_coins(interaction: discord.Interaction):
        """Show coin history with pagination"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        user_data = await get_or_create_user(discord_id, interaction.user.display_name)
        
        async with aiohttp.ClientSession() as session:
            status, history_data = await make_api_request(
                session, 'GET', f"{COIN_API_URL}/daily-coins/history/{user_data['id']}?limit=50"
            )
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter histórico de coletas diárias.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            total_claims = history_data.get('totalClaims', 0)
            total_earned = history_data.get('totalCoinsEarned', 0)
            history = history_data.get('history', [])
            
            if not history:
                embed = discord.Embed(
                    title="📅 Histórico de Coletas Diárias",
                    description="Nenhuma coleta diária encontrada. Use `/coins_ui` para começar a coletar!",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create pages (10 items per page)
            items_per_page = 10
            pages = []
            
            for page_num in range(0, len(history), items_per_page):
                page_items = history[page_num:page_num + items_per_page]
                
                embed = discord.Embed(
                    title="📅 Histórico de Coletas Diárias",
                    description=f"Total de Coletas: **{total_claims}** | Total Ganho: **{total_earned:,} moedas**",
                    color=discord.Color.blue()
                )
                
                for claim in page_items:
                    claim_date = claim.get('claimDate', 'Unknown')
                    amount = claim.get('amount', 0)
                    
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(claim_date)
                        date_str = dt.strftime('%d/%m/%Y')
                    except:
                        date_str = claim_date
                    
                    embed.add_field(
                        name=f"🗓️ {date_str}",
                        value=f"+{amount:,} moedas 🪙",
                        inline=True
                    )
                
                embed.set_footer(text=f"Página {len(pages) + 1}/{(len(history) + items_per_page - 1) // items_per_page}")
                pages.append(embed)
            
            if len(pages) == 1:
                await interaction.followup.send(embed=pages[0], ephemeral=True)
            else:
                view = PaginationView(pages)
                await interaction.followup.send(embed=pages[0], view=view, ephemeral=True)
