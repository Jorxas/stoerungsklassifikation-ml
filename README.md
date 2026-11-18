# Störungen mit messbarer Baseline klassifizieren

Stand: 17. November 2026 — **P13-T04 lokal abgeschlossen: drei beobachtete Baselinefehler und die künstlichen Daten erklärt**. Das ursprüngliche Basisziel vom 8. November und das Fortsetzungsziel vom 15. November wurden verfehlt; diese einzelne Phase wurde ausdrücklich für die jetzige Bearbeitung freigegeben. Geschätzter Basisaufwand: 3 Stunden ohne Einrichtung und Erweiterungen.

Ein Team möchte synthetische Störungsmeldungen klassifizieren und Training von Auswertung trennen.

Ergebnis: Datenvorbereitung, Mehrheitsbaseline, kleiner Klassifikator und getrennte Auswertung.

Vorgesehene Technologien: Python, Pandas, NumPy, Machine learning, scikit-learn. Eine Nennung ist kein Nachweis einer Umsetzung.

## Geprüfter erster Abschnitt

60 unveränderte synthetische Meldungen mit eindeutigen Kennungen S1 bis S60. Die feste Aufteilung in projekt.json verwendet S1 bis S42 für Training und S43 bis S60 für Test. Die Kennungslisten sind disjunkt und vollständig; je Klasse liegen 14 Trainings- und sechs Testmeldungen vor. Die Auswahl hängt nicht von der Dateireihenfolge ab.

Der [Konsistenzcheck](nachweise/P13-T01-pruefen.py) wurde in T01 ausgeführt; sein [Ergebnis](nachweise/P13-T01-pruefung.json) enthält Zeitpunkt und Prüfsummen. Sechs Meldungstexte kommen in beiden Teilmengen vor: Getrennte Kennungen ergeben hier keine unabhängige Prüfung neuer Texte. Planung und Grenzen stehen im [Versuchsplan](VERSUCHSPLAN.md).

## Geprüftes Training — P13-T02

Die [Pipeline](src/trainieren.py) verwendet TF-IDF-Textmerkmale und MultinomialNB mit alpha=1.0. Erst feste Kennungen trennen, danach Wortschatz, IDF und Klassifikator ausschließlich auf S1 bis S42 anpassen. Tatsächlich gelernt: 13 Textmerkmale und 14 Trainingsfälle je Klasse. Das Modell bleibt im Arbeitsspeicher.

Die [lokale Abnahme](nachweise/P13-T02-pruefen.py) protokolliert die tatsächlichen Anpassungsaufrufe. Geänderte Testtexte und Testklassen sowie umgekehrte Dateireihenfolge beeinflussen die gelernten Parameter nicht; überlappende Kennungen werden vor der Anpassung abgewiesen. Alle 60 synthetischen Quelldatensätze bleiben unverändert. [Neuer Ergebnisnachweis](nachweise/P13-T02-pruefung-2026-11-09.json) und [Befehle samt Wiederholungsdateien](nachweise/P13-T02-wiederaufnahme-2026-11-09.md).

T02 endete ohne Baseline, Testvorhersage oder Güteberechnung. Der folgende Abschnitt dokumentiert die getrennte Auswertung in T03; übergreifende Lastenheftkriterien werden hier nicht abgehakt.

## Geprüfte Auswertung — P13-T03

Die [Auswertung](src/auswerten.py) verwendet unverändert die feste Aufteilung und Trainingspipeline. Die Trainingsklassen sind gleich häufig; die vorab festgelegte alphabetische Regel wählt deshalb „anwendung“ als Mehrheitsbaseline. Auf denselben 18 Testfällen erreicht die Baseline 6/18 Treffer (33,33 %), das Modell 18/18 (100 %). [Ausgeführte Abnahme mit beiden Matrizen und allen Vorhersagen](nachweise/P13-T03-pruefung-2026-11-11.json).

