"""
Enhanced Client Commands with UI Components
"""
from discord import app_commands
import discord
import aiohttp
from tools.utils import make_api_request
from tools.constants import CLIENT_API_URL
from ui.modals import UserRegistrationModal
from ui.views import ConfirmationView
import logging

logger = logging.getLogger(__name__)


def client_commands(bot):
    """Register client commands with UI enhancements"""
    
    @bot.tree.command(name="registrar", description="Registrar-se no sistema usando interface modal")
    async def registrar(interaction: discord.Interaction):
        """Register using a modal interface"""
        
        async def handle_registration(interaction: discord.Interaction, username: str, bio: str = None):
            """Handle user registration from modal"""
            await interaction.response.defer(ephemeral=True)
            
            discord_id = str(interaction.user.id)
            
            async with aiohttp.ClientSession() as session:
                user_data = {
                    "discordId": discord_id,
                    "username": username
                }
                
                status, response = await make_api_request(
                    session, 'POST', f"{CLIENT_API_URL}/client/register", user_data
                )
                
                if status == 200:
                    embed = discord.Embed(
                        title="✅ Registro Completo!",
                        description=f"Bem-vindo ao Buteco Bot, **{username}**!",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Discord ID", value=f"`{discord_id}`", inline=True)
                    embed.add_field(name="Username", value=username, inline=True)
                    
                    if bio:
                        embed.add_field(name="Bio", value=bio, inline=False)
                    
                    embed.set_footer(text="Use /ajuda para ver os comandos disponíveis")
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                elif status == 400:
                    error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                    embed = discord.Embed(
                        title="❌ Erro no Registro",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="❌ Falha no Registro",
                        description="Não foi possível completar o registro. Tente novamente mais tarde.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Show registration modal
        modal = UserRegistrationModal(callback=handle_registration)
        await interaction.response.send_modal(modal)
    
    @bot.tree.command(name="deletar_conta", description="Deletar sua conta com confirmação")
    async def deletar_conta(interaction: discord.Interaction):
        """Delete account with confirmation dialog"""
        
        discord_id = str(interaction.user.id)
        
        async def on_confirm(confirm_interaction: discord.Interaction):
            """Handle account deletion confirmation"""
            await confirm_interaction.response.defer(ephemeral=True)
            
            async with aiohttp.ClientSession() as session:
                status, response = await make_api_request(
                    session, 'DELETE', f"{CLIENT_API_URL}/client/{discord_id}"
                )
                
                if status == 200:
                    embed = discord.Embed(
                        title="✅ Conta Deletada",
                        description="Sua conta foi deletada com sucesso. Até logo!",
                        color=discord.Color.green()
                    )
                    await confirm_interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                    embed = discord.Embed(
                        title="❌ Erro ao Deletar Conta",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    await confirm_interaction.followup.send(embed=embed, ephemeral=True)
        
        async def on_cancel(cancel_interaction: discord.Interaction):
            """Handle cancellation"""
            embed = discord.Embed(
                title="❌ Cancelado",
                description="A exclusão da conta foi cancelada.",
                color=discord.Color.blue()
            )
            await cancel_interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Show confirmation dialog
        embed = discord.Embed(
            title="⚠️ Confirmar Exclusão de Conta",
            description="**ATENÇÃO:** Esta ação é irreversível!\n\nVocê perderá:\n• Todas as suas moedas\n• Histórico de apostas\n• Estatísticas\n\nTem certeza que deseja continuar?",
            color=discord.Color.orange()
        )
        
        view = ConfirmationView(on_confirm=on_confirm, on_cancel=on_cancel)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def registrar_ui(interaction: discord.Interaction):
        """Register using a modal interface"""
        
        async def handle_registration(interaction: discord.Interaction, username: str, bio: str = None):
            """Handle user registration from modal"""
            await interaction.response.defer(ephemeral=True)
            
            discord_id = str(interaction.user.id)
            
            async with aiohttp.ClientSession() as session:
                user_data = {
                    "discordId": discord_id,
                    "username": username
                }
                
                status, response = await make_api_request(
                    session, 'POST', f"{CLIENT_API_URL}/client/register", user_data
                )
                
                if status == 200:
                    embed = discord.Embed(
                        title="✅ Registro Completo!",
                        description=f"Bem-vindo ao Buteco Bot, **{username}**!",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Discord ID", value=f"`{discord_id}`", inline=True)
                    embed.add_field(name="Username", value=username, inline=True)
                    
                    if bio:
                        embed.add_field(name="Bio", value=bio, inline=False)
                    
                    embed.set_footer(text="Use /ajuda para ver os comandos disponíveis")
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                elif status == 400:
                    error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                    embed = discord.Embed(
                        title="❌ Erro no Registro",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="❌ Falha no Registro",
                        description="Não foi possível completar o registro. Tente novamente mais tarde.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
    #         await confirm_interaction.response.defer(ephemeral=True)
            
    #         async with aiohttp.ClientSession() as session:
    #             status, response = await make_api_request(
    #                 session, 'DELETE', f"{CLIENT_API_URL}/client/{discord_id}"
    #             )
                
    #             if status == 200:
    #                 embed = discord.Embed(
    #                     title="✅ Conta Deletada",
    #                     description="Sua conta foi deletada com sucesso. Até logo!",
    #                     color=discord.Color.green()
    #                 )
    #                 await confirm_interaction.followup.send(embed=embed, ephemeral=True)
    #             else:
    #                 error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
    #                 embed = discord.Embed(
    #                     title="❌ Erro ao Deletar Conta",
    #                     description=error_msg,
    #                     color=discord.Color.red()
    #                 )
    #                 await confirm_interaction.followup.send(embed=embed, ephemeral=True)
        
    #     async def on_cancel(cancel_interaction: discord.Interaction):
    #         """Handle cancellation"""
    #         embed = discord.Embed(
    #             title="❌ Cancelado",
    #             description="A exclusão da conta foi cancelada.",
    #             color=discord.Color.blue()
    #         )
    #         await cancel_interaction.response.send_message(embed=embed, ephemeral=True)
        
    #     # Show confirmation dialog
    #     embed = discord.Embed(
    #         title="⚠️ Confirmar Exclusão de Conta",
    #         description="**ATENÇÃO:** Esta ação é irreversível!\n\nVocê perderá:\n• Todas as suas moedas\n• Histórico de apostas\n• Estatísticas\n\nTem certeza que deseja continuar?",
    #         color=discord.Color.orange()
    #     )
        
    #     view = ConfirmationView(on_confirm=on_confirm, on_cancel=on_cancel)
    #     await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
