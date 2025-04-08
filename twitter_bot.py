import tweepy
import os
import datetime
import json
from random import choice

print("\n=== BOT TWITTER DIMULAI ===")
print("UTC:", datetime.datetime.utcnow().strftime("%H:%M"))
print("WIB:", (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M"))

# Autentikasi
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

# Anti duplikat
def save_post(time, content):
    with open('last_post.json', 'w') as f:
        json.dump({"time": time, "content": content}, f)

def load_post():
    try:
        with open('last_post.json', 'r') as f:
            data = json.load(f)
            return data["time"], data["content"]
    except:
        return None, None

# Variasi pesan
EMOJI = ["✨", "🌸", "💫", "🌙", "☀️"]
PROMOSI = [
    " cek pricelist di bio yaa!",
    " ready akun murah lohh",
    " kami ridii akun premium!",
    " cek WA di bio untuk info lengkap"
]

# Jadwal UTC (WIB = UTC+7) dengan konten promosi
JADWAL = {
    "05:00": "1READY AMAZON PRIME VIDEO" + choice(PROMOSI),
    "06:30": "Selamat siang! Sudah makan siang belum? aku READY NETFLIX lohh" + choice(PROMOSI),
    "08:00": "Sore-sore enaknya ngapain ya? nonton viu ga sii?" + choice(PROMOSI),
    "08:45": "Menu makan malam apa hari ini? makan sambil nonton iqiyi" + choice(PROMOSI),
    "09:15": "Bosen nonton netplixx? move ke vidio keknya seruu" + choice(PROMOSI),
    "11:00": "Malam minggu nih! Nonton Disney+ Hotstar yuk!" + choice(PROMOSI),
    "12:45": "1READY HBO GO lengkap semua season!" + choice(PROMOSI),
    "13:30": "Waktunya me-time! Mau nonton apa nih? Kami ready semua platform loh" + choice(PROMOSI),
    "14:50": "Sebelum tidur nonton dulu yuk! Ada yang mau coba MOLA TV?" + choice(PROMOSI),
    "15:00": "1READY WE TV UNTUK DRAMA LOVERSS!" + choice(PROMOSI),
    "16:30": "Masih bangun nih? Yuk nonton U-NEXT biar ga ngantuk!" + choice(PROMOSI),
    "18:00": "1READY APPLE TV+ FILM BARU TERUS!" + choice(PROMOSI),
    "19:30": "Jangan lupa istirahat! Sambil nonton Crunchyroll yuk!" + choice(PROMOSI),
    "20:00": "Off dulu gais! Pesan akun bisa via WA di bio ya!"
}

# Proses posting
waktu_sekarang = datetime.datetime.utcnow()
terposting = False
waktu_terakhir, konten_terakhir = load_post()

for jadwal, pesan in JADWAL.items():
    jam, menit = map(int, jadwal.split(":"))
    
    if (waktu_sekarang.hour == jam and 
        abs(waktu_sekarang.minute - menit) <= 7):
        
        pesan_baru = f"{pesan} {choice(EMOJI)}"
        
        if waktu_terakhir != jadwal or konten_terakhir != pesan_baru:
            try:
                client.create_tweet(text=pesan_baru)
                save_post(jadwal, pesan_baru)
                waktu_wib = (datetime.datetime.strptime(jadwal, "%H:%M") + 
                            datetime.timedelta(hours=7)).strftime("%H:%M")
                print(f"✅ Berhasil posting [{jadwal} UTC/{waktu_wib} WIB]")
                print(f"📝 Isi: {pesan_baru[:60]}...")
                terposting = True
                break
            except Exception as e:
                print(f"❌ Gagal: {str(e)[:100]}")

if not terposting:
    waktu_wib = (waktu_sekarang + datetime.timedelta(hours=7)).strftime("%H:%M")
    print(f"⏳ Tidak ada jadwal (UTC: {waktu_sekarang.strftime('%H:%M')} | WIB: {waktu_wib})")
