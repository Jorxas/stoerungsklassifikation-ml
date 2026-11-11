# Technischer Einstieg — P13

## Trainingspipeline ausführen

Im Projektordner mit dem vorhandenen Python 3.12 und den Bibliotheken im projektlokalen Cache:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 src/trainieren.py
~~~

Am 9. November tatsächlich ausgeführt: Python 3.12.14, scikit-learn 1.9.1, Pandas 3.1.0 und NumPy 2.5.4. `--offline` verhindert einen Netzwerkabruf; die Indexadresse identifiziert den vorhandenen Cache. Fehlen Pakete, ist die lokale Voraussetzung nicht erfüllt.

Die Pipeline trennt zuerst anhand der festen Kennungen in projekt.json. TF-IDF und MultinomialNB lernen ausschließlich aus 42 Trainingsfällen. Erwartete Ausgabe: Training abgeschlossen, 18 Testfälle ausgeschlossen, 13 gelernte Textmerkmale. Das Modell bleibt im Arbeitsspeicher; es wird keine Modelldatei benötigt.

## Begrenzte Abnahme für P13-T02

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 nachweise/P13-T02-pruefen.py
~~~

Erwartet: 60 unveränderte Beispieldatensätze, 42 Trainingsfälle mit 14 je Klasse; tatsächliche Anpassungsaufrufe nur mit Trainingsdaten. Geänderte Testinhalte und umgekehrte Dateireihenfolge lassen Wortschatz, IDF und Modellparameter unverändert. Überlappende Kennungen werden vor jeder Anpassung abgewiesen. Änderungen der Testdaten erfolgen nur in Speicherkopien.

Der Check schreibt [P13-T02-pruefung-2026-11-09.json](nachweise/P13-T02-pruefung-2026-11-09.json). Eine Wiederholung ersetzt diesen Ergebnisnachweis mit ihrem tatsächlichen Zeitpunkt. Der vom unterbrochenen Versuch hinterlassene Nachweis P13-T02-pruefung.json bleibt erhalten. [Alle benötigten Projekt- und Prüfdateien sowie Befehlsausgaben](nachweise/P13-T02-wiederaufnahme-2026-11-09.md).

## Stand und Grenze

Die [Voraussetzungenprüfung vom 3. November](nachweise/P13-T02-blockade.md) endete blockiert. Eine spätere unterbrochene Bearbeitung hinterließ Teiländerungen; laut übergebener Startanleitung endete der Lauf vom 4. November mit „workspace routing discovery failed“. Am 9. November wurden die Bibliotheken [offline importiert](nachweise/P13-T02-voraussetzungen-bereit-2026-11-09.json) und anschließend Pipeline und Abnahme tatsächlich ausgeführt.

Damit war am 9. November nur P13-T02 beendet. Die gesonderte Auswertung vom 11. November steht im folgenden Abschnitt. Keine Lastenheftkriterien zusätzlich abgehakt. Frühere Versuche und Fertigstellungen stehen getrennt im [Journal](ARBEITSJOURNAL.md).

## Auswertung und begrenzte Abnahme — P13-T03

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 src/auswerten.py
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 nachweise/P13-T03-pruefen.py
~~~

Der erste Befehl gibt den Vergleich als JSON aus. Der zweite prüft Daten- und Pipelineerhalt, dieselben 18 Testkennungen, Trainingsmehrheit, Matrixachsen, Treffer und Fehlerlisten. Zwei absichtlich falsche Vorhersagen dienen ausschließlich als Gegenprobe der Auswertungsfunktion; sie sind keine beobachteten Modellfehler. Testklassen werden zusätzlich nur in Speicherkopien geändert und die Dateireihenfolge umgekehrt; die Vorhersagen bleiben gleich.

Beobachtet: Baseline 6/18, Modell 18/18; zwölf Baselinefehler, keine Modellfehler. Alle 18 Testtexte kommen schon im Training vor. Der Nachweis belegt diese synthetische Übung, keine Übertragbarkeit auf neue Meldungen. Versionen wie oben; keine neuen Pakete erforderlich.

Der Check schreibt [P13-T03-pruefung-2026-11-11.json](nachweise/P13-T03-pruefung-2026-11-11.json); Wiederholung ersetzt diesen Nachweis mit dem tatsächlichen neuen Zeitpunkt. [Befehle, Ausgaben, Analyse und vollständige Wiederholungsdateien](nachweise/P13-T03-abnahme-2026-11-11.md). P13-T04 wurde nicht begonnen. Sicherung und spätere Veröffentlichung durch den Koordinator bleiben getrennt von der lokalen Fertigstellung.
