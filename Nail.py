import ollama
import requests
import json
import os

REMOTE_OLLAMA_HOST = os.getenv("OLLAMA_REMOTE_HOST", "http://192.168.1.15:11434")
os.environ["OLLAMA_HOST"] = REMOTE_OLLAMA_HOST

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL_HERE")

OLLAMA_MODEL = "gemma3:1b"

SIMULATED_GMAIL_CONTENT = [
    {
        "id": "email_001",
        "subject": "Your Order #12345 Confirmed!",
        "sender": "noreply@onlinestore.com",
        "body": "Hi John, your recent order #12345 has been confirmed and will be shipped soon. Items: Laptop, Mouse. Total: $1200. You will receive another email with tracking information.",
    },
    {
        "id": "email_002",
        "subject": "Project Alpha Meeting Rescheduled",
        "sender": "alice@workcorp.com",
        "body": "Hello team, the Project Alpha meeting originally scheduled for Monday has been moved to Wednesday at 10 AM in Conference Room 3. Please update your calendars. Agenda will be sent separately.",
    },
    {
        "id": "email_003",
        "subject": "Exclusive Discount Just For You!",
        "sender": "marketing@coolgadgets.com",
        "body": "Don't miss out on our limited-time offer! Get 20% off all smartphones this week. Use code SAVE20 at checkout. Shop now!",
    },
    {
        "id": "email_004",
        "subject": "New Photo Album from Sarah",
        "sender": "photos@friends.com",
        "body": "Sarah just shared a new photo album with you: 'Summer Vacation 2025'. Click here to view the amazing pictures!",
    },
    {
        "id": "email_005",
        "subject": "Your Account Security Alert",
        "sender": "security@fakebank.com",
        "body": "Urgent: We detected unusual activity on your account. Please click this link immediately to verify your identity and prevent account suspension. [malicious link]",
    },
]

try:
    ollama_client = ollama.Client()
    ollama_client.list()
    print(f"Successfully connected to Ollama at {REMOTE_OLLAMA_HOST}")
except Exception as e:
    print(f"Error connecting to Ollama at {REMOTE_OLLAMA_HOST}. Please ensure it's running and accessible.")
    print(f"Details: {e}")
    exit(1)


def categorize_email(email_content: str) -> str:
    prompt = (
        f"Categorize the following email content into one of these categories: "
        f"Work, Personal, Promotions, Social, Updates, Spam, Other. "
        f"Respond with ONLY the category name.\n\nEmail Content: {email_content}"
    )
    try:
        response = ollama_client.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        category = response['response'].strip().split('\n')[0].replace('.', '').strip()
        valid_categories = ["Work", "Personal", "Promotions", "Social", "Updates", "Spam", "Other"]
        if category not in valid_categories:
            print(f"Warning: Ollama returned unexpected category '{category}'. Defaulting to 'Other'.")
            return "Other"
        return category
    except Exception as e:
        print(f"Error categorizing email with Ollama: {e}")
        return "Other" # Default category on error

def summarize_email(email_content: str) -> str:
    prompt = (
        f"Summarize the following email content concisely, in one or two sentences. "
        f"Focus on the main point and key details.\n\nEmail Content: {email_content}"
    )
    try:
        response = ollama_client.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False, options= { "keep_alive": -1})
        summary = response['response'].strip()
        return summary
    except Exception as e:
        print(f"Error summarizing email with Ollama: {e}")
        return "Could not generate summary."

def send_to_discord(email_details: dict, category: str, summary: str):
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("\nSkipping Discord notification: Webhook URL not configured.")
        return

    # Format the message for Discord
    message_content = f"**New Email Alert!**\n" \
                      f"**Category:** `{category}`\n" \
                      f"**Subject:** `{email_details['subject']}`\n" \
                      f"**From:** `{email_details['sender']}`\n" \
                      f"**Summary:** {summary}\n" \
                      f"**Original Body (first 200 chars):**\n```\n{email_details['body'][:200]}...\n```"

    payload = {
        "content": message_content,
        "username": "Ollama Email Monitor",
        "avatar_url": "[https://placehold.co/128x128/000000/FFFFFF?text=OM](https://placehold.co/128x128/000000/FFFFFF?text=OM)" # Placeholder avatar
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully sent details for email '{email_details['id']}' to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord webhook: {e}")
        print(f"Response content: {response.text if response else 'N/A'}")

# --- Main Program Logic ---

def process_emails():
    """
    Processes simulated email content: categorizes, summarizes, and sends to Discord.
    """
    print("\n--- Starting Email Processing ---")
    for email in SIMULATED_GMAIL_CONTENT:
        email_id = email['id']
        email_subject = email['subject']
        email_body = email['body']

        print(f"\nProcessing email ID: {email_id} - Subject: '{email_subject}'")

        # Step 1: Categorize
        category = categorize_email(email_body)
        print(f"  Categorized as: {category}")

        # Step 2: Summarize
        summary = summarize_email(email_body)
        print(f"  Summary: {summary}")

        # Step 3: Send to Discord
        send_to_discord(email, category, summary)

        print("-" * 30) # Separator for readability

    print("\n--- Email Processing Complete ---")

if __name__ == "__main__":
    # Check if webhook URL is default placeholder
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("\nWARNING: Discord Webhook URL is not configured.")
    
    # Check if Ollama remote host is default placeholder
    if "localhost:11434" in REMOTE_OLLAMA_HOST and os.getenv("OLLAMA_REMOTE_HOST") is None:
        print("\nWARNING: Ollama remote host is set to default 'localhost'.")
        print("If Ollama is running remotely, please set the OLLAMA_REMOTE_HOST environment variable or update the script.")
        print("Example: export OLLAMA_REMOTE_HOST='http://YOUR_SERVER_IP:11434'")
        print("On the remote server, ensure Ollama is running with `OLLAMA_HOST=0.0.0.0` and port 11434 is open in firewall.")


    process_emails()


