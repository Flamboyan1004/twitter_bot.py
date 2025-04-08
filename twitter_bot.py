import tweepy
import os
import datetime
import json
import time
import random

print("\n=== TWITTER BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# Improved authentication with error details
try:
    auth = tweepy.OAuth1UserHandler(
        os.environ["API_KEY"],
        os.environ["API_SECRET"],
        os.environ["ACCESS_TOKEN"],
        os.environ["ACCESS_TOKEN_SECRET"]
    )
    client = tweepy.API(auth, wait_on_rate_limit=True)
    user = client.verify_credentials()
    print(f"🔑 Connected as @{user.screen_name}")
except Exception as e:
    print(f"❌ Authentication failed: {str(e)}")
    if "Invalid or expired token" in str(e):
        print("⚠️ Please check your API keys and permissions")
    exit()

# State management
STATE_FILE = 'bot_state.json'

def save_state(last_post, last_error=None):
    state = {
        "last_post": last_post,
        "last_error": last_error or "",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"last_post": None, "last_error": None}

# Tweet schedule (UTC)
TWEET_SCHEDULE = {
    "06:30": "aku on ya gaiss, yang mau order apk premm ridii, cek di bioo",
    "08:00": "selamat sore semuaa udah nonton netflix belum?",
    "10:00": "aku open ress, dm untuk cek harga ya gaiss",
    "16:00": "selamat malam, ngapain ajaa ga tidurr nii?",
    "17:00": "playlist ada di link bio akuu yaa, murcee bangett koo"
}

current_time = datetime.datetime.utcnow()
state = load_state()
posted = False

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Check time window with buffer
    time_match = (
        current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)
    )
    
    if time_match and state.get("last_post") != schedule_time:
        try:
            # Randomized delay
            delay = random.randint(10, 60)
            print(f"⏳ Waiting {delay}s before posting...")
            time.sleep(delay)
            
            # Post tweet
            tweet = client.update_status(message)
            save_state(schedule_time)
            print(f"✅ Tweet posted: https://twitter.com/{user.screen_name}/status/{tweet.id}")
            posted = True
            
        except tweepy.TweepyException as e:
            error_msg = f"❌ Twitter API error: {str(e)}"
            print(error_msg)
            save_state(state["last_post"], error_msg)
            
            if "Too Many Requests" in str(e):
                print("🔄 Waiting 15 minutes due to rate limit...")
                time.sleep(900)
                
        except Exception as e:
            error_msg = f"⚠️ Unexpected error: {str(e)}"
            print(error_msg)
            save_state(state["last_post"], error_msg)

# Status report
if not posted:
    next_schedule = min(
        (k for k in TWEET_SCHEDULE.keys() 
         if datetime.datetime.strptime(k, "%H:%M") > current_time),
        default=None
    )
    status = f"⏳ No posts scheduled (UTC: {current_time.strftime('%H:%M')})"
    if next_schedule:
        status += f" | Next: {next_schedule} UTC"
    if state.get("last_error"):
        status += f"\n⚠️ Last error: {state['last_error']}"
    print(status)
