"""Ausgabekonsistenz und Git-Formatprüfung ohne Git-Schreiboperationen."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess

PROJEKTORDNER = Path(__file__).resolve().parents[1]

pruefung = json.loads((PROJEKTORDNER / "nachweise/P13-T03-pruefung-2026-11-11.json").read_text(encoding="utf-8"))
ausgabe = json.loads((PROJEKTORDNER / "nachweise/P13-T03-auswertung-2026-11-11.json").read_text(encoding="utf-8-sig"))
if ausgabe != pruefung["auswertung"]:
    raise ValueError("Direkte Ausgabe und geprüfte Auswertung unterscheiden sich.")
for pfad, erwartet in pruefung["dateien_sha256"].items():
    if hashlib.sha256((PROJEKTORDNER / pfad).read_bytes()).hexdigest() != erwartet:
        raise ValueError(f"Prüfeingabe nach der Abnahme verändert: {pfad}")
formatpruefung = subprocess.run(["git", "diff", "--check", "--", "."], cwd=PROJEKTORDNER,
                               capture_output=True, text=True, encoding="utf-8", check=True)
nachweis = {
    "zeitpunkt": datetime.now().astimezone().isoformat(timespec="seconds"),
    "ergebnis": "bestanden",
    "direkte_ausgabe_gleich_abnahme": True,
    "eingabepruefsummen_unveraendert": True,
    "befehl": "git diff --check -- .",
    "exitcode": formatpruefung.returncode,
    "ausgabe": formatpruefung.stdout + formatpruefung.stderr,
}
(PROJEKTORDNER / "nachweise/P13-T03-formatpruefung-2026-11-11.json").write_text(
    json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Bestanden: direkte Ausgabe gleich Abnahme; Eingabeprüfsummen unverändert; git diff --check -- . erfolgreich.")
