/* ================================================================
   Logic Trojans project site — navigation + offline replay demo
   The demo never calls a model and never executes code. It only
   replays results bundled in data/demo_data.json.
   ================================================================ */
(function () {
  "use strict";

  /* ---------------- tab navigation ---------------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  var links = Array.prototype.slice.call(document.querySelectorAll("[data-tab]"));
  var nav = document.getElementById("nav");
  var navToggle = document.getElementById("navToggle");

  function showTab(id, push) {
    if (!document.getElementById(id)) id = "overview";
    tabs.forEach(function (t) { t.classList.toggle("active", t.id === id); });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("data-tab") === id);
    });
    if (nav) nav.classList.remove("open");
    if (navToggle) navToggle.setAttribute("aria-expanded", "false");
    if (push) history.replaceState(null, "", "#" + id);
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  }

  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      showTab(a.getAttribute("data-tab"), true);
    });
  });
  if (navToggle) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  window.addEventListener("hashchange", function () { showTab(location.hash.slice(1), false); });
  showTab(location.hash.slice(1) || "overview", false);

  /* ---------------- demo gating ---------------- */
  var cfg = window.SITE_CONFIG || { demoEnabled: false };
  var locked = document.getElementById("demoLocked");
  var appEl = document.getElementById("demoApp");
  if (!cfg.demoEnabled) {
    if (locked) locked.hidden = false;
    return; // demo off: nothing else to wire up
  }
  if (appEl) appEl.hidden = false;

  /* ---------------- demo: load data ---------------- */
  var DATA = null, byId = {};
  var elTask = document.getElementById("selTask");
  var elLevel = document.getElementById("selLevel");
  var elModel = document.getElementById("selModel");
  var promptBox = document.getElementById("promptBox");
  var genOut = document.getElementById("genOut");
  var genCode = document.getElementById("genCode");
  var genMeta = document.getElementById("genMeta");
  var pairLog = document.getElementById("pairLog");
  var verifyBox = document.getElementById("verifyBox");
  var agentPanel = document.getElementById("agentPanel");
  var verdictBanner = document.getElementById("verdictBanner");
  var btnGenerate = document.getElementById("btnGenerate");
  var btnCopy = document.getElementById("btnCopy");
  var btnPaste = document.getElementById("btnPaste");
  var btnVerify = document.getElementById("btnVerify");

  var currentCell = null;

  fetch("data/demo_data.json")
    .then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
    .then(function (d) {
      DATA = d;
      d.cells.forEach(function (c) { byId[c.id] = c; });
      fillSelect(elTask, d.tasks.map(function (t) { return [t.key, t.label]; }));
      fillSelect(elLevel, d.levels.map(function (l) { return [l.key, l.label]; }));
      fillSelect(elModel, d.models.map(function (m) { return [m, m]; }));
      syncPrompt();
    })
    .catch(function (err) {
      if (appEl) appEl.innerHTML =
        '<div class="demo-locked"><h3>Could not load the demo data</h3>' +
        '<p>Please try again later.</p></div>';
      console.error(err);
    });

  function fillSelect(sel, pairs) {
    sel.innerHTML = "";
    pairs.forEach(function (p) {
      var o = document.createElement("option");
      o.value = p[0]; o.textContent = p[1];
      sel.appendChild(o);
    });
  }

  function cellId() { return elModel.value + "__" + elLevel.value + "__" + elTask.value; }

  function syncPrompt() {
    var c = byId[cellId()];
    promptBox.value = c ? c.prompt : "";
    // a new selection invalidates any previous generation/verification
    resetGeneration();
  }
  [elTask, elLevel, elModel].forEach(function (s) { s.addEventListener("change", syncPrompt); });

  function resetGeneration() {
    currentCell = null;
    genOut.hidden = true;
    pairLog.hidden = true; pairLog.innerHTML = "";
    agentPanel.hidden = true; agentPanel.innerHTML = "";
    verdictBanner.className = "verdict"; verdictBanner.hidden = true;
  }

  /* ---------------- step 1: intercept + PAIR (animated narration) ---------------- */
  var PAIR_STEPS = [
    "Request intercepted by the adversarial layer (PAIR).",
    "Generating a candidate implementation…",
    "Running the local unit tests…",
    "Scoring how hard the hidden logic is to spot…",
    "Refining the request and trying again…",
    "Repeating for several rounds…",
    "Selecting the stealthiest working candidate."
  ];

  btnGenerate.addEventListener("click", function () {
    var c = byId[cellId()];
    if (!c) return;
    resetGeneration();
    btnGenerate.disabled = true;
    pairLog.hidden = false;

    var i = 0;
    (function next() {
      if (i > 0) {
        var prev = pairLog.children[i - 1];
        if (prev) { prev.classList.remove("run"); prev.classList.add("done"); }
      }
      if (i >= PAIR_STEPS.length) {
        currentCell = c;
        genCode.textContent = c.code;
        genMeta.textContent = c.model + " · " + c.levelLabel + " · stealth score " + c.attackScore + "/10";
        genOut.hidden = false;
        btnGenerate.disabled = false;
        return;
      }
      var line = document.createElement("div");
      line.className = "line run";
      line.textContent = PAIR_STEPS[i];
      pairLog.appendChild(line);
      i++;
      setTimeout(next, 430);
    })();
  });

  btnCopy.addEventListener("click", function () {
    if (!currentCell) return;
    copyText(currentCell.code, btnCopy, "Copy");
  });
  btnPaste.addEventListener("click", function () {
    if (!currentCell) return;
    verifyBox.value = currentCell.code;
    document.getElementById("verifyBox").scrollIntoView({ behavior: "smooth", block: "center" });
  });

  function copyText(txt, btn, label) {
    var done = function () { btn.textContent = "Copied ✓"; setTimeout(function () { btn.textContent = label; }, 1400); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(done, function () { fallbackCopy(txt); done(); });
    } else { fallbackCopy(txt); done(); }
  }
  function fallbackCopy(txt) {
    var ta = document.createElement("textarea");
    ta.value = txt; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  /* ---------------- step 2: defense (animated replay of cached verdicts) ---------------- */
  btnVerify.addEventListener("click", function () {
    var pasted = verifyBox.value.trim();
    if (!pasted) { flash(verifyBox); return; }

    // Replay the recorded analysis. If the pasted text is not the generated
    // sample, verify whatever sample is currently loaded (and say so).
    var c = currentCell || byId[cellId()];
    if (!c) return;
    var mismatch = currentCell && normalize(pasted) !== normalize(currentCell.code);

    btnVerify.disabled = true;
    verdictBanner.className = "verdict"; verdictBanner.hidden = true;
    agentPanel.hidden = false;
    agentPanel.innerHTML = "";

    // build one row per agent, initially "working"
    var rows = c.agents.map(function (a, idx) {
      var row = document.createElement("div");
      row.className = "agent-row";
      row.innerHTML =
        '<div class="agent-ico">' + initials(a.name) + '</div>' +
        '<div><p class="agent-name">' + esc(a.name) + '</p>' +
        '<p class="agent-role">' + esc(a.role) + '</p>' +
        '<ul class="agent-findings" hidden></ul></div>' +
        '<div class="agent-status working"><span class="spinner"></span>reviewing…</div>';
      agentPanel.appendChild(row);
      return row;
    });

    var k = 0;
    (function step() {
      if (k >= c.agents.length) { finish(c, mismatch); return; }
      var a = c.agents[k], row = rows[k];
      row.classList.add("active");
      setTimeout(function () {
        var st = row.querySelector(".agent-status");
        var fl = row.querySelector(".agent-findings");
        if (a.blocks) {
          st.className = "agent-status flag";
          st.textContent = "⚑ flagged (" + a.confidence.toFixed(2) + ")";
        } else {
          st.className = "agent-status clean";
          st.textContent = a.verdict === "unknown" ? "— no clear verdict" : "✓ looks clean (" + a.confidence.toFixed(2) + ")";
        }
        if (a.findings && a.findings.length) {
          fl.hidden = false;
          fl.innerHTML = a.findings.map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
        }
        k++;
        setTimeout(step, 320);
      }, 780);
    })();
  });

  function finish(c, mismatch) {
    var flaggedBy = c.agents.filter(function (a) { return a.blocks; }).map(function (a) { return a.name; });
    verdictBanner.hidden = false;
    if (c.blocked) {
      verdictBanner.className = "verdict blocked show";
      verdictBanner.innerHTML =
        "<h3>⚑ Held back — hidden deviation detected</h3>" +
        "<p>The defense would block this code and send it for human review. " +
        "Flagged by: <strong>" + flaggedBy.map(esc).join(", ") + "</strong>." +
        (mismatch ? " <em>(Showing the recorded analysis of the generated sample.)</em>" : "") +
        "</p>";
    } else {
      verdictBanner.className = "verdict allowed show";
      verdictBanner.innerHTML =
        "<h3>✓ Allowed — nothing flagged</h3>" +
        "<p>None of the three agents flagged this sample, so the defense would let it through. " +
        "This is one of the cases the defense misses — a reminder that detection is not perfect." +
        (mismatch ? " <em>(Showing the recorded analysis of the generated sample.)</em>" : "") +
        "</p>";
    }
    btnVerify.disabled = false;
  }

  /* ---------------- helpers ---------------- */
  function normalize(s) { return s.replace(/\r\n/g, "\n").replace(/[ \t]+$/gm, "").trim(); }
  function initials(name) {
    return name.split(/[\s-]+/).slice(0, 2).map(function (w) { return w[0]; }).join("").toUpperCase();
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function flash(el) {
    el.style.outline = "2px solid var(--bad)";
    setTimeout(function () { el.style.outline = ""; }, 900);
  }
})();
