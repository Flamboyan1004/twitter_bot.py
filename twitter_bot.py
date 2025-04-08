import tweepy
import os
import datetime
import json
from random import choice, randint
import time

print("\n=== BOT TWITTER AMAN ===")
print("UTC:", datetime.datetime.utcnow().strftime("%H:%M"))
print("WIB:", (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M"))

# 1. Authentication
try:
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    user = client.get_me()
    print(f"🔑 Login sebagai @{user.data.username}")
except Exception as e:
    print(f"❌ Gagal login: {e}")
    exit()

# 2. Anti-spam System
def save_log(today_count, message):
    log = {
        "last_post": datetime.datetime.now().isoformat(),
        "today_count": today_count,
        "date": datetime.date.today().isoformat(),
        "content": message[:50] + "..."
    }
    with open('bot_log.json', 'w') as f:
        json.dump(log, f)

def load_log():
    try:
        with open('bot_log.json', 'r') as f:
            log = json.load(f)
            # Convert old format to new format
            if "date" not in log:
                log_date = datetime.datetime.fromisoformat(log["last_post"]).date() if log["last_post"] else datetime.date.today()
                log["date"] = log_date.isoformat()
            return log
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_post": None,
            "today_count": 0,
            "date": datetime.date.today().isoformat()
        }

# 3. Content Settings
MAX_DAILY_TWEETS = 8
MIN_INTERVAL = datetime.timedelta(minutes=90)

CONTENT_POOL = {
    "promo": [
        "1READY AMAZON PRIME VIDEO cek bio yaa!",
        "Nonton Netflix lebih hemat, aku ready! 🌸",
        "Butuh akun Viu Premium? DM aja! ✨",
        "Ada promo khusus hari ini cek WA di bio"
    ],
    "organic": [
        "kalian kalo lagi break biasanya ngapain",
        "kalian lagi nonton apaa best?",
        "Spill Film terakhir yang bikin terharu",
        "NETFLIX MURAH ADAAA!!! DM JEE KIWW",
        "drakor lama yang underrated tp bagus apa yh"
    ]
}

# 4. Time Settings (WIB 12:00-03:00 → UTC 05:00-20:00)
SCHEDULE_WINDOW = {
    "start": datetime.time(5, 0),   # 12:00 WIB
    "end": datetime.time(20, 0)     # 03:00 WIB
}

# Main Logic
log = load_log()
current_date = datetime.date.today().isoformat()

# Reset counter if new day
if log["date"] != current_date:
    log["today_count"] = 0
    log["date"] = current_date

last_post_time = (
    datetime.datetime.fromisoformat(log["last_post"]) 
    if log["last_post"] 
    else None
)
today_count = log["today_count"]

current_utc = datetime.datetime.utcnow()
current_wib = current_utc + datetime.timedelta(hours=7)

# Check if within operational hours
if SCHEDULE_WINDOW["start"] <= current_utc.time() <= SCHEDULE_WINDOW["end"]:
    
    # Check limits
    if today_count >= MAX_DAILY_TWEETS:
        print(f"⛔ Batas harian ({MAX_DAILY_TWEETS} tweet) tercapai")
        exit()

    if last_post_time and (current_utc - last_post_time) < MIN_INTERVAL:
        remaining = (MIN_INTERVAL - (current_utc - last_post_time)).seconds // 60
        print(f"⏳ Menunggu interval... ({remaining} menit lagi)")
        exit()

    # Random delay (5-15 minutes)
    delay = randint(300, 900)
    print(f"⏲️ Menambah delay acak {delay//60} menit...")
    time.sleep(delay)

    # Select content (40% promo chance)
    content_type = "promo" if randint(1, 10) <= 4 else "organic"
    current_message = choice(CONTENT_POOL[content_type])
    
    try:
        # Post tweet
        response = client.create_tweet(text=current_message)
        today_count += 1
        save_log(today_count, current_message)
        
        print(f"✅ {'PROMO' if content_type == 'promo' else 'ORGANIC'} terkirim")
        print(f"🕒 [{current_utc.strftime('%H:%M')} UTC/{current_wib.strftime('%H:%M')} WIB]")
        print(f"📝 Konten: {current_message[:60]}...")
        print(f"#️⃣ Tweet {today_count}/{MAX_DAILY_TWEETS} hari ini")
        
    except tweepy.TweepyException as e:
        if "duplicate" in str(e).lower():
            print("⚠️ Konten duplikat, mencoba alternatif...")
            current_message = choice([msg for msg in CONTENT_POOL["organic"] if msg != current_message])
            try:
                client.create_tweet(text=current_message)
                today_count += 1
                save_log(today_count, current_message)
                print("✅ Alternatif organik terkirim!")
            except Exception as alt_e:
                print(f"❌ Gagal alternatif: {alt_e}")
        else:
            print(f"❌ Error posting: {str(e)[:100]}")

else:
    print(f"🌙 Di luar jam operasional (12:00-03:00 WIB)")
