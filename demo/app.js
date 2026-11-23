(function () {
  "use strict";
  var T = window.INHALT;
  var lang = "de";
  var D = null; // Ausgabe des echten Laufs (daten/lauf.json)
  var nurFehler = false;
  var eingabe = "";

  var extra = [
    "Der Drucker im Büro druckt nicht",
    "Zugriff verweigert",
    "Anwendung abgestürzt",
    "Verbindung verloren"
  ];

  function $(id) { return document.getElementById(id); }
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function fmt(s) {
    var a = arguments;
    return s.replace(/\{(\d+)\}/g, function (_, i) { return a[+i + 1]; });
  }
  function cls(k) { return T[lang].klassen[k] || k; }
  function gloss(text) {
    if (lang === "de") return "";
    var g = T.fr.gloss;
    if (g[text]) return g[text];
    var suf = " unspezifischer Fehler";
    if (text.endsWith(suf) && g[text.slice(0, -suf.length)]) {
      return g[text.slice(0, -suf.length)] + ", " + g["unspezifischer Fehler"];
    }
    return "";
  }
  function textMitGloss(text) {
    var g = gloss(text);
    var s = el("span", { text: text });
    if (g) { s.appendChild(el("br")); s.appendChild(el("em", { class: "fine", text: g })); }
    return s;
  }
  function nf(opts) { return new Intl.NumberFormat(T[lang].locale, opts); }

  function renderStatic() {
    var t = T[lang];
    document.documentElement.lang = lang;
    document.title = t.titel;
    document.querySelectorAll("[data-i]").forEach(function (n) {
      var v = t[n.getAttribute("data-i")];
      if (typeof v === "string") n.textContent = v;
    });
    document.querySelectorAll(".langsw button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
    });
    $("beispiele").setAttribute("aria-label", t.beispieleLabel);
  }

  function renderDaten() {
    if (!D) return;
    var t = T[lang];
    var E = D.ergebnis;

    var tb = el("table");
    var cap = el("caption", { class: "sr", text: t.textenKopf });
    tb.appendChild(cap);
    var hr = el("tr");
    [t.spaltenText, t.spaltenGesamt, t.spaltenTraining, t.spaltenTest].forEach(function (h) { hr.appendChild(el("th", { scope: "col", text: h })); });
    tb.appendChild(el("thead", {}, [hr]));
    var body = el("tbody");
    D.verschiedeneTexte.forEach(function (r) {
      body.appendChild(el("tr", {}, [el("td", {}, [textMitGloss(r.text)]), el("td", { text: String(r.anzahl) }), el("td", { text: String(r.imTraining) }), el("td", { text: String(r.imTest) })]));
    });
    tb.appendChild(body);
    var tx = $("texte");
    tx.textContent = "";
    tx.appendChild(tb);

    var u = D.umgebung;
    var dt = new Intl.DateTimeFormat(t.locale, { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Berlin" }).format(new Date(D.zeit));
    $("laufmeta").textContent = fmt(t.laufmeta, dt, u.python, u["scikit-learn"], u.pandas, u.numpy);

    var pc = nf({ style: "percent", maximumFractionDigits: 1 });
    var kp = $("kpis");
    kp.textContent = "";
    [
      [E.baseline.treffer + " / " + E.baseline.testanzahl, t.kpiBase + " (" + pc.format(E.baseline.trefferanteil) + ")"],
      [E.modell.treffer + " / " + E.modell.testanzahl, t.kpiModell + " (" + pc.format(E.modell.trefferanteil) + ")"],
      [String(D.verschiedeneTexte.length), t.kpiTexte],
      [E.testfaelle_mit_bekanntem_text + " / " + E.modell.testanzahl, t.kpiBekannt]
    ].forEach(function (k) { kp.appendChild(el("div", { class: "kpi" }, [el("b", { text: k[0] }), el("span", { text: k[1] })])); });

    var mz = $("matrizen");
    mz.textContent = "";
    [[t.matrixBase, E.baseline], [t.matrixModell, E.modell]].forEach(function (par) {
      var k = E.klassenreihenfolge;
      var m = el("table", { class: "mx" });
      m.appendChild(el("caption", { text: fmt(t.matrixTitel, par[0]) }));
      var h = el("tr", {}, [el("th", { scope: "col", text: t.matrixKopf })]);
      k.forEach(function (c) { h.appendChild(el("th", { scope: "col", text: cls(c) })); });
      m.appendChild(el("thead", {}, [h]));
      var tbd = el("tbody");
      par[1].konfusionsmatrix.forEach(function (zeile, i) {
        var tr = el("tr", {}, [el("th", { scope: "row", text: cls(k[i]) })]);
        zeile.forEach(function (n, j) {
          var td = el("td", { text: String(n), class: i === j ? "diag" : "" });
          td.style.setProperty("--w", String(n / 6));
          tr.appendChild(td);
        });
        tbd.appendChild(tr);
      });
      m.appendChild(tbd);
      mz.appendChild(el("div", {}, [m]));
    });
    var mh = document.querySelector('[data-i="matrixHinweis"]');
    mh.textContent = fmt(t.matrixHinweis, E.baselineklasse);

    var nb = E.baseline.fehler.length;
    $("nurFehlerText").textContent = fmt(t.nurFehler, nb);
    var ul = $("faelle");
    ul.textContent = "";
    var basisMap = {};
    E.baseline.vorhersagen.forEach(function (f) { basisMap[f.id] = f; });
    E.modell.vorhersagen.forEach(function (f) {
      var b = basisMap[f.id];
      var bOk = b.vorhersage === f.soll, mOk = f.vorhersage === f.soll;
      if (nurFehler && bOk) return;
      function pill(label, klasse, ok) {
        return el("span", { class: "pill " + (ok ? "ok" : "bad") }, [
          label + ": " + cls(klasse) + " ",
          el("span", { class: ok ? "ok" : "bad", text: (ok ? "✓ " + t.richtig : "✗ " + t.falsch) })
        ]);
      }
      ul.appendChild(el("li", {}, [
        el("span", { class: "id", text: f.id }),
        textMitGloss(f.meldung),
        el("div", { class: "row2" }, [
          el("span", { class: "pill", text: t.soll + ": " + cls(f.soll) }),
          pill(t.baseline, b.vorhersage, bOk),
          pill(t.modell, f.vorhersage, mOk)
        ])
      ]));
    });

    var g = $("grenzen");
    g.textContent = "";
    t.grenzen.forEach(function (s) { g.appendChild(el("li", { text: s })); });

    $("befehl").textContent = "uv run --python 3.12 --with scikit-learn==1.9.1 --with pandas==3.1.0 --with numpy==2.5.4 python -X utf8 demo/erzeugen.py";

    var chips = $("beispiele");
    chips.textContent = "";
    var alle = D.verschiedeneTexte.map(function (r) { return r.text; }).concat(extra);
    alle.forEach(function (txt) {
      var b = el("button", { type: "button", class: "chip", "aria-pressed": String(txt === eingabe) });
      b.appendChild(textMitGloss(txt));
      b.addEventListener("click", function () { $("eingabe").value = txt; eingabe = txt; renderProbe(); renderChips(); });
      chips.appendChild(b);
    });
    renderProbe();
  }

  function renderChips() {
    document.querySelectorAll("#beispiele button").forEach(function (b) {
      var txt = b.firstChild.firstChild.textContent;
      b.setAttribute("aria-pressed", String(txt === eingabe));
    });
  }

  function renderProbe() {
    if (!D) return;
    var t = T[lang];
    var out = $("probeErg");
    out.textContent = "";
    if (!eingabe.trim()) { out.appendChild(el("p", { class: "fine", text: t.leer })); return; }
    var r = Klassifizierer.klassifizieren(D.modell, eingabe);
    var pc = nf({ style: "percent", maximumFractionDigits: 1 });
    out.appendChild(el("p", {}, [el("b", { text: t.ergKlasse + ": " }), el("span", { id: "vorhersage", "data-klasse": r.klasse, text: cls(r.klasse) })]));
    r.wahrscheinlichkeiten.forEach(function (p, i) {
      var k = D.modell.klassen[i];
      var fill = el("div", { class: "fill" });
      fill.style.width = (p * 100).toFixed(1) + "%";
      out.appendChild(el("div", { class: "bar" + (k === r.klasse ? " top" : "") }, [
        el("span", { text: cls(k) }), el("div", { class: "track" }, [fill]),
        el("span", { class: "pz", "data-klasse": k, text: pc.format(p) })
      ]));
    });
    var uniq = function (a) { return a.filter(function (x, i) { return a.indexOf(x) === i; }); };
    var kb = uniq(r.bekannt), ub = uniq(r.unbekannt);
    out.appendChild(el("p", { class: "fine" }, [el("b", { text: t.ergBekannt + ": " }), kb.length ? kb.join(", ") : t.keine]));
    out.appendChild(el("p", { class: "fine" }, [el("b", { text: t.ergUnbekannt + ": " }), ub.length ? ub.join(", ") : t.keine]));
    if (!kb.length) out.appendChild(el("p", { class: "note", text: t.keinBekannt }));
  }

  function setLang(l, push) {
    lang = l === "fr" ? "fr" : "de";
    if (push) {
      try {
        var u = new URL(location.href);
        if (lang === "fr") u.searchParams.set("lang", "fr"); else u.searchParams.delete("lang");
        history.replaceState(null, "", u.toString());
      } catch (e) { /* ohne Adressleiste weiter */ }
    }
    renderStatic();
    renderDaten();
  }

  document.querySelectorAll(".langsw button").forEach(function (b) {
    b.addEventListener("click", function () { setLang(b.getAttribute("data-lang"), true); });
  });
  $("nurFehler").addEventListener("change", function (e) { nurFehler = e.target.checked; renderDaten(); });
  $("eingabe").addEventListener("input", function (e) { eingabe = e.target.value; renderProbe(); renderChips(); });

  var start = "de";
  try { if (new URL(location.href).searchParams.get("lang") === "fr") start = "fr"; } catch (e) { /* Standard */ }
  setLang(start, false);

  fetch("daten/lauf.json").then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(function (d) {
    D = d;
    eingabe = d.verschiedeneTexte[0].text;
    $("eingabe").value = eingabe;
    renderDaten();
  }).catch(function (e) {
    var p = el("p", { class: "note", text: "daten/lauf.json: " + e.message });
    $("texte").appendChild(p);
  });
})();
