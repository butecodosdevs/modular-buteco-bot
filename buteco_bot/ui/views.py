"""
Discord View Components
Provides interactive UI elements like buttons, select menus, and persistent views
"""
import discord
from typing import Optional, Callable, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfirmationView(discord.ui.View):
    """Reusable confirmation dialog with Yes/No buttons"""
    
    def __init__(self, timeout: float = 180.0, on_confirm: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        super().__init__(timeout=timeout)
        self.value = None
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
    
    @discord.ui.button(label="✅ Confirmar", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle confirmation"""
        self.value = True
        if self.on_confirm_callback:
            await self.on_confirm_callback(interaction)
        else:
            await interaction.response.send_message("✅ Confirmado!", ephemeral=True)
        self.stop()
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle cancellation"""
        self.value = False
        if self.on_cancel_callback:
            await self.on_cancel_callback(interaction)
        else:
            await interaction.response.send_message("❌ Cancelado!", ephemeral=True)
        self.stop()


class BetEventView(discord.ui.View):
    """Interactive view for bet events with action buttons"""
    
    def __init__(self, event_id: str, event_data: Dict[str, Any], on_bet_callback: Optional[Callable] = None, timeout: float = None):
        super().__init__(timeout=timeout)
        self.event_id = event_id
        self.event_data = event_data
        self.on_bet_callback = on_bet_callback
    
    @discord.ui.button(label="🅰️ Apostar Opção 1", style=discord.ButtonStyle.primary, custom_id="bet_option_1")
    async def bet_option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle bet on option 1"""
        from .modals import PlaceBetModal
        
        modal = PlaceBetModal(
            event_id=self.event_id,
            choice=1,
            event_title=self.event_data.get('title', 'Aposta'),
            option_name=self.event_data.get('option1', 'Opção 1'),
            callback=self.on_bet_callback
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🅱️ Apostar Opção 2", style=discord.ButtonStyle.primary, custom_id="bet_option_2")
    async def bet_option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle bet on option 2"""
        from .modals import PlaceBetModal
        
        modal = PlaceBetModal(
            event_id=self.event_id,
            choice=2,
            event_title=self.event_data.get('title', 'Aposta'),
            option_name=self.event_data.get('option2', 'Opção 2'),
            callback=self.on_bet_callback
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="ℹ️ Ver Detalhes", style=discord.ButtonStyle.secondary, custom_id="bet_info")
    async def view_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed bet information"""
        embed = discord.Embed(
            title=f"🎰 {self.event_data.get('title', 'Aposta')}",
            description=self.event_data.get('description', ''),
            color=discord.Color.blue()
        )
        
        embed.add_field(name="ID", value=f"`{self.event_id}`", inline=True)
        embed.add_field(name="Pool Total", value=f"{self.event_data.get('totalBetAmount', 0):,} moedas", inline=True)
        
        option1_amount = self.event_data.get('option1BetAmount', 0)
        option2_amount = self.event_data.get('option2BetAmount', 0)
        total_amount = self.event_data.get('totalBetAmount', 0)
        
        option1_percentage = (option1_amount / total_amount * 100) if total_amount > 0 else 0
        option2_percentage = (option2_amount / total_amount * 100) if total_amount > 0 else 0
        
        embed.add_field(
            name=f"🅰️ {self.event_data.get('option1', 'Opção 1')}",
            value=f"{option1_amount:,} moedas ({option1_percentage:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name=f"🅱️ {self.event_data.get('option2', 'Opção 2')}",
            value=f"{option2_amount:,} moedas ({option2_percentage:.1f}%)",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class BetSelectionDropdown(discord.ui.Select):
    """Dropdown menu for selecting bet events"""
    
    def __init__(self, events: List[Dict[str, Any]], on_select_callback: Optional[Callable] = None):
        options = []
        for event in events[:25]:  # Discord limit is 25 options
            options.append(
                discord.SelectOption(
                    label=event.get('title', 'Aposta')[:100],
                    description=f"Pool: {event.get('totalBetAmount', 0):,} moedas"[:100],
                    value=event.get('id', ''),
                    emoji="🎰"
                )
            )
        
        super().__init__(
            placeholder="Selecione uma aposta...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.on_select_callback = on_select_callback
    
    async def callback(self, interaction: discord.Interaction):
        """Handle selection"""
        selected_event_id = self.values[0]
        if self.on_select_callback:
            await self.on_select_callback(interaction, selected_event_id)
        else:
            await interaction.response.send_message(
                f"Você selecionou a aposta: `{selected_event_id}`",
                ephemeral=True
            )


class BetSelectionView(discord.ui.View):
    """View containing bet selection dropdown"""
    
    def __init__(self, events: List[Dict[str, Any]], on_select_callback: Optional[Callable] = None, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.add_item(BetSelectionDropdown(events, on_select_callback))


class PaginationView(discord.ui.View):
    """Reusable pagination view for navigating through pages"""
    
    def __init__(self, pages: List[discord.Embed], timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.pages) - 1
        self.last_page.disabled = self.current_page == len(self.pages) - 1
    
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to first page"""
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page"""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page"""
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to last page"""
        self.current_page = len(self.pages) - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="🗑️", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Delete the message"""
        await interaction.message.delete()
        self.stop()


class AdminActionsView(discord.ui.View):
    """Admin action buttons for bet management"""
    
    def __init__(self, event_id: str, on_finalize: Optional[Callable] = None, on_cancel: Optional[Callable] = None, timeout: float = None):
        super().__init__(timeout=timeout)
        self.event_id = event_id
        self.on_finalize_callback = on_finalize
        self.on_cancel_callback = on_cancel
    
    @discord.ui.button(label="🏁 Finalizar (Opção 1)", style=discord.ButtonStyle.success, custom_id="finalize_1")
    async def finalize_option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Finalize bet with option 1 as winner"""
        if self.on_finalize_callback:
            await self.on_finalize_callback(interaction, self.event_id, 1)
        else:
            await interaction.response.send_message("✅ Aposta finalizada com Opção 1 vencedora!", ephemeral=True)
    
    @discord.ui.button(label="🏁 Finalizar (Opção 2)", style=discord.ButtonStyle.success, custom_id="finalize_2")
    async def finalize_option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Finalize bet with option 2 as winner"""
        if self.on_finalize_callback:
            await self.on_finalize_callback(interaction, self.event_id, 2)
        else:
            await interaction.response.send_message("✅ Aposta finalizada com Opção 2 vencedora!", ephemeral=True)
    
    @discord.ui.button(label="❌ Cancelar Aposta", style=discord.ButtonStyle.danger, custom_id="cancel_bet")
    async def cancel_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the bet"""
        if self.on_cancel_callback:
            await self.on_cancel_callback(interaction, self.event_id)
        else:
            await interaction.response.send_message("❌ Aposta cancelada!", ephemeral=True)


class QuickBetView(discord.ui.View):
    """Quick bet buttons with predefined amounts"""
    
    def __init__(self, event_id: str, choice: int, on_bet_callback: Optional[Callable] = None, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.event_id = event_id
        self.choice = choice
        self.on_bet_callback = on_bet_callback
    
    @discord.ui.button(label="💰 10", style=discord.ButtonStyle.secondary)
    async def bet_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick bet 10 coins"""
        if self.on_bet_callback:
            await self.on_bet_callback(interaction, self.event_id, self.choice, 10)
    
    @discord.ui.button(label="💰 50", style=discord.ButtonStyle.secondary)
    async def bet_50(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick bet 50 coins"""
        if self.on_bet_callback:
            await self.on_bet_callback(interaction, self.event_id, self.choice, 50)
    
    @discord.ui.button(label="💰 100", style=discord.ButtonStyle.primary)
    async def bet_100(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick bet 100 coins"""
        if self.on_bet_callback:
            await self.on_bet_callback(interaction, self.event_id, self.choice, 100)
    
    @discord.ui.button(label="💰 500", style=discord.ButtonStyle.primary)
    async def bet_500(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick bet 500 coins"""
        if self.on_bet_callback:
            await self.on_bet_callback(interaction, self.event_id, self.choice, 500)
    
    @discord.ui.button(label="✏️ Personalizado", style=discord.ButtonStyle.success)
    async def bet_custom(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open modal for custom bet amount"""
        from .modals import PlaceBetModal
        
        modal = PlaceBetModal(
            event_id=self.event_id,
            choice=self.choice,
            event_title="Aposta",
            option_name=f"Opção {self.choice}",
            callback=self.on_bet_callback
        )
        await interaction.response.send_modal(modal)
