from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
import requests
from instaloader import Instaloader, Post
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Initialize Instaloader
L = Instaloader()

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Send me an Instagram post link and I\'ll download it for you!')

def extract_shortcode(url):
    """Extract Instagram post shortcode from URL"""
    pattern = r'instagram.com/p/([^/?]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def download_and_send_post(update, context):
    """Download Instagram post and send it to user"""
    url = update.message.text
    shortcode = extract_shortcode(url)
    
    if not shortcode:
        update.message.reply_text('Please send a valid Instagram post URL')
        return
    
    try:
        # Download post
        post = Post.from_shortcode(L.context, shortcode)
        
        # Send description if available
        if post.caption:
            update.message.reply_text(f"Caption:\n{post.caption}")
        
        # Download and send media
        temp_dir = "temp_downloads"
        os.makedirs(temp_dir, exist_ok=True)
        
        L.download_post(post, target=temp_dir)
        
        # Send media files
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if file.endswith('.jpg') or file.endswith('.jpeg'):
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(file_path, 'rb'))
            elif file.endswith('.mp4'):
                context.bot.send_video(chat_id=update.effective_chat.id, video=open(file_path, 'rb'))
            
            # Clean up
            os.remove(file_path)
        
        os.rmdir(temp_dir)
        
    except Exception as e:
        update.message.reply_text(f'Error processing post: {str(e)}')

def main():
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_and_send_post))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
