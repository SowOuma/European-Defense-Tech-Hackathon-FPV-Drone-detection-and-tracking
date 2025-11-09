import cv2
from ultralytics import YOLO
from openai import OpenAI
import os
import math
import time

# === Chargement du modèle YOLO ===
model = YOLO(r"models\best_1.pt")
print("Modèle YOLO chargé avec succès")
model.eval()

# === États globaux ===
drone_history = {}
latest_detection = {}


# === Fonction de calcul de distance physique ===
def estimate_distance(h_px, f_mm=400, sensor_width_mm=36, img_width_px=3840, drone_height_m=0.25):
    """
    Calcule la distance réelle estimée (en mètres) du drone FPV Kamikaze
    à partir de la hauteur du bounding box (en pixels).
    """
    if h_px <= 0:
        return None
    f_px = (f_mm / sensor_width_mm) * img_width_px
    D = (f_px * drone_height_m) / h_px
    return round(D, 1)


# === Analyse du mouvement + distance ===
def analyse_mouvement(drone_id, bbox, frame_time):
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    current = (cx, cy, frame_time)
    previous = drone_history.get(drone_id)

    vitesse = 0
    direction = "indéterminée"
    stabilite = "haute"

    if previous:
        dt = frame_time - previous[2]
        if dt > 0:
            dx = cx - previous[0]
            dy = cy - previous[1]
            dist = math.sqrt(dx**2 + dy**2)
            vitesse = dist / dt

            if abs(dx) > abs(dy):
                direction = "vers la droite" if dx > 0 else "vers la gauche"
            else:
                direction = "vers le haut" if dy < 0 else "vers le bas"

            prev_v = previous[3] if len(previous) > 3 else vitesse
            delta_v = abs(vitesse - prev_v)
            stabilite = "haute" if delta_v < 5 else "instable"

    # Sauvegarde du dernier état
    drone_history[drone_id] = (cx, cy, frame_time, vitesse)

    # 🔹 Calcul distance physique à partir de la bbox
    h_px = y2 - y1
    distance_estimee = estimate_distance(h_px)

    return {
        "drone_id": drone_id,
        "distance_estimee": distance_estimee,
        "vitesse": round(vitesse, 2),
        "direction": direction,
        "stabilite": stabilite
    }


# === Fonction principale : génération vidéo ===
def generation_video(camera, model):
    global latest_detection  # 🔸 Important : partage avec Flask
    os.makedirs("captures", exist_ok=True)

    CLASS_NAMES = ['A10', 'B1','B52', 'C130', 'C5', 'F117', 'F15', 'F22', 'MQ9', 'Tu160', 'aircraft', 'jet']
    
    tracker_config = "bytetrack.yaml"
    tracks = {}

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Détection et tracking
        results = model.track(source=frame, persist=True, tracker=tracker_config, stream=True)
        frame_time = time.time()

        for r in results:
            boxes = r.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                track_id = int(box.id[0]) if box.id is not None else -1

                # Calcul et analyse
                info = analyse_mouvement(track_id, (x1, y1, x2, y2), frame_time)

                # 🔹 Mise à jour du dernier état global
                latest_detection = {
                    "id": track_id,
                    "class": "drone",
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                    "distance_estimee": info["distance_estimee"],
                    "vitesse": info["vitesse"],
                    "direction": info["direction"],
                    "stabilite": info["stabilite"]
                }

                # --- Affichage sur la frame ---
                label_text = (
                    f"Drone {conf:.2f} | {info['distance_estimee']}m | "
                    f"{info['vitesse']}px/s | {info['direction']}"
                )
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label_text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Trace la trajectoire du drone
                if track_id not in tracks:
                    tracks[track_id] = []
                tracks[track_id].append(((x1 + x2)//2, (y1 + y2)//2))
                if len(tracks[track_id]) > 30:
                    tracks[track_id].pop(0)

                for i in range(1, len(tracks[track_id])):
                    cv2.line(frame, tracks[track_id][i - 1], tracks[track_id][i], (0, 255, 0), 2)

        # Encodage en MJPEG pour Flask
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() +
               b'\r\n')



def get_latest_detection():
    """Retourne la dernière détection enregistrée."""
    global latest_detection
    return latest_detection

def get_drone_history():
    """Retourne l'historique des drones détectés."""
    global drone_history
    return drone_history

# === Configuration de l'API Groq (analyse IA) ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or 
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")



def analyze_aircraft_with_groq(ac_class: str, confidence: float, context: str = "") -> str:
    """
    Analyse tactique courte et factuelle d'un drone détecté.
    Le modèle NE DOIT PAS inventer de chiffres, il reformule seulement le contexte fourni.
    """
    try:
        system_prompt = (
            "Tu es un opérateur militaire observant le ciel. "
            "Tu rédiges des rapports concis (2 à 3 phrases maximum). "
            "⚠️ Tu NE DOIS PAS inventer ni modifier les valeurs numériques (distance, vitesse, direction, stabilité). "
            "Tu dois uniquement reformuler les données données dans le contexte. "
            "Aucune extrapolation, aucune conversion d'unités. "
            "Ton ton doit être clair, professionnel et concis."
        )

        user_prompt = f"""
        Informations de détection :
        {context or "Aucune donnée fournie."}

        Type d'appareil : {ac_class}
        Confiance du modèle : {confidence:.2f}

        Rédige un rapport factuel reprenant EXACTEMENT les valeurs ci-dessus.
        Exemple attendu :
        "Un drone détecté à 130.1 m, vitesse 36.33 px/s, direction indéterminée. Stabilité haute."
        Ne convertis pas les unités. Ne fais aucune supposition.
        """.strip()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # 🔒 verrouillage total : aucune imagination
            max_tokens=120,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Erreur analyse IA: {str(e)}"
