import tweepy
import os
import datetime
import json
from random import choice

# ===== CONFIGURATION =====
print("\n=== TWITTER BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))
print("WIB Time:", (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M"))

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

# ===== ANTI-DUPLICATION SYSTEM =====
def save_last_post(time_key, content):
    with open('last_post.json', 'w') as f:
        json.dump({"time": time_key, "content": content}, f)

def load_last_post():
    try:
        with open('last_post.json', 'r') as f:
            data = json.load(f)
            return data["time"], data["content"]
    except:
        return None, None

# ===== MESSAGE VARIATIONS =====
VARIATIONS = {
    "greeting": ["✨", "🌸", "💫", "🌙", "☀️"],
    "signature": ["\n\n#Day", "\n\nSemangat!", "\n\nBest regards~"]
}

# ===== TWEET SCHEDULE (UTC) =====
TWEET_SCHEDULE = {
    "05:00": "Selamat siang! Sudah makan siang belum?",
    "06:30": "Waktunya ngopi dulu!",
    "08:00": "Selamat sore! Aktivitas hari ini bagaimana?",
    "08:45": "Sore-sore enaknya ngapain ya?",
    "09:15": "Ngabuburit online yuk!",
    "11:00": "Sunset lovers! Lihat matahari terbenam hari ini?",
    "12:45": "Malam minggu nih! Ada rencana seru?",
    "13:30": "Waktunya dinner! Menu spesial apa malam ini?",
    "14:50": "Sebelum tidur, yuk refleksi hari ini!",
    "15:00": "Waktunya me-time! Mau nonton apa?",
    "16:30": "Halo night owls! Masih bangun?",
    "18:00": "Pagi-pagi buta... Sudah bangun?",
    "19:30": "Jangan lupa minum air putih ya!",
    "20:00": "Off dulu, besok lanjut lagi!"
}

# ===== TWEET POSTING =====
current_time = datetime.datetime.utcnow()
posted = False
last_time, last_content = load_last_post()

for schedule_time, base_message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Check time with 7-minute window (matches 15-minute cron)
    if (current_time.hour == schedule_hour and 
        abs(current_time.minute - schedule_min) <= 7):
        
        # Create message with variations
        emoji = choice(VARIATIONS["greeting"])
        message = f"{base_message} {emoji}"
        
        if datetime.datetime.utcnow().weekday() < 5:
            message += choice(VARIATIONS["signature"])
        
        # Check for duplicates
        if last_time != schedule_time or last_content != message:
            try:
                response = client.create_tweet(text=message)
                save_last_post(schedule_time, message)
                wib_time = (datetime.datetime.strptime(schedule_time, "%H:%M") + 
                           datetime.timedelta(hours=7)).strftime("%H:%M")
                print(f"✅ Tweet sent [{schedule_time} UTC/{wib_time} WIB]")
                print(f"📝 Content: {message[:60]}...")
                posted = True
                break
            except tweepy.TweepyException as e:
                print(f"❌ Failed to post: {str(e)[:100]}...")
                if "duplicate" in str(e):
                    print("⚠️ Trying alternative...")
                    new_emoji = choice([e for e in VARIATIONS["greeting"] if e != emoji])
                    alt_message = f"{base_message} {new_emoji}"
                    try:
                        client.create_tweet(text=alt_message)
                        save_last_post(schedule_time, alt_message)
                        print("✅ Alternative sent!")
                        posted = True
                        break
                    except Exception as alt_e:
                        print(f"❌ Failed to send alternative: {alt_e}")

if not posted:
    current_wib = (current_time + datetime.timedelta(hours=7)).strftime("%H:%M")
    print(f"⏳ No scheduled posts (UTC: {current_time.strftime('%H:%M')} | WIB: {current_wib})")
