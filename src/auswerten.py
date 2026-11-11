"""P13-T03: Feste Testmenge einmalig gegen die Trainingsbaseline auswerten."""

from collections import Counter
import json

from sklearn.metrics import accuracy_score, confusion_matrix

from trainieren import PROJEKTORDNER, daten_aufteilen, modell_trainieren


KLASSEN = ["anwendung", "netzwerk", "zugriff"]


def mehrheitsklasse_bestimmen(trainingsklassen):
    anzahl = Counter(trainingsklassen)
    # Die vorab festgelegte alphabetische Reihenfolge entscheidet Gleichstände.
    return min(anzahl, key=lambda klasse: (-anzahl[klasse], klasse))


def vorhersagen_bewerten(test, vorhersagen):
    soll = test["klasse"].tolist()
    faelle = [
        {"id": kennung, "meldung": zeile["meldung"], "soll": zeile["klasse"],
         "vorhersage": vorhersage}
        for (kennung, zeile), vorhersage in zip(test.iterrows(), vorhersagen, strict=True)
    ]
    return {
        "treffer": sum(sollklasse == vorhersage for sollklasse, vorhersage in zip(soll, vorhersagen)),
        "testanzahl": len(test),
        "trefferanteil": float(accuracy_score(soll, vorhersagen)),
        "konfusionsmatrix": confusion_matrix(soll, vorhersagen, labels=KLASSEN).tolist(),
        "vorhersagen": faelle,
        "fehler": [fall for fall in faelle if fall["soll"] != fall["vorhersage"]],
    }


def vergleichen(daten, aufteilung):
    training, test = daten_aufteilen(daten, aufteilung)
    if not test["klasse"].isin(KLASSEN).all():
        raise ValueError("Eine Testklasse ist unbekannt.")
    if not test["meldung"].map(lambda text: isinstance(text, str) and bool(text.strip())).all():
        raise ValueError("Jede Testmeldung muss einen nichtleeren Text enthalten.")
    mehrheitsklasse = mehrheitsklasse_bestimmen(training["klasse"].tolist())
    pipeline = modell_trainieren(daten, aufteilung)
    return {
        "klassenreihenfolge": KLASSEN,
        "matrixachsen": "Zeilen: tatsächliche Klasse; Spalten: vorhergesagte Klasse.",
        "trainingsanzahlen": dict(sorted(Counter(training["klasse"]).items())),
        "baselineklasse": mehrheitsklasse,
        "baseline": vorhersagen_bewerten(test, [mehrheitsklasse] * len(test)),
        "modell": vorhersagen_bewerten(test, pipeline.predict(test["meldung"].tolist()).tolist()),
        "gemeinsame_meldungstexte": len(set(training["meldung"]) & set(test["meldung"])),
        "testfaelle_mit_bekanntem_text": int(test["meldung"].isin(training["meldung"]).sum()),
        "grenze": "Synthetische, wiederholte Texte; kein Nachweis für neue Texte oder industrielle Übertragbarkeit. Keine Modelloptimierung anhand der Testdaten.",
    }


def ausfuehren():
    konfiguration = json.loads((PROJEKTORDNER / "projekt.json").read_text(encoding="utf-8"))
    daten = json.loads((PROJEKTORDNER / konfiguration["fixture"]).read_text(encoding="utf-8"))
    print(json.dumps(vergleichen(daten, konfiguration["aufteilung"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ausfuehren()
