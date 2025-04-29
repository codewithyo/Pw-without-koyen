import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, ChatWriteForbidden, PeerIdInvalid, UserDeactivated
from config import api_id, api_hash, bot_token
from main import get_all_users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Client(
    "broadcast_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Track broadcast progress
broadcast_ids = {}

@bot.on_message(filters.command("broadcast") & filters.user([7029363479]))  # Replace with your user ID
async def broadcast_handler(bot, message):
    """
    Handler for the broadcast command
    Usage: /broadcast [message]
    """
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:**\n/broadcast [message]\n\n"
            "**Example:**\n/broadcast Hello everyone! This is a test broadcast."
        )
        return

    # Get broadcast message
    broadcast_msg = message.text.split("/broadcast ", 1)[1]
    
    # Get all users
    users = get_all_users()
    if not users:
        await message.reply_text("**No users found in database!**")
        return
    
    total_users = len(users)
    done = 0
    blocked = 0
    failed = 0
    success = 0
    
    # Send initial status message
    progress = await message.reply_text(
        f"**Broadcast Started! 📣**\n\n"
        f"**Total Users:** {total_users}\n"
        f"**Completed:** {done} / {total_users}\n"
        f"**Success:** {success}\n"
        f"**Failed:** {failed}\n"
        f"**Blocked:** {blocked}"
    )
    
    # Start broadcast
    start_time = asyncio.get_event_loop().time()
    
    async def send_msg(user_id):
        nonlocal done, blocked, failed, success
        try:
            await bot.send_message(user_id, broadcast_msg)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await bot.send_message(user_id, broadcast_msg)
            success += 1
        except UserIsBlocked:
            blocked += 1
        except (ChatWriteForbidden, PeerIdInvalid, UserDeactivated):
            failed += 1
        except Exception as e:
            logger.error(f"Error in broadcast to {user_id}: {str(e)}")
            failed += 1
        done += 1
        
        if done % 20 == 0:
            try:
                await progress.edit_text(
                    f"**Broadcast in Progress! 📣**\n\n"
                    f"**Total Users:** {total_users}\n"
                    f"**Completed:** {done} / {total_users}\n"
                    f"**Success:** {success}\n"
                    f"**Failed:** {failed}\n"
                    f"**Blocked:** {blocked}"
                )
            except Exception:
                pass
    
    # Process users in chunks of 20
    tasks = []
    for i in range(0, len(users), 20):
        chunk = users[i:i + 20]
        for user_id in chunk:
            tasks.append(send_msg(user_id))
        await asyncio.gather(*tasks)
        tasks.clear()
        await asyncio.sleep(2)  # Sleep between chunks to avoid flood
    
    # Calculate time taken
    end_time = asyncio.get_event_loop().time()
    time_taken = round(end_time - start_time)
    minutes = time_taken // 60
    seconds = time_taken % 60
    
    # Send final status message
    await progress.edit_text(
        f"**Broadcast Completed! ✅**\n\n"
        f"**Total Users:** {total_users}\n"
        f"**Completed:** {done} / {total_users}\n"
        f"**Success:** {success}\n"
        f"**Failed:** {failed}\n"
        f"**Blocked:** {blocked}\n\n"
        f"**Time Taken:** {minutes}m {seconds}s"
    )

# Command to get user count
@bot.on_message(filters.command("stats") & filters.user([7029363479]))  # Replace with your user ID
async def stats_handler(bot, message):
    """Handler for getting bot statistics"""
    users = get_all_users()
    total_users = len(users)
    
    await message.reply_text(
        f"**Bot Statistics 📊**\n\n"
        f"**Total Users:** {total_users}"
    )

if __name__ == "__main__":
    logger.info("Starting Broadcast Bot...")
    bot.run() 