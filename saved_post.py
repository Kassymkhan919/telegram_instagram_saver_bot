from playwright.sync_api import sync_playwright
import csv
import time
import os
import requests

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your bot token
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'  # Replace with your chat ID

def send_telegram_message(message):
    """Send message through Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_instagram_saved_posts():
    send_telegram_message("🤖 Starting Instagram saved posts scraper...")
    with sync_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to Instagram and login (you'll need to handle login separately)
        print("Navigating to Instagram...")
        page.goto('https://www.instagram.com/')
        
        # Wait for user to login manually (you may want to implement proper login automation)
        print("Waiting for login page elements...")
        # Wait for login page elements
        page.wait_for_selector('input[name="username"]')
        page.wait_for_selector('input[name="password"]')

        print("Filling in credentials...")
        # Fill in credentials
        page.fill('input[name="username"]', 'caspiankas')  # Replace with your username
        page.fill('input[name="password"]', '!rfE1Rj#R&7j9vw')  # Replace with your password

        # Click login button
        print("Clicking login button...")
        page.click('button[type="submit"]')

        # Wait for login to complete and home page to load
        print("Waiting for login to complete...")
        page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
        
        print("Waiting additional time for manual login verification if needed...")
        page.wait_for_timeout(20000)  # 20 seconds to login manually

        send_telegram_message("✅ Successfully logged in to Instagram")

        # Navigate to saved posts
        print("Navigating to saved posts page...")
        page.goto('https://www.instagram.com/caspiankas/saved/all-posts')
        page.wait_for_load_state('networkidle')

        # Scroll and collect saved posts
        print("Starting to collect saved posts...")
        saved_posts = []
        last_height = page.evaluate('document.body.scrollHeight')
         
        while True:
            # Get all post links on current view
            posts = page.query_selector_all('article a')
            print(f"Found {len(posts)} posts in current view")
            for post in posts:
                post_url = post.get_attribute('href')
                if post_url and f"https://www.instagram.com{post_url}" not in saved_posts:
                    saved_posts.append(f"https://www.instagram.com{post_url}")
                    print(f"Added new post: https://www.instagram.com{post_url}")
                    
            # Scroll down
            print("Scrolling down...")
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)  # Wait for new content to load

            # Check if we've reached the bottom
            new_height = page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                print("Reached bottom of page")
                break
            last_height = new_height
            print(f"Current number of saved posts: {len(saved_posts)}")

        print("Closing browser...")
        browser.close()
        send_telegram_message(f"✅ Script completed. Total posts collected: {len(saved_posts)}")
        return saved_posts

# Example usage
print("Starting script execution...")
saved_posts = get_instagram_saved_posts()
print("Printing all collected posts:")
# for post in saved_posts:
#     print(post)



def save_post_details_to_file(saved_posts, output_file=os.path.join(os.path.expanduser("~"), "Downloads", "instagram_saved_posts.csv")):
    """
    Visit each saved post URL and extract description, saving results to CSV file
    """

    send_telegram_message(f"📥 Starting to collect details for {len(saved_posts)} posts...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Set up CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Description'])
            
            # Visit each post
            for post_url in saved_posts:
                try:
                    print(f"Visiting {post_url}")
                    page.goto(post_url)
                    page.wait_for_load_state('networkidle')
                    time.sleep(2)  # Additional wait to ensure content loads
                    
                    # Try to get description - Instagram usually puts it in an h1 tag
                    description = ""
                    desc_elem = page.query_selector('h1')
                    if desc_elem:
                        description = desc_elem.inner_text()
                    
                    # Write to CSV
                    writer.writerow([post_url, description])
                    print(f"Saved details for {post_url}")
                    
                except Exception as e:
                    print(f"Error processing {post_url}: {str(e)}")
                    writer.writerow([post_url, "Error processing post"])
                    
                time.sleep(1)  # Prevent too many rapid requests
        
        browser.close()
    
    send_telegram_message(f"✅ Completed! Results saved to {output_file}")

# Call the function with collected posts
save_post_details_to_file(saved_posts)


