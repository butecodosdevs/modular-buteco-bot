# How to Add UI Components to Any Command

This guide shows you how to add modals and views to your existing or new commands.

## Pattern 1: Replace Command Parameters with Modal

### Before (Traditional Command)
```python
@bot.tree.command(name="create_item")
@app_commands.describe(
    name="Item name",
    description="Item description",
    price="Item price"
)
async def create_item(interaction: discord.Interaction, name: str, description: str, price: int):
    # Process the item creation
    await interaction.response.send_message(f"Created {name}!")
```

### After (With Modal)
```python
from ui.modals import discord

class CreateItemModal(discord.ui.Modal, title="Create New Item"):
    name = discord.ui.TextInput(
        label="Item Name",
        placeholder="Enter item name...",
        required=True,
        max_length=100
    )
    
    description = discord.ui.TextInput(
        label="Description",
        placeholder="Describe the item...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    price = discord.ui.TextInput(
        label="Price",
        placeholder="Enter price...",
        required=True,
        max_length=10
    )
    
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            price_value = int(self.price.value)
            if self.callback:
                await self.callback(
                    interaction,
                    name=self.name.value,
                    description=self.description.value,
                    price=price_value
                )
        except ValueError:
            await interaction.response.send_message(
                "❌ Price must be a number!",
                ephemeral=True
            )

@bot.tree.command(name="create_item_ui")
async def create_item_ui(interaction: discord.Interaction):
    """Create item using modal"""
    
    async def handle_creation(interaction, name, description, price):
        await interaction.response.defer(ephemeral=True)
        # Your API call here
        await interaction.followup.send(f"✅ Created {name}!")
    
    modal = CreateItemModal(callback=handle_creation)
    await interaction.response.send_modal(modal)
```

---

## Pattern 2: Add Confirmation Dialog

### Before (Immediate Action)
```python
@bot.tree.command(name="delete_item")
async def delete_item(interaction: discord.Interaction, item_id: str):
    # Immediately deletes - dangerous!
    await delete_from_api(item_id)
    await interaction.response.send_message("Deleted!")
```

### After (With Confirmation)
```python
from ui.views import ConfirmationView

@bot.tree.command(name="delete_item_ui")
async def delete_item_ui(interaction: discord.Interaction, item_id: str):
    """Delete item with confirmation"""
    
    async def on_confirm(confirm_interaction):
        await confirm_interaction.response.defer(ephemeral=True)
        await delete_from_api(item_id)
        await confirm_interaction.followup.send("✅ Deleted!")
    
    async def on_cancel(cancel_interaction):
        await cancel_interaction.response.send_message("❌ Cancelled", ephemeral=True)
    
    view = ConfirmationView(on_confirm=on_confirm, on_cancel=on_cancel)
    await interaction.response.send_message(
        f"⚠️ Delete item `{item_id}`?",
        view=view,
        ephemeral=True
    )
```

---

## Pattern 3: Add Interactive Buttons

### Before (Static Message)
```python
@bot.tree.command(name="show_item")
async def show_item(interaction: discord.Interaction, item_id: str):
    item = await fetch_item(item_id)
    embed = create_item_embed(item)
    await interaction.response.send_message(embed=embed)
```

### After (With Action Buttons)
```python
class ItemActionsView(discord.ui.View):
    def __init__(self, item_id):
        super().__init__(timeout=180)
        self.item_id = item_id
    
    @discord.ui.button(label="✏️ Edit", style=discord.ButtonStyle.primary)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Open edit modal
        modal = EditItemModal(self.item_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Delete", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show confirmation
        view = ConfirmationView(...)
        await interaction.response.send_message("Delete?", view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show stats
        stats = await fetch_stats(self.item_id)
        await interaction.response.send_message(f"Stats: {stats}", ephemeral=True)

@bot.tree.command(name="show_item_ui")
async def show_item_ui(interaction: discord.Interaction, item_id: str):
    item = await fetch_item(item_id)
    embed = create_item_embed(item)
    view = ItemActionsView(item_id)
    await interaction.response.send_message(embed=embed, view=view)
```

---

## Pattern 4: Add Dropdown Selection

