// Browserprüfung der Demo. Der Ordner (Standard: demo/) wird wie auf GitHub Pages unter /stoerungsklassifikation-ml/ ausgeliefert.
// Braucht puppeteer-core (NODE_PATH) und einen installierten Chrome oder Edge (BROWSER_PFAD).
// Prüft: Deutsch als Standard, Wechsel zu Französisch und zurück (Schalter und ?lang=fr), keine Laufzeitfehler,
// keine externen Anfragen, kein waagerechtes Scrollen bei 390 px, Tastaturbedienung und die Rechnung im Browser
// gegen die Python-Referenz aus daten/lauf.json.
// Optional: --bild=<präfix> schreibt Aufnahmen (<präfix>-desktop-de.png, -handy-de.png, -handy-fr.png).
const fs = require("node:fs"), path = require("node:path"), http = require("node:http"), assert = require("node:assert/strict");
const puppeteer = require("puppeteer-core");
const ordner = path.resolve(process.argv.find(a => a.startsWith("--ordner="))?.slice(9) || path.join(__dirname, "../demo"));
const bild = process.argv.find(a => a.startsWith("--bild="))?.slice(7);
const REPO = "stoerungsklassifikation-ml";
const typen = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml" };
const server = http.createServer((q, r) => {
  let p = decodeURIComponent(new URL(q.url, "http://x").pathname);
  if (!p.startsWith("/" + REPO + "/")) { r.statusCode = 404; return r.end("nicht gefunden"); }
  p = p.slice(REPO.length + 1);
  if (p.endsWith("/")) p += "index.html";
  const f = path.join(ordner, p);
  if (!f.startsWith(ordner) || !fs.existsSync(f)) { r.statusCode = 404; return r.end("nicht gefunden"); }
  r.setHeader("Content-Type", typen[path.extname(f)] || "application/octet-stream");
  r.end(fs.readFileSync(f));
});
const browserPfad = process.env.BROWSER_PFAD || ["C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "/usr/bin/google-chrome", "/usr/bin/chromium"].find(f => fs.existsSync(f));
if (!browserPfad) throw new Error("BROWSER_PFAD auf einen installierten Chrome oder Edge setzen.");
const warte = ms => new Promise(r => setTimeout(r, ms));
const lauf = JSON.parse(fs.readFileSync(path.join(ordner, "daten/lauf.json"), "utf8"));

(async () => {
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  const basis = `http://127.0.0.1:${server.address().port}/${REPO}/`;
  const browser = await puppeteer.launch({ executablePath: browserPfad, headless: true });
  const fehler = [], extern = [];
  try {
    const s = await browser.newPage();
    s.on("pageerror", e => fehler.push("Seitenfehler: " + e.message));
    s.on("console", m => { if (["error", "warning"].includes(m.type())) fehler.push("Konsole: " + m.text()); });
    s.on("requestfailed", r => fehler.push("Anfrage fehlgeschlagen: " + r.url()));
    s.on("request", r => { if (!/^(data:|about:)/.test(r.url()) && new URL(r.url()).hostname !== "127.0.0.1") extern.push(r.url()); });
    s.on("response", r => { if (r.status() >= 400) fehler.push("HTTP " + r.status() + " " + r.url()); });
    await s.setViewport({ width: 1280, height: 900 });
    const text = () => s.$eval("body", e => e.innerText);
    const lang = () => s.$eval("html", e => e.lang);
    const kein = async (name) => assert(!(await s.evaluate(() => document.documentElement.scrollWidth > innerWidth)), "kein waagerechter Überlauf: " + name);

    // 1. Deutsch ist Standard
    await s.goto(basis, { waitUntil: "networkidle0" });
    await s.waitForSelector("#faelle li");
    assert.equal(await lang(), "de", "html lang ist de");
    assert((await s.$eval("h1", e => e.textContent)).includes("Störungsmeldungen automatisch zuordnen"), "Überschrift deutsch");
    assert((await text()).includes("Ausgabe eines echten Laufs des Projekts"), "Kennzeichnung echter Lauf");
    assert.equal(await s.$$eval("#faelle li", l => l.length), 18, "18 Testfälle");
    assert.equal(await s.$eval('.langsw [data-lang="de"]', e => e.getAttribute("aria-pressed")), "true");
    assert((await s.$eval("#kpis", e => e.innerText)).includes("6 / 18") && (await s.$eval("#kpis", e => e.innerText)).includes("18 / 18"), "Kennzahlen 6/18 und 18/18");
    assert((await s.$eval("#kpis", e => e.innerText)).includes("33,3"), "deutsches Prozentformat");
    assert(!/[–—]/.test(await text()), "keine Gedankenstriche im sichtbaren Text");
    // Zahlen der Seite stimmen mit dem erfassten Lauf überein
    assert.equal(lauf.ergebnis.baseline.treffer, 6); assert.equal(lauf.ergebnis.modell.treffer, 18);
    // Filter
    await s.click("#nurFehler");
    assert.equal(await s.$$eval("#faelle li", l => l.length), 12, "12 Baselinefehler");
    await s.click("#nurFehler");
    assert.equal(await s.$$eval("#faelle li", l => l.length), 18);
    if (bild) await s.screenshot({ path: path.resolve(bild + "-desktop-de.png"), fullPage: true });

    // 2. Rechnung im Browser gegen scikit-learn
    const pc = new Intl.NumberFormat("de-DE", { style: "percent", maximumFractionDigits: 1 });
    for (const ref of lauf.referenz.filter(r => r.text.trim())) {
      await s.$eval("#eingabe", e => { e.value = ""; });
      await s.type("#eingabe", ref.text);
      await warte(30);
      const klasse = await s.$eval("#vorhersage", e => e.dataset.klasse);
      assert.equal(klasse, ref.klasse, "Klasse für: " + ref.text);
      const pz = await s.$$eval(".pz", l => l.map(e => e.textContent));
      assert.deepEqual(pz, ref.wahrscheinlichkeiten.map(p => pc.format(p)), "Wahrscheinlichkeiten für: " + ref.text);
    }
    await s.$eval("#eingabe", e => { e.value = ""; });
    await s.type("#eingabe", "Anwendung abgestürzt");
    assert((await text()).includes("Kein Wort der Meldung steht im Wortschatz"), "Hinweis bei unbekannten Wörtern");

    // 3. Tastatur: Sprachschalter per Tab und Enter
    await s.goto(basis, { waitUntil: "networkidle0" });
    await s.keyboard.press("Tab"); await s.keyboard.press("Tab");
    assert.equal(await s.evaluate(() => document.activeElement.dataset.lang), "fr", "FR-Schalter per Tastatur erreichbar");
    await s.keyboard.press("Enter");
    assert.equal(await lang(), "fr", "Wechsel per Tastatur");
    assert((await s.$eval("h1", e => e.textContent)).includes("Classer automatiquement"), "Überschrift französisch");
    assert((await s.evaluate(() => location.search)).includes("lang=fr"), "URL enthält lang=fr");
    assert((await text()).includes("Sortie d'une vraie exécution du projet"), "Kennzeichnung französisch");
    assert(!(await text()).includes("Ausgabe eines echten Laufs"), "kein deutscher Rest in der Kennzeichnung");
    assert((await s.$eval("#kpis", e => e.innerText)).includes("33,3"), "französisches Prozentformat mit Komma");
    assert.equal(await s.$$eval("#faelle li", l => l.length), 18, "Testfälle auch auf Französisch");
    assert(!/[–—]/.test(await text()), "keine Gedankenstriche (fr)");
    // deutsche Wörter der Oberfläche dürfen auf Französisch nicht stehen bleiben
    const frText = await s.$eval("main", e => e.innerText);
    for (const w of ["Aufgabe", "Ergebnis", "Grenzen", "Konfusionsmatrix", "Eigene Meldung", "Mehrheitsbaseline"]) assert(!frText.includes(w), "deutsches Wort auf Französisch: " + w);
    await kein("fr desktop");
    // zurück zu Deutsch
    await s.click('.langsw [data-lang="de"]');
    assert.equal(await lang(), "de", "zurück zu Deutsch");
    assert(!(await s.evaluate(() => location.search)).includes("lang=fr"), "lang=fr entfernt");
    assert((await s.$eval("h1", e => e.textContent)).includes("automatisch zuordnen"));

    // 4. ?lang=fr direkt
    await s.goto(basis + "?lang=fr", { waitUntil: "networkidle0" });
    await s.waitForSelector("#faelle li");
    assert.equal(await lang(), "fr", "?lang=fr");
    assert.equal(await s.$eval('.langsw [data-lang="fr"]', e => e.getAttribute("aria-pressed")), "true");

    // 5. Handy 390 px, beide Sprachen
    await s.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
    await s.goto(basis, { waitUntil: "networkidle0" });
    await s.waitForSelector("#faelle li");
    await kein("de 390");
    if (bild) await s.screenshot({ path: path.resolve(bild + "-handy-de.png"), fullPage: true });
    await s.click('.langsw [data-lang="fr"]');
    await warte(100);
    await kein("fr 390");
    if (bild) await s.screenshot({ path: path.resolve(bild + "-handy-fr.png"), fullPage: true });
    await s.type("#eingabe", " Verbindung zum Demorechner nicht möglich und noch ein sehr langes Wort ".repeat(3));
    await kein("fr 390 lange Eingabe");
  } finally { await browser.close(); server.close(); }
  assert.deepEqual(fehler, [], "keine Laufzeitfehler: " + fehler.join(" | "));
  assert.deepEqual(extern, [], "keine externen Anfragen");
  console.log("Browserprüfung bestanden: Deutsch als Standard, Wechsel zu Französisch und zurück, ?lang=fr, Tastatur, Rechnung gegen scikit-learn-Referenz, 390 px ohne waagerechtes Scrollen; keine Fehler, keine externen Anfragen.");
})().catch(e => { console.error(e); process.exitCode = 1; server.close(); });
