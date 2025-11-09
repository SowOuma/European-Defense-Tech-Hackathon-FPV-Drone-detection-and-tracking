/******************************
 *  Script principal interface
 *  — Projet Drone Detection —
 ******************************/

let lastSeenClass = null;
let lastAnalysisAt = 0;
let lastDistance = null;
let lastSpeed = null;
let lastDirection = null;
const ANALYSIS_COOLDOWN_MS = 3000; // délai mini entre 2 analyses IA

// === Fonction : Analyse IA (appel à Flask → Groq)
async function refreshAnalysis(det) {
  const el = document.getElementById("llm_output");
  el.innerHTML = "<em>Analyse en cours...</em>";

  try {
    const resp = await fetch("/analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "class": det.cls,
        "confidence": det.conf ?? 0.0,
        "context": ""
      })
    });

    const data = await resp.json();
    const a = data.analysis;

    if (typeof a === "string") {
      el.innerHTML = a;

      // ✨ Animation visuelle : clignotement vert lors de la mise à jour IA
      el.classList.add("flash");
      setTimeout(() => el.classList.remove("flash"), 1000);
    } else {
      el.innerHTML = "<em>Analyse vide.</em>";
    }
  } catch (err) {
    console.warn("Erreur d'analyse IA :", err);
    el.innerHTML = "<span style='color:#f87171;'>⚠️ Erreur réseau ou IA.</span>";
  }
}

// === Fonction : mise à jour des infos de détection ===
async function refreshDetection() {
  try {
    const r = await fetch('/last_detection');
    const d = await r.json();
    if (!d || !d.class) return;

    // ✅ Met à jour les métriques principales dans la page
    document.getElementById("drone_count").textContent = d.count ?? 1;
    document.getElementById("drone_distance").textContent = d.distance_estimee ?? "–";
    document.getElementById("drone_speed").textContent = d.vitesse ?? "–";
    document.getElementById("drone_direction").textContent = d.direction ?? "–";
    document.getElementById("drone_stability").textContent = d.stabilite ?? "–";

    // 🔍 Vérifie si des valeurs clés ont changé
    const changed =
      d.distance_estimee !== lastDistance ||
      d.vitesse !== lastSpeed ||
      d.direction !== lastDirection;

    // 🔁 Si oui → relance une nouvelle analyse IA
    if (changed && Date.now() - lastAnalysisAt > ANALYSIS_COOLDOWN_MS) {
      lastSeenClass = d.class;
      lastDistance = d.distance_estimee;
      lastSpeed = d.vitesse;
      lastDirection = d.direction;
      lastAnalysisAt = Date.now();

      console.log("🔄 Nouvelle analyse IA (valeurs modifiées) :", {
        distance: lastDistance,
        vitesse: lastSpeed,
        direction: lastDirection
      });

      await refreshAnalysis({ cls: d.class, conf: d.confidence });
    }
  } catch (e) {
    console.warn("Erreur refreshDetection", e);
  }
}

// === Reset au démarrage ===
fetch("/reset_detection", { method: "POST" })
  .then(() => console.log("✅ Détection réinitialisée au lancement."))
  .catch(console.warn);

// === Gestion du formulaire caméra ===
$(document).ready(function () {
  $('#camera1').click(function () {
    $.post('/cliquer_bouton', { button: 'camera1' }, function (response) {
      if (response.url) {
        $('#video_camera1').attr('src', response.url);
      } else {
        alert('Erreur : aucun flux disponible.');
      }
    });
  });

  document.getElementById('camera-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const camera1Url = document.getElementById('cam1').value;
    if (!camera1Url) {
      alert('Veuillez entrer la source de la caméra.');
      return;
    }
    fetch('/recuperer_source', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ camera1_url: camera1Url })
    })
      .then(r => r.json())
      .then(d => {
        if (d.error) alert('Erreur: ' + d.error);
        else console.log('🎥 Source caméra OK:', d);
      })
      .catch(console.error);
  });
});

// === Rafraîchissement automatique ===
setInterval(refreshDetection, 2500);