### Before (List Command)
```python
@bot.tree.command(name="list_items")
async def list_items(interaction: discord.Interaction):
    items = await fetch_items()
    # Shows static list
    await interaction.response.send_message(f"Items: {items}")
```

### After (With Dropdown)
```python
class ItemSelect(discord.ui.Select):
    def __init__(self, items):
        options = [
            discord.SelectOption(
                label=item['name'],
                description=f"Price: {item['price']}",
                value=item['id'],
                emoji="📦"
            )
            for item in items[:25]  # Discord limit
        ]
        super().__init__(placeholder="Select an item...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        item_id = self.values[0]
        item = await fetch_item(item_id)
        embed = create_item_embed(item)
        view = ItemActionsView(item_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ItemSelectionView(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=180)
        self.add_item(ItemSelect(items))

@bot.tree.command(name="list_items_ui")
async def list_items_ui(interaction: discord.Interaction):
    items = await fetch_items()
    view = ItemSelectionView(items)
    await interaction.response.send_message("Select an item:", view=view, ephemeral=True)
```

---

## Pattern 5: Quick Action Buttons

```python
class QuickActionsView(discord.ui.View):
    def __init__(self, item_id):
        super().__init__(timeout=60)
        self.item_id = item_id
    
    @discord.ui.button(label="👍 Like", style=discord.ButtonStyle.success)
    async def like(self, interaction: discord.Interaction, button: discord.ui.Button):
        await api_like(self.item_id, interaction.user.id)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Liked!", ephemeral=True)
    
    @discord.ui.button(label="⭐ Favorite", style=discord.ButtonStyle.primary)
    async def favorite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await api_favorite(self.item_id, interaction.user.id)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("⭐ Added to favorites!", ephemeral=True)
```

---

## Best Practices

### 1. Always Defer Long Operations
```python
async def on_submit(self, interaction: discord.Interaction):
    # Defer immediately if operation takes > 3 seconds
    await interaction.response.defer(ephemeral=True)
    
    # Do long operation
    result = await long_api_call()
    
    # Follow up
    await interaction.followup.send(f"Done: {result}")
```

### 2. Handle Errors Gracefully
```python
async def on_error(self, interaction: discord.Interaction, error: Exception):
    logger.error(f"Error: {error}")
    await interaction.response.send_message(
        "❌ Something went wrong. Please try again.",
        ephemeral=True
    )
```

### 3. Validate Input
```python
async def on_submit(self, interaction: discord.Interaction):
    try:
        amount = int(self.amount.value)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # Process...
    except ValueError as e:
        await interaction.response.send_message(
            f"❌ Invalid input: {e}",
            ephemeral=True
        )
```

### 4. Use Ephemeral for Personal Data
```python
# Only visible to the user
await interaction.response.send_message(
    "Your personal data...",
    ephemeral=True
)
```

### 5. Disable Buttons After Use
```python
@discord.ui.button(label="One Time")
async def one_time(self, interaction: discord.Interaction, button: discord.ui.Button):
    button.disabled = True
    await interaction.response.edit_message(view=self)
```

---

## Quick Reference

### Show a Modal
```python
modal = MyModal()
await interaction.response.send_modal(modal)
```

### Send with View
```python
view = MyView()
await interaction.response.send_message("Message", view=view)
```

### Defer Response
```python
await interaction.response.defer(ephemeral=True)
# ... do work ...
await interaction.followup.send("Result")
```

### Edit Message
```python
await interaction.response.edit_message(content="New content", view=new_view)
```

---

## See Also

- [Discord UI Guide](file:///c:/Users/gio/.gemini/antigravity/brain/8997dc74-8c1a-4c51-8730-fa49543a6eb0/DISCORD_UI_GUIDE.md) - Complete guide
- [bet_ui.py](file:///c:/Users/gio/Documents/dev/modular-buteco-bot/buteco_bot/commands/bet_ui.py) - Real examples
- [ui/modals.py](file:///c:/Users/gio/Documents/dev/modular-buteco-bot/buteco_bot/ui/modals.py) - Modal components
- [ui/views.py](file:///c:/Users/gio/Documents/dev/modular-buteco-bot/buteco_bot/ui/views.py) - View components
