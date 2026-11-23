/* Rechnet die Vorhersage des im Projekt trainierten Modells nach (TF-IDF, Multinomial Naive Bayes).
   Alle Zahlen kommen aus daten/lauf.json (echter scikit-learn-Lauf); hier wird nur angewendet,
   nicht trainiert. Gleiche Schritte wie scikit-learn: Kleinbuchstaben, Token mit mindestens zwei
   Wortzeichen, Häufigkeit mal IDF, L2-Norm, gewichtete Summe der logarithmierten Wahrscheinlichkeiten
   plus Klassenprior, Softmax. */
(function (global) {
  "use strict";
  function tokens(text) {
    return (String(text).toLowerCase().match(/[\p{L}\p{N}_]{2,}/gu)) || [];
  }
  function klassifizieren(modell, text) {
    var index = {};
    modell.wortschatz.forEach(function (w, i) { index[w] = i; });
    var toks = tokens(text);
    var anzahl = {};
    var bekannt = [], unbekannt = [];
    toks.forEach(function (t) {
      if (Object.prototype.hasOwnProperty.call(index, t)) {
        anzahl[index[t]] = (anzahl[index[t]] || 0) + 1;
        bekannt.push(t);
      } else {
        unbekannt.push(t);
      }
    });
    var gewichte = {}, norm = 0;
    Object.keys(anzahl).forEach(function (i) {
      var w = anzahl[i] * modell.idf[i];
      gewichte[i] = w;
      norm += w * w;
    });
    norm = Math.sqrt(norm);
    var log = modell.klassen.map(function (_, c) {
      var s = modell.klassenLogPrior[c];
      Object.keys(gewichte).forEach(function (i) {
        s += (gewichte[i] / (norm || 1)) * modell.featureLogProb[c][i];
      });
      return s;
    });
    var max = Math.max.apply(null, log);
    var e = log.map(function (x) { return Math.exp(x - max); });
    var summe = e.reduce(function (a, b) { return a + b; }, 0);
    var p = e.map(function (x) { return x / summe; });
    var best = 0;
    log.forEach(function (x, i) { if (x > log[best]) best = i; });
    return { klasse: modell.klassen[best], wahrscheinlichkeiten: p, bekannt: bekannt, unbekannt: unbekannt, token: toks };
  }
  var api = { klassifizieren: klassifizieren, tokens: tokens };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else global.Klassifizierer = api;
})(typeof window !== "undefined" ? window : globalThis);
