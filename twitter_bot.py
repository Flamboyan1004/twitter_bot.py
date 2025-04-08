import tweepy
import os
import datetime
import json
import time
import random

print("\n=== TWITTER BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# Gunakan API v1.1 dengan OAuth1
try:
    auth = tweepy.OAuth1UserHandler(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    client = tweepy.API(auth, wait_on_rate_limit=True)
    
    # Verifikasi kredensial
    try:
        user = client.verify_credentials()
        print(f"🔑 Connected as @{user.screen_name}")
    except tweepy.TweepyException as e:
        print(f"❌ Credential verification failed: {str(e)}")
        if "Unauthorized" in str(e):
            print("⚠️ Please check your API keys and permissions")
        exit()

except Exception as e:
    print(f"❌ Authentication failed: {str(e)}")
    exit()

# ... (bagian state management tetap sama)

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
    
    time_match = (
        current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)
    )
    
    if time_match and state.get("last_post") != schedule_time:
        try:
            delay = random.randint(10, 60)
            print(f"⏳ Waiting {delay}s before posting...")
            time.sleep(delay)
            
            # Gunakan API v1.1 untuk posting
            tweet = client.update_status(status=message)
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
            elif "Forbidden" in str(e):
                print("⚠️ Please check your app permissions in Twitter Developer Portal")
                
        except Exception as e:
            error_msg = f"⚠️ Unexpected error: {str(e)}"
            print(error_msg)
            save_state(state["last_post"], error_msg)

# ... (bagian status report tetap sama)
