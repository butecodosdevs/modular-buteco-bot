"""
Bet Commands with UI Components
Example implementation showing how to use modals and views
"""
from discord import app_commands
import discord
import aiohttp
from tools.utils import make_api_request, get_or_create_user, is_admin, requires_registration
from tools.constants import BET_API_URL
from ui.modals import BetCreationModal
from ui.views import BetEventView, BetSelectionView, AdminActionsView
import logging

logger = logging.getLogger(__name__)


def bet_commands(bot):
    """Register bet commands that use UI components"""
    
    @bot.tree.command(name="criar_evento", description="Criar um novo evento de aposta usando interface modal (Admin)")
    async def criar_evento(interaction: discord.Interaction):
        """Create a new bet event using a modal interface"""
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem criar eventos de aposta.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        async def handle_bet_creation(interaction: discord.Interaction, title: str, description: str, option1: str, option2: str):
            """Callback for bet creation modal"""
            await interaction.response.defer()
            
            async with aiohttp.ClientSession() as session:
                bet_data = {
                    "title": title,
                    "description": description,
                    "option1": option1,
                    "option2": option2
                }
                
                status, response = await make_api_request(
                    session, 'POST', f"{BET_API_URL}/bet/event", bet_data
                )
                
                if status == 200:
                    event_id = response.get('eventId', 'Unknown')
                    embed = discord.Embed(
                        title="🎰 Evento de Aposta Criado com Sucesso!",
                        description=f"**{title}**\n{description}",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="ID do Evento", value=f"`{event_id}`", inline=False)
                    embed.add_field(name="Opção 1", value=f"🅰️ {option1}", inline=True)
                    embed.add_field(name="Opção 2", value=f"🅱️ {option2}", inline=True)
                    embed.set_footer(text=f"Criado por {interaction.user.display_name}")
                    
                    # Add interactive view
                    event_data = {
                        'title': title,
                        'description': description,
                        'option1': option1,
                        'option2': option2,
                        'totalBetAmount': 0,
                        'option1BetAmount': 0,
                        'option2BetAmount': 0
                    }
                    view = BetEventView(event_id, event_data, on_bet_callback=handle_place_bet)
                    
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    embed = discord.Embed(
                        title="❌ Erro ao Criar Evento",
                        description="Falha ao criar o evento. Tente novamente mais tarde.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
        
        modal = BetCreationModal(callback=handle_bet_creation)
        await interaction.response.send_modal(modal)
    
    @bot.tree.command(name="apostar", description="Fazer uma aposta usando interface interativa")
    @app_commands.describe(event_id="ID do evento de aposta")
    @requires_registration()
    async def apostar(interaction: discord.Interaction, event_id: str):
        """Place a bet using interactive UI"""
        await interaction.response.defer(ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Evento Não Encontrado",
                    description=f"Não foi possível encontrar o evento com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            elif status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter informações do evento.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            event = response.get('event', {})
            
            embed = discord.Embed(
                title=f"🎰 {event['title']}",
                description=event.get('description', ''),
                color=discord.Color.blue()
            )
            
            embed.add_field(name="🅰️ Opção 1", value=event.get('option1', 'Opção 1'), inline=True)
            embed.add_field(name="🅱️ Opção 2", value=event.get('option2', 'Opção 2'), inline=True)
            embed.add_field(name="Pool Total", value=f"{event.get('totalBetAmount', 0):,} moedas", inline=True)
            
            view = BetEventView(event_id, event, on_bet_callback=handle_place_bet)
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @bot.tree.command(name="eventos_listar", description="Listar eventos ativos")
    async def eventos_listar(interaction: discord.Interaction):
        """List active bets with interactive selection"""
        await interaction.response.defer(ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/events"
            )
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter lista de eventos ativos.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            active_events = response.get('events', [])
            
            if not active_events:
                embed = discord.Embed(
                    title="🎰 Eventos Ativos",
                    description="Nenhum evento ativo no momento.",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎰 Eventos Ativos",
                description=f"Encontrados {len(active_events)} eventos ativos. Selecione um abaixo:",
                color=discord.Color.blue()
            )
            
            async def handle_selection(interaction: discord.Interaction, selected_event_id: str):
                """Handle bet selection from dropdown"""
                async with aiohttp.ClientSession() as session:
                    status, response = await make_api_request(
                        session, 'GET', f"{BET_API_URL}/bet/event/{selected_event_id}"
                    )
                    
                    if status == 200:
                        event = response.get('event', {})
                        
                        detail_embed = discord.Embed(
                            title=f"🎰 {event['title']}",
                            description=event.get('description', ''),
                            color=discord.Color.blue()
                        )
                        
                        detail_embed.add_field(name="🅰️ Opção 1", value=event.get('option1', 'Opção 1'), inline=True)
                        detail_embed.add_field(name="🅱️ Opção 2", value=event.get('option2', 'Opção 2'), inline=True)
                        detail_embed.add_field(name="Pool Total", value=f"{event.get('totalBetAmount', 0):,} moedas", inline=True)
                        
                        view = BetEventView(selected_event_id, event, on_bet_callback=handle_place_bet)
                        
                        await interaction.response.send_message(embed=detail_embed, view=view, ephemeral=True)
            
            view = BetSelectionView(active_events, on_select_callback=handle_selection)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @bot.tree.command(name="evento_admin", description="Gerenciar evento com interface de admin (Admin)")
    @app_commands.describe(event_id="ID do evento")
    async def evento_admin(interaction: discord.Interaction, event_id: str):
        """Manage event with admin UI"""
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem gerenciar eventos.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Evento Não Encontrado",
                    description=f"Não foi possível encontrar o evento com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            event = response.get('event', {})
            
            embed = discord.Embed(
                title=f"⚙️ Gerenciar: {event['title']}",
                description=event.get('description', ''),
                color=discord.Color.gold()
            )
            
            embed.add_field(name="ID", value=f"`{event_id}`", inline=True)
            embed.add_field(name="Pool Total", value=f"{event.get('totalBetAmount', 0):,} moedas", inline=True)
            embed.add_field(name="🅰️ Opção 1", value=event.get('option1', 'Opção 1'), inline=True)
            embed.add_field(name="🅱️ Opção 2", value=event.get('option2', 'Opção 2'), inline=True)
            
            async def handle_finalize(interaction: discord.Interaction, event_id: str, winning_choice: int):
                """Handle event finalization"""
                await interaction.response.defer()
                
                async with aiohttp.ClientSession() as session:
                    finalize_data = {
                        "betEventId": event_id,
                        "winningOption": winning_choice
                    }
                    
                    status, response = await make_api_request(
                        session, 'POST', f"{BET_API_URL}/bet/finalize", finalize_data
                    )
                    
                    if status == 200:
                        embed = discord.Embed(
                            title="🏁 Evento Finalizado!",
                            description=f"Opção {winning_choice} foi declarada vencedora!",
                            color=discord.Color.green()
                        )
                        await interaction.followup.send(embed=embed)
                    else:
                        error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                        embed = discord.Embed(
                            title="❌ Erro ao Finalizar",
                            description=error_msg,
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(embed=embed)
            
            async def handle_cancel(interaction: discord.Interaction, event_id: str):
                """Handle event cancellation"""
                await interaction.response.defer()
                
                async with aiohttp.ClientSession() as session:
                    status, response = await make_api_request(
                        session, 'DELETE', f"{BET_API_URL}/bet/event/{event_id}"
                    )
                    
                    if status == 200:
                        embed = discord.Embed(
                            title="❌ Evento Cancelado",
                            description="O evento foi cancelado e todos foram reembolsados.",
                            color=discord.Color.orange()
                        )
                        await interaction.followup.send(embed=embed)
                    else:
                        error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                        embed = discord.Embed(
                            title="❌ Erro ao Cancelar",
                            description=error_msg,
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(embed=embed)
            
            view = AdminActionsView(event_id, on_finalize=handle_finalize, on_cancel=handle_cancel)
            await interaction.followup.send(embed=embed, view=view)


async def handle_place_bet(interaction: discord.Interaction, event_id: str, choice: int, amount: int):
    """Shared callback for placing bets"""
    await interaction.response.defer(ephemeral=True)
    
    discord_id = str(interaction.user.id)
    user_data = await get_or_create_user(discord_id, interaction.user.display_name)
    
    async with aiohttp.ClientSession() as session:
        bet_data = {
            "userId": user_data['id'],
            "betEventId": event_id,
            "chosenOption": choice,
            "amount": amount
        }
        
        status, response = await make_api_request(
            session, 'POST', f"{BET_API_URL}/bet/place", bet_data
        )
        
        if status == 200:
            embed = discord.Embed(
                title="✅ Aposta Realizada com Sucesso!",
                description=f"Você apostou **{amount:,} moedas** na opção {choice}",
                color=discord.Color.green()
            )
        elif status == 400:
            error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
            embed = discord.Embed(
                title="❌ Erro na Aposta",
                description=error_msg,
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ Falha na Aposta",
                description="Falha ao realizar a aposta. Tente novamente mais tarde.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed, ephemeral=True)
