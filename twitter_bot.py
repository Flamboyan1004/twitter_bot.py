import tweepy
import os
import datetime
import json
from random import choice

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

# ===== VARIASI PESAN =====
VARIATIONS = {
    "greeting": ["✨", "🌸", "💫", "🌙", "☀️"],
    "signature": ["\n\n#Day", "\n\nSemangat!", "\n\nBest regards~"]
}

# ===== JADWAL TWEET (UTC) =====
TWEET_SCHEDULE = {
    "05:00": "Selamat siang! Sudah makan siang belum? Jangan lupa istirahat sebentar ya! ☀️",
    "06:30": "Waktunya ngopi dulu biar semangat lanjut aktivitas! ☕",
    "08:00": "Selamat sore gaiss! Aktivitas hari ini udah sampai mana nih? 😊",
    "08:45": "Sore-sore gini enaknya ngapain ya? Ada rekomendasi series atau lagu?",
    "09:15": "Ngabuburit online yuk! Ada yang mau cerita aktivitas hari ini? 🍵",
    "11:00": "Hai sunset lovers! Udah lihat matahari terbenam hari ini? 💛",
    "12:45": "Malam minggu nih! Ada yang punya rencana seru malam ini? 🎉",
    "13:30": "Waktunya dinner! Menu spesial malam ini apa nih? 🥘",
    "14:50": "Sebelum tidur, yuk refleksiin hari ini! Hal paling berkesan apa? 🌙",
    "15:00": "Waktunya me-time! Mau nonton apa atau main game apa? 🎮",
    "16:30": "Halo night owls! Ada yang masih bangun? 😊",
    "18:00": "Pagi-pagi buta... Ada yang udah bangun buat sahur? 🌙",
    "19:30": "Buat yang masih terjaga, jangan lupa minum air putih ya! 💧",
    "20:00": "Off dulu gais, besok lanjut lagi! 💤"
}

# ===== POSTING TWEET =====
current_time = datetime.datetime.utcnow()
posted = False
last_time, last_content = load_last_post()

for schedule_time, base_message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Cek waktu dengan toleransi 15 menit
    if (current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 15)):
        
        # Tambahkan variasi ke pesan
        message = f"{base_message}{choice(VARIATIONS['greeting']}"
        if datetime.datetime.now().weekday() < 5:  # Hari kerja
            message += choice(VARIATIONS['signature'])
        
        # Cek duplikat
        if last_time != schedule_time or last_content != message:
            try:
                response = client.create_tweet(text=message)
                save_last_post(schedule_time, message)
                wib_time = (datetime.datetime.strptime(schedule_time, "%H:%M") + 
                           datetime.timedelta(hours=7)).strftime("%H:%M")
                print(f"✅ Tweet terkirim [{schedule_time} UTC/{wib_time} WIB]")
                print(f"📝 Konten: {message[:60]}...")
                posted = True
                break
            except tweepy.TweepyException as e:
                print(f"❌ Gagal posting: {str(e)[:100]}...")
                if "duplicate" in str(e):
                    print("⚠️ Mencoba versi alternatif...")
                    alt_message = f"{base_message} {choice(VARIATIONS['greeting'])}"
                    try:
                        client.create_tweet(text=alt_message)
                        save_last_post(schedule_time, alt_message)
                        print("✅ Alternatif terkirim!")
                        posted = True
                        break
                    except Exception as alt_e:
                        print(f"❌ Gagal alternatif: {alt_e}")

if not posted:
    current_wib = (current_time + datetime.timedelta(hours=7)).strftime("%H:%M")
    print(f"⏳ Tidak ada jadwal (UTC: {current_time.strftime('%H:%M')} | WIB: {current_wib})")
