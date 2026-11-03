# Versuchsplan vor dem Training

60 synthetische Störungen, absichtlich einfach und wenig repräsentativ. Reproduzierbare Aufteilung vor der Anpassung festlegen. Gegen eine Mehrheitsbaseline vergleichen, Kennzahlen auf zurückgehaltenen Testdaten berechnen und Fehlklassifikationen besprechen. Bei der Initialisierung ist noch keine erreichte Güte eingetragen.

## Festlegung vor dem Training — P13-T01

- Drei Klassen: anwendung, netzwerk und zugriff. Insgesamt 20 Meldungen je Klasse.
- Training: S1 bis S42; Test: S43 bis S60. Auswahl über feste Kennungslisten in projekt.json, unabhängig von der Dateireihenfolge. Kein Zufallszustand erforderlich.
- Die Mehrheitsbaseline zählt ausschließlich Trainingsklassen. Bei Gleichstand gilt die alphabetisch erste Bezeichnung; hier anwendung. Ihre spätere Bewertung nutzt dieselbe Testmenge wie das Modell.
- Noch keine Merkmale anpassen, kein Modell trainieren und keine Testgüte berechnen. Erst im jeweiligen Folgeticket tatsächlich ausführen.

## Beobachtete Grenzen

Der ausgeführte Konsistenzcheck bestätigt eindeutige und disjunkte Kennungen sowie vollständige Abdeckung. Er findet sechs identische Meldungstexte in beiden Teilmengen. Die spätere Auswertung beschreibt damit eine kleine künstliche Übung; sie belegt keine Verallgemeinerung auf neue Meldungen oder industrielle Daten. Eine spätere gruppierte Aufteilung nach Meldungstext wäre eine getrennte methodische Verbesserung und darf nicht rückwirkend als bereits erfolgt dargestellt werden.
