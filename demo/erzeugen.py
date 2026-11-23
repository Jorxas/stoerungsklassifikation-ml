"""Erzeugt demo/daten/lauf.json aus einem echten Lauf der Projektpipeline.

Aufruf im Projektordner (Versionen wie in START.md):
  uv run --python 3.12 --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 \
      python -X utf8 demo/erzeugen.py

Es wird nichts nachgebaut: src/trainieren.py und src/auswerten.py laufen unverändert.
Zusätzlich werden die gelernten Parameter des angepassten Modells exportiert, damit die
Seite im Browser dieselbe Vorhersage rechnen kann (Eigene Meldung testen). Eine Referenz
mit Python-Vorhersagen für Beispieltexte dient dem Browsertest als Gegenprobe.
"""
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

PROJEKT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKT / "src"))
from auswerten import vergleichen  # noqa: E402
from trainieren import modell_trainieren, daten_aufteilen  # noqa: E402

konfig = json.loads((PROJEKT / "projekt.json").read_text(encoding="utf-8"))
daten = json.loads((PROJEKT / konfig["fixture"]).read_text(encoding="utf-8"))
aufteilung = konfig["aufteilung"]

ergebnis = vergleichen(daten, aufteilung)
pipeline = modell_trainieren(daten, aufteilung)
tf = pipeline.named_steps["textmerkmale"]
nb = pipeline.named_steps["klassifikator"]
training, test = daten_aufteilen(daten, aufteilung)

wortschatz = sorted(tf.vocabulary_, key=lambda w: tf.vocabulary_[w])
modell = {
    "klassen": [str(k) for k in nb.classes_],
    "wortschatz": wortschatz,
    "idf": [float(x) for x in tf.idf_],
    "featureLogProb": [[float(x) for x in z] for z in nb.feature_log_prob_],
    "klassenLogPrior": [float(x) for x in nb.class_log_prior_],
    "alpha": float(nb.alpha),
}

proben = [
    "Verbindung zum Demorechner nicht möglich",
    "Demoanwendung nicht verfügbar unspezifischer Fehler",
    "Zugriff auf Demoverzeichnis verweigert",
    "Der Drucker im Büro druckt nicht",
    "Zugriff verweigert",
    "Verbindung verloren",
    "Anwendung abgestürzt",
    "demoanwendung",
    "VERBINDUNG ZUM DEMORECHNER NICHT MÖGLICH",
    "Zugriff auf die Anwendung nicht möglich",
    "",
    "x",
]
referenz = []
for t in proben:
    wahr = pipeline.predict([t])[0]
    p = pipeline.predict_proba([t])[0]
    referenz.append({"text": t, "klasse": str(wahr), "wahrscheinlichkeiten": [float(x) for x in p]})

mengen = {}
for z in daten:
    mengen[z["meldung"]] = mengen.get(z["meldung"], 0) + 1
texte = [{"text": t, "anzahl": n,
          "imTraining": int(sum(training["meldung"] == t)),
          "imTest": int(sum(test["meldung"] == t))} for t, n in mengen.items()]

ausgabe = {
    "zeit": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "umgebung": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                 "pandas": pd.__version__, "numpy": np.__version__},
    "befehl": "src/auswerten.py (vergleichen) und src/trainieren.py (modell_trainieren), unverändert",
    "ergebnis": ergebnis,
    "datensatz": daten,
    "aufteilung": {"training": aufteilung["training"], "test": aufteilung["test"]},
    "verschiedeneTexte": texte,
    "modell": modell,
    "referenz": referenz,
}
ziel = PROJEKT / "demo/daten/lauf.json"
ziel.parent.mkdir(parents=True, exist_ok=True)
ziel.write_text(json.dumps(ausgabe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"geschrieben: {ziel.relative_to(PROJEKT)}; Baseline {ergebnis['baseline']['treffer']}/18, "
      f"Modell {ergebnis['modell']['treffer']}/18; Wortschatz {len(wortschatz)}")
