from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables dari file .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'app.env')
load_dotenv(ENV_PATH)

# Ambil API Key dari file .env
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

app = Flask(__name__)

# Menentukan path file history dalam folder proyek
FILE_PATH = os.path.join(BASE_DIR, 'history_bmi.txt')

def kirim_email(email, nama, usia, jenis_kelamin, berat, tinggi, aktivitas, bmi, rekomendasi):
    try:
        message = Mail(
            from_email="syafiqsyaugisyawie@gmail.com",  # Ganti dengan email yang sudah diverifikasi di SendGrid
            to_emails=email,
            subject="Hasil Perhitungan BMI Anda",
            plain_text_content=f"""
            Halo {nama},

            Berikut adalah hasil perhitungan BMI Anda:
            - Nama: {nama}
            - Usia: {usia} tahun
            - Jenis Kelamin: {jenis_kelamin}
            - Berat: {berat} kg
            - Tinggi: {tinggi} m
            - Aktivitas: {aktivitas}
            - BMI: {bmi:.2f}
            - Rekomendasi: {rekomendasi}

            Terima kasih telah menggunakan layanan kami.
            """
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True, ""
    except Exception as e:
        return False, str(e)

def hitung_bmi(berat, tinggi):
    return berat / (tinggi ** 2)

def rekomendasi_kesehatan(bmi):
    if bmi < 18.5:
        return "Kamu kekurangan berat badan. Perbanyak makan makanan bergizi!"
    elif 18.5 <= bmi < 24.9:
        return "Berat badan kamu normal. Pertahankan!"
    elif 25 <= bmi < 29.9:
        return "Kamu kelebihan berat badan. Kurangi makan dan perbanyak olahraga!"
    else:
        return "Kamu obesitas. Segera konsultasi dengan dokter!"

def catat_history(nama, usia, jenis_kelamin, berat, tinggi, aktivitas, bmi, rekomendasi, email_status="Sukses"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            file.write("=== HISTORY BMI ===\n")

    with open(FILE_PATH, 'a', encoding='utf-8') as file:
        file.write(f"\nTimestamp: {timestamp}\n")
        file.write(f"Nama: {nama}, Usia: {usia}, Jenis Kelamin: {jenis_kelamin}\n")
        file.write(f"Berat: {berat} kg, Tinggi: {tinggi} m, Aktivitas: {aktivitas}, BMI: {bmi:.2f}\n")
        file.write(f"Rekomendasi: {rekomendasi}\n")
        file.write(f"Status Email: {email_status}\n")
        file.write("-" * 50 + "\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hitung_bmi', methods=['POST'])
def hitung():
    try:
        data = request.json
        nama = data.get('nama', '').strip()
        usia = data.get('usia', '').strip()
        jenis_kelamin = data.get('jenis_kelamin', '').strip()
        berat = data.get('berat', '').strip()
        tinggi = data.get('tinggi', '').strip()
        aktivitas = data.get('aktivitas', '').strip()
        email = data.get('email', '').strip()

        if not nama or not usia or not jenis_kelamin or not berat or not tinggi or not aktivitas or not email:
            return jsonify({"error": "Semua kolom harus diisi dengan benar!"}), 400

        usia = int(usia)
        berat = float(berat)
        tinggi = float(tinggi)

        if usia < 0 or berat < 10 or tinggi < 0.8:
            return jsonify({"error": "Data tidak valid. Cek kembali isian Anda!"}), 400

        bmi = hitung_bmi(berat, tinggi)
        rekomendasi = rekomendasi_kesehatan(bmi)

        email_berhasil, email_error = kirim_email(email, nama, usia, jenis_kelamin, berat, tinggi, aktivitas, bmi, rekomendasi)
        email_status = "Sukses" if email_berhasil else f"Gagal ({email_error})"

        catat_history(nama, usia, jenis_kelamin, berat, tinggi, aktivitas, bmi, rekomendasi, email_status)

        response_data = {"bmi": round(bmi, 2), "rekomendasi": rekomendasi}
        if not email_berhasil:
            response_data["email_error"] = "Gagal mengirim email, namun hasil BMI tetap ditampilkan."

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
