State of Charge Prediction Dashboard

Bu proje, bir bataryanın State of Charge (SOC) tahminini yapabilen bir sistemdir. Sistem üç ana bileşenden oluşur:

Dash Dashboard – SOC verilerini görselleştirmek için web arayüzü.

Flask API + MQTT Subscriber – MQTT üzerinden gelen batarya verilerini alır, SOC tahmini yapar ve API üzerinden sunar.

MQTT Publisher – Örnek batarya verilerini MQTT broker’ına gönderir.

Projede Docker Compose kullanılarak üç servis aynı anda çalıştırılabilir.

🚀 Özellikler

Gerçek zamanlı SOC tahmini

Dashboard ile veri görselleştirme

MQTT üzerinden veri alma ve gönderme

Kolayca Docker ile dağıtılabilir

Kurulum ve Çalıştırma
1. Gereksinimler

Docker ve Docker Compose yüklü olmalı

Windows kullanıcıları için Linux container modu aktif olmalı

2. Docker ile Çalıştırma

Proje dizininde terminal açın ve:

# Tüm container’ları build edip ayağa kaldır
docker-compose up --build
Dash Dashboard: http://localhost:8010/dashboard

Flask API: http://localhost:5000/latest_soc

Container’ları arka planda çalıştırmak için:

docker-compose up -d

Durdurmak için:

docker-compose down

3. Servisler
Servis	        Açıklama    	            Port
dash_app	    Dash Dashboard	            8010
api_server	    Flask API + MQTT Subscriber	5000
mqtt_publisher	Örnek veri gönderici	—


4. Veri Güncelleme

Yeni .mat dosyalarını data/ klasörüne ekleyin.

MQTT Publisher container’ı tekrar başlatıldığında yeni verileri gönderir.

Eğer volume kullanıyorsanız, host dizinini container’a mount edebilirsiniz.

5. Python Bağımlılıkları

Tüm bağımlılıklar requirements.txt içinde listelenmiştir

6. Notlar

PYTHONPATH=/app Dockerfile’da ayarlanmıştır, böylece proje modülleri container içinde import edilebilir.

MQTT Publisher, Dash ve API bağımsız çalışabilir.

Dash, SOC tahminlerini gerçek zamanlı görselleştirir ve API üzerinden son SOC değerlerini sunar.
