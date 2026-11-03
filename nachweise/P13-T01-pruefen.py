"""Prüft nur Datenbestand und feste Aufteilung; trainiert und bewertet kein Modell."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform


def pruefen(bedingung, meldung):
    if not bedingung:
        raise ValueError(meldung)


def ausfuehren():
    projektordner = Path(__file__).resolve().parents[1]
    datenpfad = projektordner / "beispieldaten/stoerungen.json"
    konfigurationspfad = projektordner / "projekt.json"
    dateninhalt = datenpfad.read_bytes()
    konfigurationsinhalt = konfigurationspfad.read_bytes()
    daten = json.loads(dateninhalt)
    konfiguration = json.loads(konfigurationsinhalt)
    klassen = {"anwendung", "netzwerk", "zugriff"}
    pruefen(len(daten) == konfiguration["expectedRecords"] == 60,
            "Es müssen unverändert 60 Beispieldatensätze vorliegen.")
    for datensatz in daten:
        pruefen(set(datensatz) == {"id", "meldung", "klasse", "synthetisch"},
                "Ein Beispieldatensatz hat unerwartete Felder.")
        pruefen(datensatz["synthetisch"] is True, "Nur synthetische Daten sind zulässig.")
        pruefen(isinstance(datensatz["meldung"], str) and datensatz["meldung"].strip(),
                "Eine Meldung fehlt.")
        pruefen(datensatz["klasse"] in klassen, "Eine Klasse ist unbekannt.")
    kennungen = [datensatz["id"] for datensatz in daten]
    pruefen(len(set(kennungen)) == 60, "Beispielkennungen sind nicht eindeutig.")
    pruefen(set(kennungen) == {f"S{nummer}" for nummer in range(1, 61)},
            "Die Beispielkennungen müssen genau S1 bis S60 sein.")
    aufteilung = konfiguration["aufteilung"]
    training = aufteilung["training"]
    test = aufteilung["test"]
    pruefen(training == [f"S{nummer}" for nummer in range(1, 43)],
            "Die festgelegten Trainingskennungen wurden verändert.")
    pruefen(test == [f"S{nummer}" for nummer in range(43, 61)],
            "Die festgelegten Testkennungen wurden verändert.")
    pruefen(len(set(training)) == len(training) and len(set(test)) == len(test),
            "Eine Teilmenge enthält doppelte Kennungen.")
    pruefen(not set(training) & set(test), "Training und Test überschneiden sich.")
    pruefen(set(training) | set(test) == set(kennungen),
            "Die Aufteilung muss alle Beispielkennungen genau einmal enthalten.")
    nach_kennung = {datensatz["id"]: datensatz for datensatz in daten}
    umgekehrt = {datensatz["id"]: datensatz for datensatz in reversed(daten)}
    pruefen([nach_kennung[kennung] for kennung in training + test]
            == [umgekehrt[kennung] for kennung in training + test],
            "Die Auswahl hängt von der Dateireihenfolge ab.")
    trainingsklassen = Counter(nach_kennung[kennung]["klasse"] for kennung in training)
    testklassen = Counter(nach_kennung[kennung]["klasse"] for kennung in test)
    pruefen(trainingsklassen == {klasse: 14 for klasse in klassen},
            "Unerwartete Trainingsverteilung.")
    pruefen(testklassen == {klasse: 6 for klasse in klassen},
            "Unerwartete Testverteilung.")
    trainingstexte = {nach_kennung[kennung]["meldung"] for kennung in training}
    testtexte = {nach_kennung[kennung]["meldung"] for kennung in test}
    gemeinsame_texte = sorted(trainingstexte & testtexte)
    pruefen(datenpfad.read_bytes() == dateninhalt, "Die Beispieldaten wurden verändert.")
    ergebnis = {
        "ticket": "P13-T01",
        "zeitpunkt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "befehl": "uv run --offline --python 3.12 python -X utf8 nachweise/P13-T01-pruefen.py",
        "python_version": platform.python_version(),
        "ergebnis": "bestanden",
        "daten_sha256": hashlib.sha256(dateninhalt).hexdigest(),
        "konfiguration_sha256": hashlib.sha256(konfigurationsinhalt).hexdigest(),
        "datenanzahl": len(daten),
        "eindeutige_kennungen": len(set(kennungen)),
        "training": training,
        "test": test,
        "kennungsueberschneidung": sorted(set(training) & set(test)),
        "vollstaendig": True,
        "reihenfolgeunabhaengig": True,
        "trainingsklassen": dict(sorted(trainingsklassen.items())),
        "testklassen": dict(sorted(testklassen.items())),
        "gemeinsame_meldungstexte": gemeinsame_texte,
        "testmeldungen_mit_text_im_training": sum(
            nach_kennung[kennung]["meldung"] in trainingstexte for kennung in test),
        "beispieldaten_unveraendert": True,
        "modell_trainiert": False,
        "guetewerte_berechnet": False,
    }
    nachweispfad = projektordner / "nachweise/P13-T01-pruefung.json"
    nachweispfad.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    print("Bestanden: 60 eindeutige Kennungen; Training 42, Test 18; disjunkt und vollständig.")
    print("Je Klasse: Training 14, Test 6; Auswahl unabhängig von der Dateireihenfolge.")
    print(f"Datenleckrisiko: {len(gemeinsame_texte)} gleiche Meldungstexte in beiden Teilmengen.")
    print("Keine Modellanpassung und keine Gütewerte. Nachweis: nachweise/P13-T01-pruefung.json")


if __name__ == "__main__":
    ausfuehren()
