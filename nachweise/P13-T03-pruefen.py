"""Begrenzte Abnahme des Vergleichs mit unabhängig abgezählten Erwartungen."""

from copy import deepcopy
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
from auswerten import mehrheitsklasse_bestimmen, vergleichen, vorhersagen_bewerten
from trainieren import daten_aufteilen


def pruefen(bedingung, meldung):
    if not bedingung:
        raise ValueError(meldung)


def ausfuehren():
    dateien = ["beispieldaten/stoerungen.json", "projekt.json", "src/trainieren.py",
               "src/auswerten.py", "nachweise/P13-T03-pruefen.py",
               "nachweise/P13-T01-pruefung.json", "nachweise/P13-T02-pruefung-2026-11-09.json"]
    inhalte = {pfad: (PROJEKTORDNER / pfad).read_bytes() for pfad in dateien}
    daten = json.loads(inhalte[dateien[0]])
    konfiguration = json.loads(inhalte["projekt.json"])
    vorleistung = json.loads(inhalte["nachweise/P13-T02-pruefung-2026-11-09.json"])
    pruefen(hashlib.sha256(inhalte[dateien[0]]).hexdigest() == vorleistung["daten_sha256"]
            and len(daten) == konfiguration["expectedRecords"] == 60,
            "Die 60 ursprünglichen Beispieldatensätze müssen erhalten bleiben.")
    pruefen(hashlib.sha256(inhalte["src/trainieren.py"]).hexdigest() == vorleistung["quellcode_sha256"],
            "Die geprüfte Trainingspipeline wurde verändert.")
    aufteilung = konfiguration["aufteilung"]
    pruefen(aufteilung["training"] == vorleistung["training"]
            and aufteilung["test"] == vorleistung["test"], "Feste Aufteilung verändert.")
    ergebnis = vergleichen(daten, aufteilung)
    pruefen(ergebnis["trainingsanzahlen"] == {"anwendung": 14, "netzwerk": 14, "zugriff": 14}
            and ergebnis["baselineklasse"] == "anwendung", "Trainingsbaseline oder Gleichstand falsch.")
    for verfahren, treffer, matrix in [
            ("baseline", 6, [[6, 0, 0], [6, 0, 0], [6, 0, 0]]),
            ("modell", 18, [[6, 0, 0], [0, 6, 0], [0, 0, 6]])]:
        wert = ergebnis[verfahren]
        pruefen([fall["id"] for fall in wert["vorhersagen"]] == aufteilung["test"],
                "Verfahren verwenden nicht dieselben 18 Testkennungen.")
        pruefen(wert["treffer"] == treffer and wert["testanzahl"] == 18
                and wert["trefferanteil"] == treffer / 18 and wert["konfusionsmatrix"] == matrix
                and len(wert["fehler"]) == 18 - treffer, "Kennzahlen oder Fehlerliste unerwartet.")
    pruefen(ergebnis["gemeinsame_meldungstexte"] == 6
            and ergebnis["testfaelle_mit_bekanntem_text"] == 18, "Duplikatgrenze falsch gezählt.")

    # Gegenprobe nur im Speicher: Die Baseline muss einer echten Mehrheit folgen.
    training, test = daten_aufteilen(daten, aufteilung)
    pruefen(mehrheitsklasse_bestimmen(training[training["klasse"] != "anwendung"]["klasse"])
            == "netzwerk", "Alphabetischer Gleichstand falsch.")
    pruefen(mehrheitsklasse_bestimmen(training.iloc[:-2]["klasse"]) == "netzwerk",
            "Baseline folgt nicht der Trainingsmehrheit.")
    # Modell hat hier keine Fehler. Zwei absichtlich falsche Vorhersagen prüfen
    # deshalb die Matrixachsen und Fehlerkennungen, ohne einen Modellfehler zu behaupten.
    gegenprobe = vorhersagen_bewerten(test.iloc[:3], ["zugriff", "zugriff", "netzwerk"])
    pruefen(gegenprobe["treffer"] == 1 and gegenprobe["trefferanteil"] == 1 / 3
            and gegenprobe["konfusionsmatrix"] == [[0, 1, 0], [0, 0, 1], [0, 0, 1]]
            and [fall["id"] for fall in gegenprobe["fehler"]] == ["S43", "S45"],
            "Gegenprobe für Matrixachsen und Fehlerliste fehlgeschlagen.")

    veraendert = deepcopy(daten)
    for zeile in veraendert:
        if zeile["id"] in aufteilung["test"]:
            zeile["klasse"] = "zugriff"
    vergleich = vergleichen(list(reversed(veraendert)), aufteilung)
    for verfahren in ("baseline", "modell"):
        pruefen([fall["vorhersage"] for fall in vergleich[verfahren]["vorhersagen"]]
                == [fall["vorhersage"] for fall in ergebnis[verfahren]["vorhersagen"]],
                "Testklassen oder Dateireihenfolge beeinflussen Vorhersagen.")
    pruefen(all((PROJEKTORDNER / pfad).read_bytes() == inhalt for pfad, inhalt in inhalte.items()),
            "Eine Eingabedatei wurde während der Prüfung verändert.")
    nachweis = {
        "ticket": "P13-T03", "zeitpunkt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ergebnis": "bestanden",
        "versionen": {"Python": platform.python_version(), "scikit-learn": sklearn.__version__,
                      "Pandas": pd.__version__, "NumPy": np.__version__},
        "dateien_sha256": {pfad: hashlib.sha256(inhalt).hexdigest() for pfad, inhalt in inhalte.items()},
        "pruefungen": ["60 Quelldatensätze und geprüfte Trainingspipeline unverändert",
                       "Beide Verfahren auf denselben festen 18 Testkennungen",
                       "Baseline, Trefferanteile, Matrizen und Fehlerlisten unabhängig abgezählt",
                       "Mehrheit und alphabetischer Gleichstand aus Trainingsklassen",
                       "Matrixachsen und Fehlerliste mit zwei absichtlich falschen Vorhersagen geprüft",
                       "Geänderte Testklassen und umgekehrte Dateireihenfolge ändern keine Vorhersage"],
        "auswertung": ergebnis,
    }
    (PROJEKTORDNER / "nachweise/P13-T03-pruefung-2026-11-11.json").write_text(
        json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Bestanden: 60 unveränderte Fälle; beide Verfahren auf denselben 18 Testfällen.")
    print(f"Baseline: {ergebnis['baseline']['treffer']}/18; Modell: {ergebnis['modell']['treffer']}/18.")
    print("Matrizen, Fehlerlisten, Trainingsmehrheit und Gegenproben geprüft; alle 18 Testtexte schon im Training.")


if __name__ == "__main__":
    ausfuehren()
