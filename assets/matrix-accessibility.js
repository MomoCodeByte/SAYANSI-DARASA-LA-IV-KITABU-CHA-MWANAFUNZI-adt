(function () {
  "use strict";

  // Enforce one audible media stream for the whole textbook. The bundled
  // reader and interface sounds both use HTMLMediaElement; without this lock
  // a second play request can overlap an active narration clip.
  if (!window.__matrixSingleAudioLock) {
    window.__matrixSingleAudioLock = true;
    var activeMedia = null;
    var nativePlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () {
      if (activeMedia && activeMedia !== this) {
        try {
          activeMedia.pause();
          activeMedia.currentTime = 0;
        } catch (_) {}
      }
      activeMedia = this;
      var result = nativePlay.apply(this, arguments);
      if (result && typeof result.catch === "function") {
        result.catch(function () {});
      }
      return result;
    };
    window.addEventListener("pagehide", function () {
      if (!activeMedia) return;
      try {
        activeMedia.pause();
        activeMedia.currentTime = 0;
      } catch (_) {}
      activeMedia = null;
    });
  }
  var bookTypography = document.createElement("style");
  bookTypography.id = "book-typography-consistency";
  bookTypography.textContent = [
    "#content, #content *{font-family:'Atkinson Hyperlegible',sans-serif!important}",
    "#content section p,#content section li,#content section td,#content section th,#content section div[data-id]:not([role='button']){text-align:justify;text-justify:inter-word}",
    "#content section h1,#content section h2,#content section h3,#content section h4,#content section h5,#content section h6,#content section .text-center{font-family:'Atkinson Hyperlegible',sans-serif!important}",
    "#content section h1.text-center,#content section h2.text-center,#content section h3.text-center,#content section h4.text-center,#content section .text-center{text-align:center!important}",
    "#content section .text-right{text-align:right!important}",
    "#content section textarea,#content section input,#content section select,#content section button{font-family:'Atkinson Hyperlegible',sans-serif!important}"
  ].join("");
  document.head.appendChild(bookTypography);
  function pageName() {
    var name = location.pathname.split("/").pop() || "index.html";
    return name === "index.html" ? "index.html" : name;
  }
  function visuallyHidden(node) {
    Object.assign(node.style, {
      position: "absolute", width: "1px", height: "1px", padding: "0",
      margin: "-1px", overflow: "hidden", clip: "rect(0,0,0,0)",
      whiteSpace: "nowrap", border: "0"
    });
  }
  function renameGlossary() {
    document.querySelectorAll("button,[aria-label]").forEach(function (node) {
      ["aria-label", "title"].forEach(function (attribute) {
        var value = node.getAttribute(attribute);
        if (value && /Kamusi/i.test(value)) node.setAttribute(attribute, value.replace(/Kamusi/gi, "Farahasa"));
      });
      if (node.tagName === "BUTTON" && /Kamusi/i.test(node.textContent || "")) {
        node.childNodes.forEach(function (child) {
          if (child.nodeType === Node.TEXT_NODE) child.textContent = child.textContent.replace(/Kamusi/gi, "Farahasa");
        });
      }
    });
  }
  renameGlossary();
  new MutationObserver(renameGlossary).observe(document.documentElement, { childList: true, subtree: true });
  function improvePageThirtyThreeMatching() {
    if (pageName() !== "pg027_sec001.html") return;
    var correct = { "item-1": "b", "item-2": "d", "item-3": "a", "item-4": "c" };
    var labels = [
      ["", "Chagua kundi"], ["a", "(a) Katazo"], ["b", "(b) Tahadhari"],
      ["c", "(c) Dharura"], ["d", "(d) Amri"]
    ];
    var count = 0;
    document.querySelectorAll(".activity-item[data-activity-item]").forEach(function (item) {
      var key = item.dataset.activityItem;
      var select = document.createElement("select");
      count += 1;
      select.id = "pg027-match-" + count;
      select.className = "matrix-match-select";
      select.dataset.matchKey = key;
      select.dataset.correctValue = correct[key];
      select.setAttribute("aria-label", "Chagua kundi sahihi la alama namba " + key.replace("item-", ""));
      select.setAttribute("tabindex", "0");
      labels.forEach(function (entry) {
        var option = document.createElement("option");
        option.value = entry[0];
        option.textContent = entry[1];
        select.appendChild(option);
      });
      item.replaceWith(select);
    });
    var feedbackBox = document.querySelector("#feedback");
    if (feedbackBox && !document.querySelector("#pg027-submit-matching")) {
      var submit = document.createElement("button");
      submit.id = "pg027-submit-matching";
      submit.type = "button";
      submit.className = "matrix-match-submit";
      submit.textContent = "Tuma";
      feedbackBox.parentElement.appendChild(submit);
    }
    document.addEventListener("click", function (event) {
      var button = event.target.closest("button");
      if (!button || (button.textContent || "").trim().toLowerCase() !== "tuma") return;
      var visible = Array.from(document.querySelectorAll(".matrix-match-select")).filter(function (select) {
        return select.offsetParent !== null;
      });
      if (!visible.length) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      var answered = visible.filter(function (select) { return select.value; }).length;
      var score = 0;
      visible.forEach(function (select) {
        var isCorrect = select.value && select.value === select.dataset.correctValue;
        if (isCorrect) score += 1;
        select.style.borderColor = isCorrect ? "#15803d" : "#dc2626";
        select.style.backgroundColor = isCorrect ? "#f0fdf4" : "#fef2f2";
      });
      var feedback = document.querySelector("#feedback");
      if (feedback) {
        feedback.textContent = answered < visible.length
          ? "Chagua jibu kwa kila alama kabla ya kutuma."
          : "Umejibu " + score + " kati ya " + visible.length + " kwa usahihi.";
        feedback.style.color = answered === visible.length && score === visible.length ? "#15803d" : "#b91c1c";
      }
    }, true);
  }
  function addPageThirtyNineAnswer(questionId, label) {
    var question = document.querySelector('[data-id="' + questionId + '"]');
    if (!question || document.querySelector('[data-response-for="' + questionId + '"]')) return;
    var row = question.parentElement;
    var card = document.createElement("div");
    card.className = "matrix-page39-answer-card";
    row.parentNode.insertBefore(card, row);
    card.appendChild(row);
    var answer = document.createElement("textarea");
    answer.className = "matrix-page39-answer";
    answer.dataset.responseFor = questionId;
    answer.setAttribute("aria-label", label);
    answer.setAttribute("tabindex", "0");
    card.appendChild(answer);
  }
  function improvePageThirtyNine() {
    if (pageName() !== "pg032_sec001.html") return;
    var orphanChoice = document.querySelector('[data-id="pg032_n0003"]');
    if (orphanChoice && orphanChoice.closest("ul")) orphanChoice.closest("ul").remove();
    var heading = document.querySelector('[data-id="pg032_n0007"]');
    if (heading) heading.classList.add("matrix-page39-heading");
    addPageThirtyNineAnswer("pg032_n0046", "Jibu la swali la 11 kuhusu umuhimu wa alama za usalama");
    addPageThirtyNineAnswer("pg032_n0048", "Jibu la swali la 12 kuhusu michezo muhimu kwa afya ya mwili");
    var instruction = document.querySelector('[data-id="pg032_n0051"]');
    if (instruction && !document.querySelector(".matrix-page39-note")) {
      var note = document.createElement("p");
      note.className = "matrix-page39-note";
      note.textContent = "Jedwali la kujibia linaendelea kwenye page 40.";
      instruction.parentElement.parentNode.appendChild(note);
    }
  }
  function improvePageThirtyThreeTable() {
    if (pageName() !== "pg033_sec001.html") return;
    document.querySelectorAll("table tr").forEach(function (row, index) {
      if (index === 0) return;
      var cells = row.querySelectorAll("td");
      if (cells.length < 3 || cells[2].querySelector("textarea")) return;
      var letter = (cells[0].textContent || "").trim();
      var answer = document.createElement("textarea");
      answer.className = "matrix-sign-meaning-answer";
      answer.dataset.responseFor = "pg033-sign-" + index;
      answer.setAttribute("aria-label", "Andika maana ya alama " + letter);
      answer.setAttribute("tabindex", "0");
      cells[2].appendChild(answer);
    });
    var section = document.querySelector('[data-section-id="pg033_sec001"]');
    if (section && !document.querySelector("#pg033-submit-meanings")) {
      var controls = document.createElement("div");
      controls.className = "matrix-sign-controls";
      var feedback = document.createElement("p");
      feedback.id = "pg033-meaning-feedback";
      feedback.className = "matrix-sign-feedback";
      feedback.setAttribute("role", "status");
      feedback.setAttribute("aria-live", "polite");
      var submit = document.createElement("button");
      submit.id = "pg033-submit-meanings";
      submit.type = "button";
      submit.className = "matrix-sign-submit";
      submit.textContent = "Tuma";
      submit.addEventListener("click", function () {
        var answers = Array.from(document.querySelectorAll(".matrix-sign-meaning-answer"));
        var completed = answers.filter(function (answer) { return answer.value.trim(); }).length;
        answers.forEach(function (answer) {
          answer.style.borderColor = answer.value.trim() ? "#38bdf8" : "#dc2626";
        });
        if (completed < answers.length) {
          feedback.textContent = "Jaza maana ya alama zote nne kabla ya kutuma.";
          feedback.style.color = "#b91c1c";
        } else {
          feedback.textContent = "Majibu yote manne yametumwa.";
          feedback.style.color = "#15803d";
        }
      });
      controls.appendChild(feedback);
      controls.appendChild(submit);
      section.appendChild(controls);
    }
  }
  function improveResponseSubmission() {
    var fields = Array.from(document.querySelectorAll(
      'textarea[data-response-for], input[type="text"][data-response-for], textarea[data-aria-id], input[type="text"][data-aria-id]'
    )).filter(function (field) {
      return !field.disabled && field.offsetParent !== null;
    });
    if (!fields.length || document.querySelector("[data-matrix-response-controls]")) return;
    var host = document.querySelector('section[role="activity"], section[data-section-type*="activity"], section[data-section-id]');
    if (!host) return;
    var controls = document.createElement("div");
    controls.className = "matrix-response-controls";
    controls.dataset.matrixResponseControls = "true";

    var feedback = document.createElement("p");
    feedback.className = "matrix-response-feedback";
    feedback.setAttribute("role", "status");
    feedback.setAttribute("aria-live", "polite");

    var submit = document.createElement("button");
    submit.type = "button";
    submit.className = "matrix-response-submit";
    submit.textContent = "Tuma";
    submit.addEventListener("click", function () {
      var completed = fields.filter(function (field) { return field.value.trim(); }).length;
      fields.forEach(function (field) {
        field.style.borderColor = field.value.trim() ? "#0284c7" : "#dc2626";
      });
      if (completed < fields.length) {
        feedback.textContent = "Jaza sehemu zote za kujibia kabla ya kutuma.";
        feedback.style.color = "#b91c1c";
      } else {
        feedback.textContent = "Majibu yako yametumwa.";
        feedback.style.color = "#15803d";
      }
    });
    controls.appendChild(feedback);
    controls.appendChild(submit);
    fields[fields.length - 1].insertAdjacentElement("afterend", controls);
  }
  function hideDockResponseSubmit() {
    var content = document.querySelector("#content");
    var hasResponses = document.querySelector(
      'textarea[data-response-for], input[type="text"][data-response-for], textarea[data-aria-id], input[type="text"][data-aria-id]'
    );
    if (!content || !hasResponses) return;
    Array.from(document.querySelectorAll("button")).forEach(function (button) {
      var isSubmit = /^(tuma|wasilisha)$/i.test((button.textContent || "").trim());
      if (isSubmit && !content.contains(button)) {
        button.hidden = true;
        button.style.display = "none";
        button.setAttribute("aria-hidden", "true");
      }
    });
  }
  var matchingStyle = document.createElement("style");
  matchingStyle.textContent = ".matrix-match-select{display:block;width:100%;max-width:15rem;padding:.7rem .85rem;border:2px solid #38bdf8;border-radius:.65rem;background:#fff;color:#1f2937;font-size:1.05rem}.matrix-match-select:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-match-submit{margin-top:1rem;padding:.7rem 2rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-match-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}.matrix-page39-heading{max-width:100%!important;font-size:1.75rem!important;line-height:1.3!important;overflow-wrap:anywhere!important}.matrix-page39-answer-card{margin-top:.8rem;padding:1rem;border-radius:.85rem;background:rgba(255,255,255,.7)}.matrix-page39-answer{display:block;width:100%;min-height:7rem;margin-top:.75rem;padding:.75rem 1rem;border:1px solid #38bdf8;border-radius:.65rem;background:#fff;resize:vertical}.matrix-page39-answer:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-page39-note{margin:.7rem 0 0 3.5rem;color:#475569;font-size:.9rem;font-style:italic}.matrix-sign-meaning-answer{display:block;width:calc(100% - 1rem);min-height:10rem;margin:.5rem;padding:.75rem;border:2px solid #38bdf8;border-radius:.65rem;background:#fff;resize:vertical}.matrix-sign-meaning-answer:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-sign-controls{text-align:center;padding:1.25rem 0 .25rem}.matrix-sign-feedback{min-height:1.5rem;margin:0 0 .75rem;font-weight:700}.matrix-sign-submit{padding:.7rem 2.2rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-sign-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}.matrix-response-controls{text-align:center;padding:1.25rem 0 .25rem}.matrix-response-feedback{min-height:1.5rem;margin:0 0 .75rem;font-weight:700}.matrix-response-submit{padding:.75rem 2.4rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-response-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}@media(max-width:640px){.matrix-page39-heading{font-size:1.3rem!important}.matrix-page39-note{margin-left:0}.matrix-sign-meaning-answer{min-height:7rem}}";
  document.head.appendChild(matchingStyle);
  improvePageThirtyThreeMatching();
  improvePageThirtyNine();
  improvePageThirtyThreeTable();
  improveResponseSubmission();
  hideDockResponseSubmit();
  new MutationObserver(hideDockResponseSubmit).observe(document.body, { childList: true, subtree: true });
  fetch("./content/accessibility-overrides.json?v=matrix-final-59", { cache: "no-store" })
    .then(function (response) { return response.json(); })
    .then(function (overrides) {
      var entries = overrides[pageName()] || [];
      if (!entries.length) return;
      var aside = document.createElement("aside");
      aside.className = "matrix-accessibility-supplement";
      aside.setAttribute("aria-label", "Maelezo ya ziada ya ufikivu");
      visuallyHidden(aside);
      entries.forEach(function (entry) {
        var paragraph = document.createElement("p");
        paragraph.dataset.matrixItem = String(entry.matrix_item);
        paragraph.textContent = entry.text;
        aside.appendChild(paragraph);
      });
      (document.querySelector("main") || document.body).appendChild(aside);
    })
    .catch(function (error) { console.warn("[matrix-accessibility]", error); });
})();
