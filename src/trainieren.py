"""P13-T02: Textmerkmale und Klassifikator ausschließlich im Training anpassen."""

import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


PROJEKTORDNER = Path(__file__).resolve().parents[1]


def daten_aufteilen(daten, aufteilung):
    """Feste Kennungslisten vor jeder lernenden Verarbeitung anwenden."""
    tabelle = pd.DataFrame(daten).set_index("id")
    if not tabelle.index.is_unique:
        raise ValueError("Jede Störung benötigt eine eindeutige Kennung.")
    training = aufteilung["training"]
    test = aufteilung["test"]
    if (len(tabelle) != 60 or len(training) != 42 or len(test) != 18
            or len(set(training)) != 42 or len(set(test)) != 18
            or set(training) & set(test)
            or set(training) | set(test) != set(tabelle.index)):
        raise ValueError("Erwartet: 60 eindeutige Fälle, disjunkt in 42 Training und 18 Test.")
    if not tabelle["synthetisch"].map(lambda wert: wert is True).all():
        raise ValueError("Nur synthetische Beispieldaten sind zulässig.")
    return tabelle.loc[training].copy(), tabelle.loc[test].copy()


def modell_trainieren(daten, aufteilung):
    training, _ = daten_aufteilen(daten, aufteilung)
    if not training["meldung"].map(
            lambda text: isinstance(text, str) and bool(text.strip())).all():
        raise ValueError("Jede Trainingsmeldung muss einen nichtleeren Text enthalten.")
    if not training["klasse"].isin(["anwendung", "netzwerk", "zugriff"]).all():
        raise ValueError("Eine Trainingsklasse ist unbekannt.")
    pipeline = Pipeline([
        ("textmerkmale", TfidfVectorizer()),
        ("klassifikator", MultinomialNB(alpha=1.0)),
    ])
    # Wortschatz, IDF-Gewichte und Klassifikator lernen nur aus diesen 42 Zeilen.
    pipeline.fit(training["meldung"].tolist(), training["klasse"].tolist())
    return pipeline


def ausfuehren():
    konfiguration = json.loads((PROJEKTORDNER / "projekt.json").read_text(encoding="utf-8"))
    daten = json.loads((PROJEKTORDNER / konfiguration["fixture"]).read_text(encoding="utf-8"))
    pipeline = modell_trainieren(daten, konfiguration["aufteilung"])
    print("Training abgeschlossen: 42 Trainingsfälle; 18 Testfälle von der Anpassung ausgeschlossen.")
    print(f"Gelernte Textmerkmale: {len(pipeline.named_steps['textmerkmale'].vocabulary_)}.")
    print("Modell nur im Arbeitsspeicher; keine Baseline, Testvorhersage oder Güteberechnung.")


if __name__ == "__main__":
    ausfuehren()
