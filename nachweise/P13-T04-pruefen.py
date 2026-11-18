"""T04: Drei echte Baselinefehler und die synthetische Datengrenze nachweisen."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
import sklearn

PROJEKTORDNER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKTORDNER / "src"))
from auswerten import vergleichen


def pruefen(bedingung, meldung):
    if not bedingung:
        raise ValueError(meldung)


def ausfuehren():
    dateien = ["beispieldaten/stoerungen.json", "projekt.json", "src/trainieren.py",
               "src/auswerten.py", "nachweise/P13-T04-pruefen.py",
               "nachweise/P13-T03-pruefung-2026-11-11.json"]
    inhalte = {pfad: (PROJEKTORDNER / pfad).read_bytes() for pfad in dateien}
    vorleistung = json.loads(inhalte[dateien[-1]])
    pruefen(vorleistung["ticket"] == "P13-T03" and vorleistung["ergebnis"] == "bestanden",
            "Die geprüfte Vorleistung T03 fehlt.")
    for pfad in (dateien[0], "src/trainieren.py", "src/auswerten.py"):
        pruefen(hashlib.sha256(inhalte[pfad]).hexdigest() == vorleistung["dateien_sha256"][pfad],
                f"Quelldaten oder geprüfter Quellcode verändert: {pfad}")
    daten = json.loads(inhalte[dateien[0]])
    konfiguration = json.loads(inhalte["projekt.json"])
    pruefen(len(daten) == konfiguration["expectedRecords"] == 60
            and all(zeile["synthetisch"] is True for zeile in daten),
            "Erwartet: die ursprünglichen 60 synthetischen Meldungen.")
    aufteilung = konfiguration["aufteilung"]
    pruefen(aufteilung["training"] == [f"S{nummer}" for nummer in range(1, 43)]
            and aufteilung["test"] == [f"S{nummer}" for nummer in range(43, 61)],
            "Die feste Aufteilung wurde verändert.")
    # Tatsächlich erneut trainieren und vorhersagen; keine künstlichen Fehler einspeisen.
    ergebnis = vergleichen(daten, aufteilung)
    pruefen(ergebnis == vorleistung["auswertung"], "Der Vergleich weicht von T03 ab.")
    fehler = {fall["id"]: fall for fall in ergebnis["baseline"]["fehler"]}
    modellfaelle = {fall["id"]: fall for fall in ergebnis["modell"]["vorhersagen"]}
    beispiele = []
    for kennung in ("S43", "S44", "S50"):
        fall = fehler[kennung]
        pruefen(fall["soll"] != fall["vorhersage"] == "anwendung",
                f"Kein beobachteter Baselinefehler: {kennung}")
        beispiele.append({**fall, "verfahren": "Mehrheitsbaseline",
                          "modellvorhersage": modellfaelle[kennung]["vorhersage"]})
    pruefen(len(ergebnis["baseline"]["fehler"]) == 12
            and ergebnis["modell"]["fehler"] == []
            and len({zeile["meldung"] for zeile in daten}) == 6
            and ergebnis["gemeinsame_meldungstexte"] == 6
            and ergebnis["testfaelle_mit_bekanntem_text"] == 18,
            "Fehlerzahl oder Grenze der wiederholten Texte unerwartet.")
    pruefen(all((PROJEKTORDNER / pfad).read_bytes() == inhalt for pfad, inhalt in inhalte.items()),
            "Eine Eingabedatei wurde während der Prüfung verändert.")
    nachweis = {
        "ticket": "P13-T04", "ergebnis": "bestanden",
        "zeitpunkt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "versionen": {"Python": platform.python_version(), "scikit-learn": sklearn.__version__,
                      "Pandas": pd.__version__, "NumPy": np.__version__},
        "dateien_sha256": {pfad: hashlib.sha256(inhalt).hexdigest() for pfad, inhalt in inhalte.items()},
        "drei_beobachtete_baselinefehler": beispiele,
        "klassenanzahlen": dict(sorted(Counter(zeile["klasse"] for zeile in daten).items())),
        "eindeutige_meldungstexte": 6,
        "auswertung": ergebnis,
        "grenze": "60 synthetische Meldungen; alle 18 Testtexte im Training. Keine industrielle Übertragbarkeit belegt. Drei Baselinefehler sind keine drei unterschiedlichen Fehlerursachen; kein Modellfehler beobachtet.",
    }
    (PROJEKTORDNER / "nachweise/P13-T04-pruefung-2026-11-17.json").write_text(
        json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Bestanden: S43, S44 und S50 erneut als Baselinefehler beobachtet; kein Modellfehler.")
    print("60 unveränderte synthetische Meldungen, 6 Texte; alle 18 Testtexte im Training.")
    print("Baseline 6/18, Modell 18/18; vollständiger Vergleich identisch mit T03.")


if __name__ == "__main__":
    ausfuehren()
