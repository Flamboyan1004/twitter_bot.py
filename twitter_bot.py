import tweepy
import os
import datetime
import json
import time
import random

# ===== CONFIGURATION =====
print("\n=== TWITTER BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# 1. Authentication
try:
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    user = client.get_me()
    print(f"🔑 Connected as @{user.data.username}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# ===== ANTI-DUPLICATION =====
def save_last_post(time_key):
    with open('last_post.json', 'w') as f:
        json.dump({"last_post": time_key}, f)

def load_last_post():
    try:
        with open('last_post.json', 'r') as f:
            return json.load(f).get("last_post")
    except:
        return None

# ===== TWEET SCHEDULE (UTC) =====
TWEET_SCHEDULE = {
    "06:30": "aku on ya gaiss, yang mau order apk premm ridii, cek di bioo",
    "08:00": "selamat sore semuaa udah nonton netflix belum?",
    "10:00": "aku open ress, dm untuk cek harga ya gaiss",
    "16:00": "selamat malam, ngapain ajaa ga tidurr nii?",
    "17:00": "playlist ada di link bio akuu yaa, murcee bangett koo"
}

# ===== TWEET POSTING =====
current_time = datetime.datetime.utcnow()
posted = False
last_post = load_last_post()

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Check time window (15 mins before - 20 mins after)
    if (current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)):
        
        # Check if already posted
        if last_post != schedule_time:
            try:
                # Random delay to avoid pattern detection
                time.sleep(random.randint(0, 120))
                
                response = client.create_tweet(text=message)
                save_last_post(schedule_time)
                print(f"✅ Tweet posted: https://twitter.com/user/status/{response.data['id']}")
                posted = True
            except tweepy.TweepyException as e:
                print(f"❌ Failed to post: {e}")
                if "Too Many Requests" in str(e):
                    print("⚠️ Rate limit exceeded, waiting 15 minutes...")
                    time.sleep(900)
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")

if not posted:
    next_schedule = min(
        (k for k in TWEET_SCHEDULE.keys() 
         if datetime.datetime.strptime(k, "%H:%M") > current_time),
        default=None
    )
    status_msg = f"⏳ No scheduled posts (UTC: {current_time.strftime('%H:%M')})"
    if next_schedule:
        status_msg += f" | Next: {next_schedule} UTC"
    print(status_msg)
