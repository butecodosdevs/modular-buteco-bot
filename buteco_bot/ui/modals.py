"""
Discord Modal Components
Provides reusable modal forms following Discord UI patterns
"""

import discord
from typing import Optional, Callable, Any
import logging
import os

logger = logging.getLogger(__name__)


class BetCreationModal(discord.ui.Modal, title="🎰 Criar Nova Aposta"):
    """Modal for creating a new bet event"""

    bet_title = discord.ui.TextInput(
        label="Título da Aposta",
        placeholder="Ex: Quem vai ganhar o jogo?",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )

    description = discord.ui.TextInput(
        label="Descrição",
        placeholder="Descreva os detalhes da aposta...",
        required=True,
        max_length=500,
        style=discord.TextStyle.paragraph,
    )

    option1 = discord.ui.TextInput(
        label="Opção 1",
        placeholder="Ex: Time A",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )

    option2 = discord.ui.TextInput(
        label="Opção 2",
        placeholder="Ex: Time B",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )

    def __init__(self, callback: Optional[Callable] = None):
        super().__init__()
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        if self.callback:
            await self.callback(
                interaction,
                title=self.bet_title.value,
                description=self.description.value,
                option1=self.option1.value,
                option2=self.option2.value,
            )
        else:
            await interaction.response.send_message(
                "✅ Aposta criada com sucesso!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in BetCreationModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao processar sua aposta. Tente novamente.",
            ephemeral=True,
        )


class PlaceBetModal(discord.ui.Modal, title="💰 Fazer Aposta"):
    """Modal for placing a bet"""

    amount = discord.ui.TextInput(
        label="Quantidade de Moedas",
        placeholder="Ex: 100",
        required=True,
        max_length=10,
        style=discord.TextStyle.short,
    )

    def __init__(
        self,
        event_id: str,
        choice: int,
        event_title: str,
        option_name: str,
        callback: Optional[Callable] = None,
    ):
        super().__init__(title=f"💰 Apostar em {option_name}")
        self.event_id = event_id
        self.choice = choice
        self.event_title = event_title
        self.option_name = option_name
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle bet placement"""
        try:
            amount = int(self.amount.value)
            if amount <= 0:
                await interaction.response.send_message(
                    "❌ O valor da aposta deve ser positivo!", ephemeral=True
                )
                return

            if self.callback:
                await self.callback(
                    interaction,
                    event_id=self.event_id,
                    choice=self.choice,
                    amount=amount,
                )
        except ValueError:
            await interaction.response.send_message(
                "❌ Por favor, insira um número válido!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in PlaceBetModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao processar sua aposta. Tente novamente.",
            ephemeral=True,
        )


class UserRegistrationModal(discord.ui.Modal, title="📝 Registro de Usuário"):
    """Modal for user registration"""

    username = discord.ui.TextInput(
        label="Nome de Usuário",
        placeholder="Como você quer ser chamado?",
        required=True,
        max_length=50,
        style=discord.TextStyle.short,
    )

    bio = discord.ui.TextInput(
        label="Bio (Opcional)",
        placeholder="Conte um pouco sobre você...",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, callback: Optional[Callable] = None):
        super().__init__()
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle user registration"""
        if self.callback:
            await self.callback(
                interaction,
                username=self.username.value,
                bio=self.bio.value if self.bio.value else None,
            )
        else:
            await interaction.response.send_message(
                f"✅ Bem-vindo, {self.username.value}!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in UserRegistrationModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro durante o registro. Tente novamente.", ephemeral=True
        )


class FeedbackModal(discord.ui.Modal, title="💬 Enviar Feedback"):
    """Modal for collecting user feedback"""

    subject = discord.ui.TextInput(
        label="Assunto",
        placeholder="Sobre o que é seu feedback?",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )

    message = discord.ui.TextInput(
        label="Mensagem",
        placeholder="Compartilhe seus pensamentos...",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, callback: Optional[Callable] = None):
        super().__init__()
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle feedback submission"""
        if self.callback:
            await self.callback(
                interaction, subject=self.subject.value, message=self.message.value
            )
        else:
            await interaction.response.send_message(
                "✅ Obrigado pelo seu feedback!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in FeedbackModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao enviar seu feedback. Tente novamente.",
            ephemeral=True,
        )


class EditBetModal(discord.ui.Modal, title="✏️ Editar Aposta"):
    """Modal for editing bet details"""

    new_title = discord.ui.TextInput(
        label="Novo Título",
        placeholder="Digite o novo título...",
        required=False,
        max_length=100,
        style=discord.TextStyle.short,
    )

    new_description = discord.ui.TextInput(
        label="Nova Descrição",
        placeholder="Digite a nova descrição...",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph,
    )

    def __init__(
        self,
        event_id: str,
        current_title: str,
        current_description: str,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.event_id = event_id
        self.new_title.default = current_title
        self.new_description.default = current_description
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle bet edit"""
        if self.callback:
            await self.callback(
                interaction,
                event_id=self.event_id,
                title=self.new_title.value if self.new_title.value else None,
                description=self.new_description.value
                if self.new_description.value
                else None,
            )
        else:
            await interaction.response.send_message(
                "✅ Aposta atualizada com sucesso!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in EditBetModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao editar a aposta. Tente novamente.", ephemeral=True
        )