Zeilen der Konfusionsmatrizen sind die tatsächlichen Klassen, Spalten die Vorhersagen, jeweils in der Reihenfolge anwendung, netzwerk, zugriff. Baseline: `[[6,0,0],[6,0,0],[6,0,0]]`; Modell: `[[6,0,0],[0,6,0],[0,0,6]]`. Die zwölf Baselinefehler betreffen sämtliche Netzwerk- und Zugriffsfälle. Beispiel S43: „Verbindung zum Demorechner nicht möglich unspezifischer Fehler“, tatsächlich netzwerk, Baseline anwendung, Modell netzwerk. Die Baseline ignoriert den Meldungstext. Beim Modell wurden keine Fehler beobachtet; es wird kein Modellfehler erfunden.

Alle 18 Testfälle verwenden einen der sechs bereits im Training vorhandenen Texte. Disjunkte Kennungen ergeben damit keine unabhängige Bewertung neuer Texte; 100 % belegen keine industrielle Übertragbarkeit. Keine Modelloptimierung anhand der Testdaten vorgenommen und keine Daten hinzugefügt. [Wiederholbare Befehle, Fehleranalyse und benötigte Dateien](nachweise/P13-T03-abnahme-2026-11-11.md). Die übergreifende Gesamtabnahme bleibt offen.

## Dokumentierte Grenzen — P13-T04

Die [lokale Abnahme](nachweise/P13-T04-pruefen.py) führt den unveränderten Vergleich erneut aus. Drei tatsächlich beobachtete Fehler der Mehrheitsbaseline:

| Kennung | Meldung | Soll | Baseline | Modell |
|---|---|---|---|---|
| S43 | Verbindung zum Demorechner nicht möglich unspezifischer Fehler | netzwerk | anwendung | netzwerk |
| S44 | Zugriff auf Demoverzeichnis verweigert | zugriff | anwendung | zugriff |
| S50 | Zugriff auf Demoverzeichnis verweigert unspezifischer Fehler | zugriff | anwendung | zugriff |

Alle drei Fälle haben dieselbe methodische Ursache: Die Baseline ignoriert den Text und sagt bei 14 Trainingsfällen je Klasse durch alphabetischen Gleichstand immer anwendung voraus. S43 zeigt eine Netzwerkmeldung, S44 eine Zugriffsmeldung, S50 eine Zugriffsmeldung mit unspezifischem Zusatz; der Zusatz ändert die konstante Baseline nicht. Dies sind drei Fehlerfälle, keine drei unabhängigen Fehlerursachen. Beim Modell weiterhin kein Fehler beobachtet.

Die 60 Meldungen sind vollständig synthetisch und als solche markiert, je Klasse 20. Sie enthalten nur sechs unterschiedliche Texte: drei einfache Demomeldungen, jeweils mit oder ohne „unspezifischer Fehler“. Alle 18 Testfälle wiederholen Trainingstexte. Das Modell kann diese wiederkehrenden Formulierungen zuordnen; die gemessenen 100 % prüfen keine unbekannten Formulierungen, realen Klassenhäufigkeiten oder betrieblichen Störungen. Es liegen keine echten Unternehmensdaten und kein Nachweis industrieller Übertragbarkeit vor. Eine Aufteilung nach Textgruppen oder neue Daten wären eigene spätere Arbeit und wurden nicht umgesetzt.

[Ergebnis mit drei Fällen, vollständigem Vergleich und Prüfsummen](nachweise/P13-T04-pruefung-2026-11-17.json), [Befehle und Wiederholungsdateien](nachweise/P13-T04-abnahme-2026-11-17.md). Nur der Dokumentationsendpunkt von T04 ist abgenommen; LASTENHEFT.md und die übergreifende Gesamtabnahme bleiben unverändert offen. Kein weiterer Produktzugang oder praktische Kompetenz in einer nicht ausgeführten Variante wird behauptet. Fertigstellung jetzt lokal, spätere Sicherung und Veröffentlichung getrennt durch den Koordinator.

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
