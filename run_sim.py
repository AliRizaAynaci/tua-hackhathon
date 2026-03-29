import subprocess
import os
import sys

def run():
    baseline_map = "output/test2_cost_data/cost_map.npy"
    if not os.path.exists(baseline_map):
        print(f"Hata: Baseline cost map bulunamadi: {baseline_map}")
        print("Lutfen once src/cost_map.py ile bir baseline olusturun.")
        return

    # Sadece ilk acilista haritayi kopyalamak icin kullaniyoruz
    # Artik rastgele engel enjekte ETMİYORUZ, engelleri UI üzerinden ekleyeceksiniz.
    new_map = "output/new_cost_map.npy"
    
    # Python venv dosyasini zorla (zorunlu module not found hatalarini onler)
    venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "bin", "python3")
    if os.path.exists(venv_python):
        python_cmd = venv_python
    else:
        python_cmd = sys.executable

    print("--- 1. Baseline Harita Hazirlaniyor (Sadece Orijinal NASA Verisi, Rastgele Engel Yok) ---")
    # Rastgele engelleri tamamen iptal ettik, sadece saf ay haritasini (cost_map.npy) aliyoruz
    subprocess.run([python_cmd, "-c", f"import shutil; shutil.copy('{baseline_map}', '{new_map}')"])

    print("\n--- 2. A* + RRT Simulasyonu Basliyor (Pygame) ---")
    subprocess.run([python_cmd, "src/rover_sim_pygame.py", baseline_map, new_map])

if __name__ == "__main__":
    run()
