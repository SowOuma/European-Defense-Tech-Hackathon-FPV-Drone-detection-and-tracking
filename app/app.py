from flask import Flask, Response, render_template, request, jsonify, url_for 
import os, json, re
from fonctions import *




app = Flask(__name__)

# Initialisation des variables globales
camera1_url = None#"rtsp://169.254.197.98:554/media/video1"
camera2_url =None
camera = None
camera1 = None
points_camera1 = []
points_camera2 = []



#definition du route principale 
@app.route("/")


#appelle de la appelle page html pour son affichage 

@app.route("/App")
def home1():
    return render_template('index.html')



@app.route('/recuperer_source', methods=['POST'])
def recuperer_source():
    global camera1_url, camera2_url, camera, camera1
    data = request.json
    try:
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        """"
        if 'camera1_url' not in data or 'camera2_url' not in data:
            return jsonify({'error': 'Les URLs des deux caméras doivent être fournies'}), 400
        """
        camera1_url = data.get('camera1_url')
        
        
        print(f"URL de la caméra 1 : {camera1_url}")
      
        
        # Libération des caméras précédemment ouvertes

        if camera is not None:
            camera.release()
        


        def captureVideo(url):
            if url.startswith("rtsp://"):
                capture=cv2.VideoCapture(url)
                capture.set(cv2.CAP_PROP_BUFFERSIZE,2)
                
                return capture
            elif(url=='0'):
                return cv2.VideoCapture(0)
            else:

                return cv2.VideoCapture(url)
    
        camera = captureVideo(camera1_url)
        
        
        # Vérification si les caméras ont été ouvertes avec succès
        if not camera.isOpened():
            camera = None
            print(f"Échec de l'ouverture de la caméra avec l'URL {camera1_url}")
            return jsonify({'error': f'Échec de l\'ouverture de la caméra avec l\'URL {camera1_url}'}), 500
        
        return jsonify({'message': 'Flux démarrés avec succès'})
    except Exception as e:
        print(f"Erreur lors de la recuperation des urls: {str(e)}")   
     



@app.route("/video")
def video():
    from fonctions import model
    if camera is None:
        return "Camera 1 non initialisée", 500
    return Response(generation_video(camera, model), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/cliquer_bouton", methods=["POST"])
def cliquer_bouton():
    button = request.form.get("button")
    if button == "camera1":
        url = url_for("video", _external=True)  
    elif button == "camera2":
        url = url_for("video1", _external=True) 
    else:
        url = None

    if url:
        return jsonify({"url": url})
    else:
        return jsonify({"error": "Flux vidéo non disponible"}), 400


@app.route("/last_detection")
def last_detection():
    from fonctions import get_latest_detection, get_drone_history

    latest = get_latest_detection()
    history = get_drone_history()

    # S’il n’y a encore rien
    if not latest or latest.get("bbox") is None:
        return jsonify({
            "class": None,
            "confidence": 0.0,
            "count": len(history),
            "distance_estimee": None,
            "vitesse": None,
            "direction": None,
            "stabilite": None
        })

    # Sinon on renvoie les infos de la dernière détection
    return jsonify({
        **latest,
        "count": len(history)
    })






@app.route("/analysis", methods=["POST"])
def analysis():
    try:
        from fonctions import get_latest_detection  # 🔹 Import du getter
        data = request.get_json(force=True) or {}
        ac_class = (data.get("class") or "").strip()
        confidence = float(data.get("confidence") or 0.0)

        # 🔹 On récupère la dernière détection réelle
        last = get_latest_detection() or {}
        distance = last.get("distance_estimee", "inconnue")
        vitesse = last.get("vitesse", "inconnue")
        direction = last.get("direction", "inconnue")
        stabilite = last.get("stabilite", "inconnue")

        # 🔹 Construit un contexte simple et factuel
        context = (
            f"Distance estimée: {distance} mètres. "
            f"Vitesse: {vitesse} px/s. "
            f"Direction: {direction}. "
            f"Stabilité: {stabilite}."
        )

        if not ac_class:
            return jsonify({"error": "Missing 'class'"}), 400

        # 🔹 Appel à ton analyseur IA avec le vrai contexte
        result = analyze_aircraft_with_groq(ac_class, confidence, context)
        print("📡 Contexte IA :", context)


        return jsonify({"analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset_tracking", methods=["POST"])
def reset_tracking():
    """
    Réinitialise complètement le système de détection et de tracking :
    - efface toutes les vitesses, directions, trajectoires, etc.
    - réinitialise la dernière détection.
    """
    try:
        from fonctions import drone_history, latest_detection  # import des objets globaux

        # 🔄 Vider les dictionnaires / structures
        drone_history.clear()
        latest_detection.clear()

        # 🔹 Réinitialiser proprement les valeurs de base
        latest_detection.update({
            "class": None,
            "confidence": None,
            "bbox": None,
            "distance_estimee": None,
            "vitesse": None,
            "direction": None,
            "stabilite": None
        })

        print("♻️ Tracking et détection réinitialisés avec succès.")
        return jsonify({"message": "Tracking réinitialisé avec succès"}), 200

    except Exception as e:
        print("❌ Erreur de reset tracking :", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
