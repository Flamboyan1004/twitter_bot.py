import tweepy
import os
import datetime
import json

# ===== KONFIGURASI =====
print("\n=== BOT TWITTER DIMULAI ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))
print("WIB Time:", (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M"))

# 1. Autentikasi
try:
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    user = client.get_me()
    print(f"🔑 Terhubung ke Twitter sebagai @{user.data.username}")
except Exception as e:
    print(f"❌ Gagal koneksi: {e}")
    exit()

# ===== FUNGSI ANTI DUPLIKASI =====
def save_last_post(time_key):
    with open('last_post.json', 'w') as f:
        json.dump({"last_post": time_key}, f)

def load_last_post():
    try:
        with open('last_post.json', 'r') as f:
            return json.load(f).get("last_post")
    except:
        return None

# ===== JADWAL TWEET (UTC) DENGAN KONVERSI WIB =====
TWEET_SCHEDULE = {
    # Format: "UTC_TIME": "message"  # WIB_TIME (UTC+7)
    "05:00": "Selamat siang! Sudah makan siang belum nih? Jangan lupa istirahat sebentar ya! ☀️ Aku ready akun prem lohh, cek bio yaa!!! #LunchTime",  # 12:00 WIB
    "06:30": "Waktunya ngopi dulu biar semangat lanjut aktivitas! ☕ Siapa yang lagi WFH hari ini?",  # 13:30 WIB
    "08:00": "Selamat sore gaiss! Aktivitas hari ini udah sampai mana nih? 😊",  # 15:00 WIB
    "08:45": "Sore-sore gini enaknya ngapain ya? Ada yang mau rekomendasiin series atau lagu?",  # 15:45 WIB
    "09:15": "Ngabuburit online yuk! Ada yang mau cerita aktivitas hari ini? 🍵",  # 16:15 WIB
    "15:00": "Waktunya me-time! Malam ini ada yang mau nonton apa atau main game apa? 🎮🍿",  # 22:00 WIB
    "16:30": "Halo night owls! Ada yang masih bangun? Aku open order sampai jam 3 pagi nih 😊",  # 23:30 WIB
    "18:00": "Pagi-pagi buta yang sepi... Ada yang udah bangun buat sahur atau kerja shift malam? 🌙",  # 01:00 WIB
    "19:30": "Buat yang masih terjaga, jangan lupa minum air putih ya! 💧",  # 02:30 WIB
    "20:00": "Off dulu gais, besok lanjut lagi! 💤"  # 03:00 WIB
}

# ===== POSTING TWEET =====
current_time = datetime.datetime.utcnow()
posted = False
last_post = load_last_post()

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Cek waktu dengan toleransi 15 menit sebelum - 20 menit setelah
    if (current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)):
        
        # Cek apakah sudah pernah diposting
        if last_post != schedule_time:
            try:
                response = client.create_tweet(text=message)
                save_last_post(schedule_time)
                wib_time = (datetime.datetime.strptime(schedule_time, "%H:%M") + datetime.timedelta(hours=7)).strftime("%H:%M")
                print(f"✅ Tweet terkirim [{schedule_time} UTC / {wib_time} WIB]: https://twitter.com/user/status/{response.data['id']}")
                posted = True
            except Exception as e:
                print(f"❌ Gagal posting: {e}")

if not posted:
    current_wib = (current_time + datetime.timedelta(hours=7)).strftime("%H:%M")
    print(f"⏳ Tidak ada jadwal (UTC: {current_time.strftime('%H:%M')} | WIB: {current_wib})")
