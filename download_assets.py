import urllib.request
import os
from pathlib import Path

ASSETS_DIR = Path("assets/exercises")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Sources from free-exercise-db and curated fitness illustrations
SOURCES = {
    "deadbug_estatico": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Dead_Bug/0.jpg",
    "bird_dog_controlado": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Superman/0.jpg",
    "plancha_lateral": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Side_Bridge/0.jpg",
    "jalon_al_pecho": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Wide-Grip_Lat_Pulldown/0.jpg",
    "dominadas_asistidas": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Band_Assisted_Pull-Up/0.jpg",
    "jalon_estrecho": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/V-Bar_Pulldown/0.jpg",
    "press_hombros_sentado_mancuernas": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Seated_Dumbbell_Press/0.jpg",
    "press_maquina": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Machine_Shoulder_Military_Press/0.jpg",
    "press_half_kneeling": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Landmine_180s/0.jpg",
    "remo_mancuerna_apoyado": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/One-Arm_Dumbbell_Row/0.jpg",
    "remo_polea_baja": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Seated_Cable_Rows/0.jpg",
    "remo_pecho_apoyado": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Dumbbell_Incline_Row/0.jpg",
    "sentadilla_bulgara": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Split_Squat_with_Dumbbells/0.jpg",
    "zancada_atras": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Dumbbell_Rear_Lunge/0.jpg",
    "prensa_unilateral": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Leg_Press/0.jpg",
    "goblet_squat": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Goblet_Squat/0.jpg",
    "prensa_horizontal": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Leg_Press/0.jpg",
    "sentadilla_fitball": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Ball_Squat/0.jpg",
    "extension_banco_45": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Hyperextensions_Back_Extensions/0.jpg",
    "puente_gluteos": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Barbell_Glute_Bridge/0.jpg",
    "patada_gluteo_polea": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Glute_Kickback/0.jpg"
}

results = {}
for key, url in SOURCES.items():
    dest = ASSETS_DIR / f"{key}.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
        results[key] = (True, len(data))
        print(f"SUCCESS: {key} ({len(data)} bytes)")
    except Exception as e:
        results[key] = (False, str(e))
        print(f"FAILED: {key} -> {e}")

success_count = sum(1 for v in results.values() if v[0])
print(f"\nDownloaded {success_count}/{len(SOURCES)} images successfully.")

