"""
Enhanced Balance Commands with UI Components
"""
from discord import app_commands
import discord
import aiohttp
from tools.utils import get_or_create_user, make_api_request, requires_registration
from tools.constants import BALANCE_API_URL, CLIENT_API_URL
from ui.modals import TransferCoinsModal
from ui.views import PaginationView
import logging

logger = logging.getLogger(__name__)


def balance_commands(bot):
    """Register balance commands with UI enhancements"""
    
    @bot.tree.command(name="fazer_transferencia", description="Transfira moedas usando interface modal")
    @app_commands.describe(recipient="O usuário para quem transferir moedas")
    @requires_registration()
    async def transferir(interaction: discord.Interaction, recipient: discord.Member):
        """Transfer coins using modal interface"""
        
        if recipient.id == interaction.user.id:
            embed = discord.Embed(
                title="❌ Transferência Inválida",
                description="Você não pode transferir moedas para si mesmo!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        async def handle_transfer(interaction: discord.Interaction, recipient: discord.Member, amount: int, description: str):
            """Handle transfer from modal"""
            await interaction.response.defer(ephemeral=True)
            
            sender = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
            receiver = await get_or_create_user(str(recipient.id), recipient.display_name)
            
            if not sender or not receiver:
                embed = discord.Embed(
                    title="❌ Usuário Não Encontrado",
                    description="Um ou ambos os usuários não estão registrados.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            async with aiohttp.ClientSession() as session:
                status, balance_data = await make_api_request(
                    session, 'GET', f"{BALANCE_API_URL}/balance/{sender['id']}"
                )
                
                if status != 200:
                    embed = discord.Embed(
                        title="❌ Erro",
                        description="Falha ao verificar saldo.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                current_balance = balance_data.get('balance', 0)
                if current_balance < amount:
                    embed = discord.Embed(
                        title="❌ Saldo Insuficiente",
                        description=f"Você tem **{current_balance:,} moedas**, mas precisa de **{amount:,} moedas**.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                transfer_data = {
                    "senderId": sender['id'],
                    "receiverId": receiver['id'],
                    "amount": amount,
                    "description": description
                }
                
                status, response = await make_api_request(
                    session, 'POST', f"{BALANCE_API_URL}/balance/transaction", transfer_data
                )
                
                if status == 200:
                    new_balance = current_balance - amount
                    embed = discord.Embed(
                        title="✅ Transferência Realizada!",
                        description=f"Você transferiu **{amount:,} moedas** para {recipient.mention}",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="💬 Descrição", value=description, inline=False)
                    embed.add_field(name="💰 Seu Saldo Anterior", value=f"{current_balance:,} moedas", inline=True)
                    embed.add_field(name="💵 Seu Saldo Atual", value=f"{new_balance:,} moedas", inline=True)
                    embed.set_thumbnail(url=recipient.display_avatar.url)
                else:
                    embed = discord.Embed(
                        title="❌ Falha na Transferência",
                        description="Falha ao completar a transferência. Tente novamente.",
                        color=discord.Color.red()
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Show transfer modal
        modal = TransferCoinsModal(recipient=recipient, callback=handle_transfer)
        await interaction.response.send_modal(modal)
    
    @bot.tree.command(name="faria_limers", description="Ranking dos usuários mais ricos com interface visual")
    async def top_patroes(interaction: discord.Interaction):
        """Show leaderboard with enhanced UI"""
        await interaction.response.defer()
        
        async with aiohttp.ClientSession() as session:
            status, users = await make_api_request(session, 'GET', f"{CLIENT_API_URL}/client/")
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter dados dos usuários.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            user_balances = []
            for user in users:
                status, balance_data = await make_api_request(
                    session, 'GET', f"{BALANCE_API_URL}/balance/{user['id']}"
                )
                if status == 200:
                    balance = balance_data.get('balance', 0)
                    user_balances.append((user, balance))
            
            user_balances.sort(key=lambda x: x[1], reverse=True)
            
            # Create pages (10 users per page)
            items_per_page = 10
            pages = []
            
            for page_num in range(0, len(user_balances), items_per_page):
                page_items = user_balances[page_num:page_num + items_per_page]
                
                embed = discord.Embed(
                    title="🏆 Ranking - Melhores Usuários",
                    description=f"Top {len(user_balances)} usuários mais ricos do servidor",
                    color=discord.Color.gold()
                )
                
                medals = ["🥇", "🥈", "🥉"]
                
                for i, (user, balance) in enumerate(page_items):
                    actual_rank = page_num + i + 1
                    medal = medals[actual_rank - 1] if actual_rank <= 3 else f"**{actual_rank}.**"
                    
                    try:
                        discord_user = bot.get_user(int(user['discordId']))
                        display_name = discord_user.display_name if discord_user else user['name']
                    except Exception as e:
                        logger.error(f"Erro ao obter nome do usuário: {e}")
                        display_name = user['name']
                    
                    embed.add_field(
                        name=f"{medal} {display_name}",
                        value=f"💰 {balance:,} moedas",
                        inline=True
                    )
                
                embed.set_footer(text=f"Página {len(pages) + 1}/{(len(user_balances) + items_per_page - 1) // items_per_page}")
                pages.append(embed)
            
            if not user_balances:
                embed = discord.Embed(
                    title="🏆 Ranking - Melhores Usuários",
                    description="Nenhum usuário encontrado no ranking.",
                    color=discord.Color.gold()
                )
                await interaction.followup.send(embed=embed)
            elif len(pages) == 1:
                await interaction.followup.send(embed=pages[0])
            else:
                view = PaginationView(pages)
                await interaction.followup.send(embed=pages[0], view=view)
    
    @bot.tree.command(name="extrato", description="Veja seu histórico de transações com paginação")
    async def extrato(interaction: discord.Interaction):
        """Show transaction history with pagination"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        user_data = await get_or_create_user(discord_id, interaction.user.display_name)
        
        async with aiohttp.ClientSession() as session:
            status, operations = await make_api_request(
                session, 'GET', f"{BALANCE_API_URL}/balance/operations/{user_data['id']}"
            )
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter histórico de transações.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if not operations:
                embed = discord.Embed(
                    title="📊 Histórico de Transações",
                    description="Nenhuma transação encontrada.",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            operations.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            
            # Calculate statistics
            total_income = sum(op['amount'] for op in operations if op['amount'] > 0)
            total_expense = sum(abs(op['amount']) for op in operations if op['amount'] < 0)
            
            # Create pages (9 items per page to leave room for stats)
            items_per_page = 9
            pages = []
            
            for page_num in range(0, len(operations), items_per_page):
                page_items = operations[page_num:page_num + items_per_page]
                
                embed = discord.Embed(
                    title="📊 Histórico de Transações",
                    description=f"📈 Total Recebido: **{total_income:,}** moedas\\n📉 Total Gasto: **{total_expense:,}** moedas",
                    color=discord.Color.blue()
                )
                
                for operation in page_items:
                    amount = operation.get('amount', 0)
                    description = operation.get('description', 'Sem descrição')
                    created_at = operation.get('createdAt', '')
                    
                    if amount > 0:
                        amount_str = f"+{amount:,} moedas"
                        color_emoji = "🟢"
                    else:
                        amount_str = f"{amount:,} moedas"
                        color_emoji = "🔴"
                    
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%d/%m/%Y %H:%M')
                    except Exception as e:
                        logger.error(f"Erro ao formatar data: {e}")
                        date_str = "Desconhecido"
                    
                    embed.add_field(
                        name=f"{color_emoji} {amount_str}",
                        value=f"{description}\\n`{date_str}`",
                        inline=True
                    )
                
                embed.set_footer(text=f"Página {len(pages) + 1}/{(len(operations) + items_per_page - 1) // items_per_page}")
                pages.append(embed)
            
            if len(pages) == 1:
                await interaction.followup.send(embed=pages[0], ephemeral=True)
            else:
                view = PaginationView(pages)
                await interaction.followup.send(embed=pages[0], view=view, ephemeral=True)