class TransferCoinsModal(discord.ui.Modal, title="💸 Transferir Moedas"):
    """Modal for transferring coins to another user"""

    amount = discord.ui.TextInput(
        label="Quantidade de Moedas",
        placeholder="Ex: 100",
        required=True,
        max_length=10,
        style=discord.TextStyle.short,
    )

    description = discord.ui.TextInput(
        label="Descrição (Opcional)",
        placeholder="Motivo da transferência...",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, recipient: discord.Member, callback: Optional[Callable] = None):
        super().__init__()
        self.recipient = recipient
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle transfer submission"""
        try:
            amount_value = int(self.amount.value)
            if amount_value <= 0:
                await interaction.response.send_message(
                    "❌ O valor deve ser positivo!", ephemeral=True
                )
                return

            if self.callback:
                await self.callback(
                    interaction,
                    recipient=self.recipient,
                    amount=amount_value,
                    description=self.description.value
                    if self.description.value
                    else "Transferência de moedas",
                )
        except ValueError:
            await interaction.response.send_message(
                "❌ Por favor, insira um número válido!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in TransferCoinsModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao processar a transferência. Tente novamente.",
            ephemeral=True,
        )


class AIPromptModal(discord.ui.Modal, title="🤖 Consultar IA"):
    """Modal for AI prompt input"""

    prompt = discord.ui.TextInput(
        label="Sua Pergunta",
        placeholder="Digite sua pergunta ou comando para a IA...",
        required=True,
        max_length=2000,
        style=discord.TextStyle.paragraph,
    )

    system_prompt = discord.ui.TextInput(
        label="Orientação do Sistema (Opcional)",
        placeholder="Ex: Responda como um professor de matemática...",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph,
    )

    def __init__(
        self, provider: Optional[str] = None, callback: Optional[Callable] = None
    ):
        super().__init__()
        self.provider = provider
        self.callback = callback

        # Show cost in title
        cost = int(os.getenv("AI_USAGE_COST", 100))
        self.title = f"🤖 Consultar IA (Custo: {cost} moedas)"

    async def on_submit(self, interaction: discord.Interaction):
        """Handle AI prompt submission"""
        if self.callback:
            await self.callback(
                interaction,
                prompt=self.prompt.value,
                provider=self.provider,
                system_prompt=self.system_prompt.value
                if self.system_prompt.value
                else None,
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in AIPromptModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao processar sua consulta. Tente novamente.",
            ephemeral=True,
        )


class PoliticalPositionModal(discord.ui.Modal, title="🗳️ Definir Posição Política"):
    """Modal for setting political position"""

    x_coord = discord.ui.TextInput(
        label="Coordenada X (Esquerda ← → Direita)",
        placeholder="Digite um valor entre -10 e 10",
        required=True,
        max_length=6,
        style=discord.TextStyle.short,
    )

    y_coord = discord.ui.TextInput(
        label="Coordenada Y (Libertário ↓ ↑ Autoritário)",
        placeholder="Digite um valor entre -10 e 10",
        required=True,
        max_length=6,
        style=discord.TextStyle.short,
    )

    def __init__(self, user: discord.User, callback: Optional[Callable] = None):
        super().__init__()
        self.user = user
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        """Handle political position submission"""
        try:
            x = float(self.x_coord.value)
            y = float(self.y_coord.value)

            if x < -10 or x > 10 or y < -10 or y > 10:
                await interaction.response.send_message(
                    "❌ As coordenadas devem estar entre -10 e 10!", ephemeral=True
                )
                return

            if self.callback:
                await self.callback(interaction, user=self.user, x=x, y=y)
        except ValueError:
            await interaction.response.send_message(
                "❌ Por favor, insira números válidos!", ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle errors during modal submission"""
        logger.error(f"Error in PoliticalPositionModal: {error}")
        await interaction.response.send_message(
            "❌ Ocorreu um erro ao definir a posição política. Tente novamente.",
            ephemeral=True,
        )
