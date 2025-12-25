from flask import Flask, jsonify, request
import csv
import os
import re
from flask_cors import CORS
import unicodedata

app = Flask(__name__)
CORS(app)

# CSV'yi yükle ve işle
def load_plaka_data():
    data = []
    try:
        with open('plaka.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    # Ad soyad ve plakayı temizle
                    ad_soyad = row[0].strip()
                    plaka = row[1].strip().upper()
                    
                    # Türkçe karakter normalize
                    ad_soyad = unicodedata.normalize('NFKC', ad_soyad)
                    plaka = unicodedata.normalize('NFKC', plaka)
                    
                    data.append({
                        'ad_soyad': ad_soyad,
                        'plaka': plaka
                    })
        print(f"✓ {len(data)} kayıt yüklendi")
        return data
    except Exception as e:
        print(f"✗ CSV yükleme hatası: {e}")
        return []

# Global veri
plaka_data = load_plaka_data()

# Türkçe karakter normalize fonksiyonu
def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', str(text))
    text = text.upper()
    # Türkçe karakter düzeltme
    replacements = {
        'İ': 'I', 'ı': 'I', 'Ğ': 'G', 'ğ': 'G',
        'Ü': 'U', 'ü': 'U', 'Ş': 'S', 'ş': 'S',
        'Ö': 'O', 'ö': 'O', 'Ç': 'C', 'ç': 'C'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

# Plakaya göre ara
def ara_plaka(plaka_sorgu):
    plaka_sorgu = normalize_text(plaka_sorgu)
    sonuclar = []
    
    for kayit in plaka_data:
        if plaka_sorgu in normalize_text(kayit['plaka']):
            sonuclar.append(kayit)
    
    return sonuclar

# Ad soyada göre ara
def ara_ad_soyad(ad, soyad):
    ad = normalize_text(ad) if ad else ""
    soyad = normalize_text(soyad) if soyad else ""
    
    sonuclar = []
    
    for kayit in plaka_data:
        ad_soyad_norm = normalize_text(kayit['ad_soyad'])
        
        # Hem ad hem soyad varsa
        if ad and soyad:
            if ad in ad_soyad_norm and soyad in ad_soyad_norm:
                sonuclar.append(kayit)
        # Sadece ad varsa
        elif ad:
            if ad in ad_soyad_norm:
                sonuclar.append(kayit)
        # Sadece soyad varsa
        elif soyad:
            if soyad in ad_soyad_norm:
                sonuclar.append(kayit)
    
    return sonuclar

# Ana sayfa
@app.route('/')
def ana_sayfa():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>F3 Plaka API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
            .endpoint { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #4CAF50; }
            code { background: #e9ecef; padding: 3px 6px; border-radius: 3px; font-family: monospace; }
            .test-link { display: inline-block; background: #4CAF50; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; margin: 5px 0; }
            .test-link:hover { background: #45a049; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 F3 Plaka API</h1>
            <p>Toplam <strong>""" + str(len(plaka_data)) + """</strong> plaka kaydı</p>
            
            <div class="endpoint">
                <h3>🔍 Plakaya Göre Ara</h3>
                <code>GET /f3api/plaka?plaka=34KG4978</code><br>
                <a class="test-link" href="/f3api/plaka?plaka=34KG4978" target="_blank">Test: 34KG4978</a>
                <a class="test-link" href="/f3api/plaka?plaka=34" target="_blank">Test: 34 (İl kodu)</a>
            </div>
            
            <div class="endpoint">
                <h3>👤 Ad Soyada Göre Ara</h3>
                <code>GET /f3api/adsoyadplaka?ad=SEFER&soyad=KARABACAK</code><br>
                <code>GET /f3api/adsoyadplaka?ad=AHMET</code><br>
                <code>GET /f3api/adsoyadplaka?soyad=YILMAZ</code><br>
                <a class="test-link" href="/f3api/adsoyadplaka?ad=SEFER&soyad=KARABACAK" target="_blank">Test: SEFER KARABACAK</a>
                <a class="test-link" href="/f3api/adsoyadplaka?ad=AHMET" target="_blank">Test: AHMET</a>
            </div>
            
            <div class="endpoint">
                <h3>📊 İstatistikler</h3>
                <code>GET /f3api/istatistik</code><br>
                <a class="test-link" href="/f3api/istatistik" target="_blank">İstatistikleri Gör</a>
            </div>
            
            <div class="footer">
                <p>💻 <strong>Yapımcı:</strong> @sukazatkinis</p>
                <p>📢 <strong>Telegram Kanal:</strong> @f3system</p>
                <p>📅 Veritabanı: """ + str(len(plaka_data)) + """ kayıt</p>
                <p>⚠️ Bu API sadece eğitim amaçlıdır.</p>
            </div>
        </div>
    </body>
    </html>
    """

# Plaka arama endpoint'i
@app.route('/f3api/plaka')
def plaka_ara():
    plaka_sorgu = request.args.get('plaka', '').strip()
    
    if not plaka_sorgu:
        return jsonify({
            'success': False,
            'message': 'Plaka parametresi gerekli',
            'ornek': '/f3api/plaka?plaka=34KG4978',
            'yapimci': '@sukazatkinis',
            'kanal': '@f3system'
        }), 400
    
    sonuclar = ara_plaka(plaka_sorgu)
    
    return jsonify({
        'success': True,
        'sorgu': plaka_sorgu,
        'sonuc_sayisi': len(sonuclar),
        'sonuclar': sonuclar,
        'yapimci': '@sukazatkinis',
        'telegram_kanal': '@f3system',
        'not': 'Bu API sadece eğitim amaçlıdır.'
    })

# Ad soyad arama endpoint'i
@app.route('/f3api/adsoyadplaka')
def ad_soyad_ara():
    ad = request.args.get('ad', '').strip()
    soyad = request.args.get('soyad', '').strip()
    
    if not ad and not soyad:
        return jsonify({
            'success': False,
            'message': 'Ad veya soyad parametresi gerekli',
            'ornek': '/f3api/adsoyadplaka?ad=SEFER&soyad=KARABACAK',
            'yapimci': '@sukazatkinis',
            'kanal': '@f3system'
        }), 400
    
    sonuclar = ara_ad_soyad(ad, soyad)
    
    return jsonify({
        'success': True,
        'sorgu': {
            'ad': ad,
            'soyad': soyad
        },
        'sonuc_sayisi': len(sonuclar),
        'sonuclar': sonuclar,
        'yapimci': '@sukazatkinis',
        'telegram_kanal': '@f3system',
        'not': 'Ozsoylar her yerde vip kalite :D.'
    })

# İstatistik endpoint'i
@app.route('/f3api/istatistik')
def istatistik():
    # İl kodlarına göre sayım
    il_kodlari = {}
    for kayit in plaka_data:
        plaka = kayit['plaka']
        if plaka and len(plaka) >= 2:
            il_kodu = plaka[:2]
            if il_kodu.isdigit():
                il_kodlari[il_kodu] = il_kodlari.get(il_kodu, 0) + 1
    
    # En çok kayıt olan ilk 10 il
    en_cok_kayit = sorted(il_kodlari.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'success': True,
        'toplam_kayit': len(plaka_data),
        'il_dagilimi': il_kodlari,
        'en_cok_kayitli_iller': en_cok_kayit,
        'yapimci': '@sukazatkinis',
        'telegram_kanal': '@f3system'
    })

# Health check
@app.route('/f3api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'kayit_sayisi': len(plaka_data),
        'api_versiyon': '1.0',
        'yapimci': '@sukazatkinis'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
