# pyrogram imports
from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant

# extra imports
from config import Config
from helper.database import digital_botz
import datetime 

# Multiple Force Subscription Channels
FORCE_SUB_CHANNELS = [
    -1001802883067,  # Replace with your first channel ID
    -1001788629657,  # Replace with your second channel ID
    Config.FORCE_SUB_3   # Replace with your third channel ID
]

async def not_subscribed(_, client, message):
    await digital_botz.add_user(client, message)
    
    if not FORCE_SUB_CHANNELS:
        return False  # Agar koi channel nahi diya gaya hai to check na kare

    for channel_id in FORCE_SUB_CHANNELS:
        try:
            user = await client.get_chat_member(channel_id, message.from_user.id)
            if user.status not in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                return True
        except UserNotParticipant:
            return True
        except Exception as e:
            print(f"Error checking subscription: {e}")
    
    return False  # Agar sab channels joined hain to False return kare

async def handle_banned_user_status(bot, message):
    await digital_botz.add_user(bot, message) 
    user_id = message.from_user.id
    ban_status = await digital_botz.get_ban_status(user_id)
    if ban_status.get("is_banned", False):
        if ( datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])
        ).days > ban_status["ban_duration"]:
            await digital_botz.remove_ban(user_id)
        else:
            return await message.reply_text("Sorry Sir, 😔 You are Banned!.. Please Contact - @DigitalBotz") 
    await message.continue_propagation()
    
@Client.on_message(filters.private)
async def _(bot, message):
    await handle_banned_user_status(bot, message)
    
@Client.on_message(filters.private & filters.create(not_subscribed))
async def force_sub(client, message):
    join_buttons = []
    
    for idx, channel_id in enumerate(FORCE_SUB_CHANNELS, start=1):
        channel_link = f"https://t.me/{channel_id}"
        join_buttons.append([InlineKeyboardButton(text=f"📢 Join Channel {idx} 📢", url=channel_link)])

    text = "**Sᴏʀʀy Dᴜᴅᴇ, Yᴏᴜ'ʀᴇ Nᴏᴛ Jᴏɪɴᴇᴅ Aʟʟ Rᴇǫᴜɪʀᴇᴅ Cʜᴀɴɴᴇʟꜱ 😐. Pʟᴇᴀꜱᴇ Jᴏɪɴ Tʜᴇ ᴍ ᴀʟʟ Tᴏ Cᴏɴᴛɪɴᴜᴇ**"

    return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(join_buttons))
