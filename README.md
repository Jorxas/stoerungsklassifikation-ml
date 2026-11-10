# Störungen mit messbarer Baseline klassifizieren

Stand: 9. November 2026 — **P13-T02 lokal abgeschlossen: Pipeline ausschließlich mit Trainingsdaten angepasst**. Baseline und Testauswertung bleiben offen. Das ursprüngliche Basisziel vom 8. November wurde verfehlt; der Fortsetzungsplan sieht offene Entwicklung bis 15. November vor. Geschätzter Basisaufwand: 3 Stunden ohne Einrichtung und Erweiterungen.

Ein Team möchte synthetische Störungsmeldungen klassifizieren und Training von Auswertung trennen.

Ergebnis: Datenvorbereitung, Mehrheitsbaseline, kleiner Klassifikator und getrennte Auswertung.

Vorgesehene Technologien: Python, Pandas, NumPy, Machine learning, scikit-learn. Eine Nennung ist kein Nachweis einer Umsetzung.

## Geprüfter erster Abschnitt

60 unveränderte synthetische Meldungen mit eindeutigen Kennungen S1 bis S60. Die feste Aufteilung in projekt.json verwendet S1 bis S42 für Training und S43 bis S60 für Test. Die Kennungslisten sind disjunkt und vollständig; je Klasse liegen 14 Trainings- und sechs Testmeldungen vor. Die Auswahl hängt nicht von der Dateireihenfolge ab.

Der [Konsistenzcheck](nachweise/P13-T01-pruefen.py) wurde in T01 ausgeführt; sein [Ergebnis](nachweise/P13-T01-pruefung.json) enthält Zeitpunkt und Prüfsummen. Sechs Meldungstexte kommen in beiden Teilmengen vor: Getrennte Kennungen ergeben hier keine unabhängige Prüfung neuer Texte. Planung und Grenzen stehen im [Versuchsplan](VERSUCHSPLAN.md).

## Geprüftes Training — P13-T02

Die [Pipeline](src/trainieren.py) verwendet TF-IDF-Textmerkmale und MultinomialNB mit alpha=1.0. Erst feste Kennungen trennen, danach Wortschatz, IDF und Klassifikator ausschließlich auf S1 bis S42 anpassen. Tatsächlich gelernt: 13 Textmerkmale und 14 Trainingsfälle je Klasse. Das Modell bleibt im Arbeitsspeicher.

Die [lokale Abnahme](nachweise/P13-T02-pruefen.py) protokolliert die tatsächlichen Anpassungsaufrufe. Geänderte Testtexte und Testklassen sowie umgekehrte Dateireihenfolge beeinflussen die gelernten Parameter nicht; überlappende Kennungen werden vor der Anpassung abgewiesen. Alle 60 synthetischen Quelldatensätze bleiben unverändert. [Neuer Ergebnisnachweis](nachweise/P13-T02-pruefung-2026-11-09.json) und [Befehle samt Wiederholungsdateien](nachweise/P13-T02-wiederaufnahme-2026-11-09.md).

Keine Baseline, Testvorhersage oder Güteberechnung ausgeführt. P13-T03 und die übergreifenden Lastenheftkriterien bleiben offen; industrielle Übertragbarkeit ist nicht belegt.

## Einstieg

Am 3. November war P13-T02 wegen fehlender Bibliotheken [blockiert](nachweise/P13-T02-blockade.md). Die spätere unterbrochene Bearbeitung hinterließ Pipeline und Prüfskript. Diese Teiländerungen wurden bei der Wiederaufnahme erhalten und am 9. November erneut lokal ausgeführt: Python 3.12.14, scikit-learn 1.9.1, Pandas 3.1.0, NumPy 2.5.4. Einzelheiten und getrennte Versuche stehen im [Arbeitsjournal](ARBEITSJOURNAL.md).

1. [Lastenheft](LASTENHEFT.md) lesen.
2. [Erstes Ticket](tickets/P13-T01.md) öffnen.
3. [Technischen Einstieg](START.md) prüfen und ein Ticket nach dem anderen bearbeiten.
4. [Arbeitsjournal](ARBEITSJOURNAL.md) und echte Nachweise aktualisieren.

Abhängigkeiten: keine weiteren Projekte.

[Erweiterungen](VARIANTEN.md) haben einen eigenen Umsetzungsstand. [Private Unternehmenszuordnung](UNTERNEHMEN.lokal.md) bleibt außerhalb der Git-Verwaltung.

## Projektsprache

Dokumentation, selbst gewählte Bezeichner, Kommentare, Meldungen und Beispieldaten werden auf Deutsch geschrieben. Festgelegte API-Schlüssel, Sprachsyntax und Produktnamen bleiben unverändert.
