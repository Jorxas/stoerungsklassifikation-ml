"""Lokale Abnahme: echte Pipeline und Ausschluss der Testdaten aus jeder Anpassung."""

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import sys
from unittest.mock import patch

import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

PROJEKTORDNER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKTORDNER / "src"))
from trainieren import modell_trainieren


def pruefen(bedingung, meldung):
    if not bedingung:
        raise ValueError(meldung)


def ausfuehren():
    datenpfad = PROJEKTORDNER / "beispieldaten/stoerungen.json"
    dateninhalt = datenpfad.read_bytes()
    daten = json.loads(dateninhalt)
    konfiguration = json.loads((PROJEKTORDNER / "projekt.json").read_text(encoding="utf-8"))
    vorher = json.loads((PROJEKTORDNER / "nachweise/P13-T01-pruefung.json").read_text(encoding="utf-8"))
    aufteilung = konfiguration["aufteilung"]
    pruefen(hashlib.sha256(dateninhalt).hexdigest() == vorher["daten_sha256"],
            "Die ursprünglichen Beispieldaten wurden verändert.")
    pruefen(len(daten) == konfiguration["expectedRecords"] == 60
            and aufteilung["training"] == vorher["training"]
            and aufteilung["test"] == vorher["test"], "Datenanzahl oder feste Aufteilung verändert.")
    nach_kennung = {zeile["id"]: zeile for zeile in daten}
    erwartete_texte = [nach_kennung[kennung]["meldung"] for kennung in aufteilung["training"]]
    erwartete_klassen = [nach_kennung[kennung]["klasse"] for kennung in aufteilung["training"]]
    merkmalsaufrufe = []
    modellaufrufe = []
    urspruengliche_merkmale = TfidfVectorizer.fit_transform
    urspruengliches_training = MultinomialNB.fit

    def merkmale_anpassen(selbst, texte, ziel=None):
        merkmalsaufrufe.append(list(texte))
        return urspruengliche_merkmale(selbst, texte, ziel)

    def klassifikator_anpassen(selbst, merkmale, klassen, sample_weight=None):
        modellaufrufe.append((merkmale.shape[0], list(klassen)))
        return urspruengliches_training(selbst, merkmale, klassen, sample_weight=sample_weight)

    with patch.object(TfidfVectorizer, "fit_transform", merkmale_anpassen), patch.object(
            MultinomialNB, "fit", klassifikator_anpassen):
        pipeline = modell_trainieren(daten, aufteilung)
    pruefen(merkmalsaufrufe == [erwartete_texte], "Textanpassung verwendet andere als Trainingsdaten.")
    pruefen(modellaufrufe == [(42, erwartete_klassen)], "Modellanpassung verwendet andere als Trainingsdaten.")

    # Nur Kopien im Speicher verändern: Die 60 Quelldatensätze bleiben erhalten.
    veraendert = deepcopy(daten)
    for zeile in veraendert:
        if zeile["id"] in aufteilung["test"]:
            zeile["meldung"] = "ausschliesslichestestwort"
            zeile["klasse"] = "testklasse"
    vergleich = modell_trainieren(list(reversed(veraendert)), aufteilung)
    textmerkmale = pipeline.named_steps["textmerkmale"]
    vergleichsmerkmale = vergleich.named_steps["textmerkmale"]
    pruefen(textmerkmale.vocabulary_ == vergleichsmerkmale.vocabulary_
            and "ausschliesslichestestwort" not in vergleichsmerkmale.vocabulary_,
            "Testinhalte beeinflussen den Wortschatz.")
    np.testing.assert_array_equal(textmerkmale.idf_, vergleichsmerkmale.idf_)
    klassifikator = pipeline.named_steps["klassifikator"]
    vergleichsklassifikator = vergleich.named_steps["klassifikator"]
    for attribut in ("classes_", "class_count_", "feature_count_", "class_log_prior_", "feature_log_prob_"):
        np.testing.assert_array_equal(getattr(klassifikator, attribut), getattr(vergleichsklassifikator, attribut))
    np.testing.assert_array_equal(klassifikator.class_count_, [14, 14, 14])

    ungueltig = deepcopy(aufteilung)
    ungueltig["test"][0] = aufteilung["training"][0]
    with patch.object(TfidfVectorizer, "fit_transform") as anpassung:
        try:
            modell_trainieren(daten, ungueltig)
        except ValueError as fehler:
            fehlermeldung = str(fehler)
        else:
            raise ValueError("Überlappende Kennungen wurden zugelassen.")
        pruefen(not anpassung.called, "Ungültige Aufteilung wurde vor ihrer Ablehnung angepasst.")
    pruefen(datenpfad.read_bytes() == dateninhalt, "Die Quelldatei wurde verändert.")
    ergebnis = {
        "ticket": "P13-T02",
        "zeitpunkt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ergebnis": "bestanden",
        "befehl": "uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 nachweise/P13-T02-pruefen.py",
        "versionen": {"Python": platform.python_version(), "scikit-learn": sklearn.__version__, "Pandas": pd.__version__, "NumPy": np.__version__},
        "daten_sha256": hashlib.sha256(dateninhalt).hexdigest(),
        "quellcode_sha256": hashlib.sha256((PROJEKTORDNER / "src/trainieren.py").read_bytes()).hexdigest(),
        "pruefskript_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "vorleistungsnachweis_sha256": hashlib.sha256(
            (PROJEKTORDNER / "nachweise/P13-T01-pruefung.json").read_bytes()).hexdigest(),
        "datenanzahl": len(daten),
        "training": aufteilung["training"],
        "test": aufteilung["test"],
        "textanpassung_nur_training": merkmalsaufrufe == [erwartete_texte],
        "klassifikatoranpassung_nur_training": modellaufrufe == [(42, erwartete_klassen)],
        "merkmalsanzahl": len(textmerkmale.vocabulary_),
        "gelernte_klassenanzahlen": dict(zip(klassifikator.classes_, klassifikator.class_count_.astype(int).tolist())),
        "testinhalte_und_dateireihenfolge_ohne_einfluss": True,
        "ueberlappung_vor_anpassung_abgewiesen": fehlermeldung,
        "beispieldaten_unveraendert": True,
        "baseline_ausgefuehrt": False,
        "testvorhersagen_oder_guetewerte_berechnet": False,
    }
    # Den beim unterbrochenen Versuch hinterlassenen Nachweis nicht überschreiben.
    (PROJEKTORDNER / "nachweise/P13-T02-pruefung-2026-11-09.json").write_text(
        json.dumps(ergebnis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Bestanden: 60 unveränderte Fälle; Anpassung nur auf 42 Trainingsfällen, 14 je Klasse.")
    print("Wortschatz, IDF und Modellparameter trotz geänderter Testinhalte unverändert.")
    print("Überlappende Kennungen vor Anpassung abgewiesen; keine Baseline oder Testgüte berechnet.")


if __name__ == "__main__":
    ausfuehren()
