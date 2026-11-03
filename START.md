# Technischer Einstieg — P13


## Einstiegspunkt ausführen

Voraussetzungen: Python 3; scikit-learn, Pandas und NumPy in einer eigenen Umgebung.

~~~powershell
python src/trainieren.py
~~~

Das Startprogramm meldet den Initialisierungsstand. Fachfunktionen sind bewusst noch nicht implementiert und melden dies bei einem Aufruf. Fehlende Bibliotheken und Frameworks erst im passenden Ticket mit ihrer tatsächlichen Version ergänzen.

## Nächste Aufgabe

P13-T01 erneut prüfen, ohne ein Modell zu trainieren; dafür genügt die Python-Standardbibliothek:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/P13-T01-pruefen.py
~~~

Der Check schreibt nachweise/P13-T01-pruefung.json. Erwartet: 60 eindeutige Kennungen, 42 Trainings- und 18 Testfälle, keine gemeinsame Kennung und sechs gemeinsame Meldungstexte. Anschließend erst im geplanten nächsten Abschnitt die Datenpipeline und das Modell entwickeln.

## Technische Quellen

- [Python-CSV-Modul](https://docs.python.org/3/library/csv.html)
- [Offizielle Angular-CLI-Anleitung](https://angular.dev/tools/cli/setup-local)
- [WPF mit .NET](https://learn.microsoft.com/de-de/dotnet/desktop/wpf/get-started/create-app-visual-studio)

Vor dem Einbinden eines Frameworks dessen aktuelle offizielle Anleitung lesen.
