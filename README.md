# Störungen mit messbarer Baseline klassifizieren

Stand: 1. November 2026 — **erste Phase geprüft; Modelltraining und Auswertung offen**. Geplanter Abschluss der Basis: 8. November 2026. Geschätzter Basisaufwand: 3 Stunden ohne Einrichtung und Erweiterungen.

Ein Team möchte synthetische Störungsmeldungen klassifizieren und Training von Auswertung trennen.

Ergebnis: Datenvorbereitung, Mehrheitsbaseline, kleiner Klassifikator und getrennte Auswertung.

Vorgesehene Technologien: Python, Pandas, NumPy, Machine learning, scikit-learn. Eine Nennung ist kein Nachweis einer Umsetzung.

## Geprüfter erster Abschnitt

60 unveränderte synthetische Meldungen mit eindeutigen Kennungen S1 bis S60. Die feste Aufteilung in projekt.json verwendet S1 bis S42 für Training und S43 bis S60 für Test. Die Kennungslisten sind disjunkt und vollständig; je Klasse liegen 14 Trainings- und sechs Testmeldungen vor. Die Auswahl hängt nicht von der Dateireihenfolge ab.

Der [Konsistenzcheck](nachweise/P13-T01-pruefen.py) wurde ausgeführt; sein [Ergebnis](nachweise/P13-T01-pruefung.json) enthält Zeitpunkt und Prüfsummen. Sechs Meldungstexte kommen in beiden Teilmengen vor: Getrennte Kennungen ergeben hier keine unabhängige Prüfung neuer Texte. Kein Modell wurde trainiert und keine Güte berechnet. Planung und Grenzen stehen im [Versuchsplan](VERSUCHSPLAN.md).

## Einstieg

1. [Lastenheft](LASTENHEFT.md) lesen.
2. [Erstes Ticket](tickets/P13-T01.md) öffnen.
3. [Technischen Einstieg](START.md) prüfen und ein Ticket nach dem anderen bearbeiten.
4. [Arbeitsjournal](ARBEITSJOURNAL.md) und echte Nachweise aktualisieren.

Abhängigkeiten: keine weiteren Projekte.

[Erweiterungen](VARIANTEN.md) haben einen eigenen Umsetzungsstand. [Private Unternehmenszuordnung](UNTERNEHMEN.lokal.md) bleibt außerhalb der Git-Verwaltung.

## Projektsprache

Dokumentation, selbst gewählte Bezeichner, Kommentare, Meldungen und Beispieldaten werden auf Deutsch geschrieben. Festgelegte API-Schlüssel, Sprachsyntax und Produktnamen bleiben unverändert.
