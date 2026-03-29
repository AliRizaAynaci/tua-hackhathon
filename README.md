# Lunar Rover Navigation Simulator

## Kurulum
Öncelikle gerekli kütüphaneleri sanal ortamınızda (venv) yükleyin:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Not: `crop_tiff.py` GDAL aracını kullanır, bu sebeple sisteminizde `gdal` kurulu olmalıdır (`brew install gdal` veya `sudo apt install gdal-bin`).

## Simülasyonu Çalıştırma (A* + RRT)
Projede oluşturulan `run_sim.py` dosyası ile engel ekleme ve UI simülasyon süreçlerini tek komutla başlatabilirsiniz. 

```bash
python3 run_sim.py
```
*(Not: Çalıştırmadan önce `output/cost_test_data/cost_map.npy` dosyasının oluşturulmuş olması gereklidir.)*

## Backend API (Unity Entegrasyonu)
Global A* ve local RRT planlama API'si `backend/` altındadır.

### Çalıştırma
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpointler
- `GET /health`
- `POST /plan/global`
- `POST /map/update-obstacles`
- `POST /plan/local-rrt`
- `GET /session/{session_id}/path`
- `DELETE /session/{session_id}`

### Minimal akış
1. Unity `start/goal` ile `POST /plan/global` çağırır (A*).
2. Simülasyon sırasında yeni engel algılanınca sadece obstacle delta gönderilir (`POST /map/update-obstacles`).
3. Rover engel önünde kaldığında `POST /plan/local-rrt` çağrılır ve local detour alınır.

---

## Veri Hazırlama Scriptleri

Dosyalar `src/` klasörü içindedir. 

### 1. src/crop_tiff.py
DEM'den belirli bir bölgeyi keser (GDAL kullanır).
```bash
python3 src/crop_tiff.py ../dem.tif 2000 5000 2000 2000 test_region.tif
```

### 2. src/cost_map.py
DEM verisinden eğim, pürüzlülük ve maliyet haritası oluşturur. (Simülasyon öncesi gereklidir!)
```bash
python3 src/cost_map.py test_region.tif output/cost_test
```

### 3. src/tif2png.py
TIFF'i PNG'ye çevirir (Raw DEM + Hillshade görünümü).
```bash
python3 src/tif2png.py test_region.tif test_region.png
```

---

## DEM Bilgileri
**Ana DEM:** `dem.tif`
- Boyut: 10324x25540 piksel
- Yükseklik: -2068m ile -1087m
