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
    "#content section textarea,#content section input,#content section select,#content section button{font-family:'Atkinson Hyperlegible',sans-serif!important}",
    "html.matrix-content-page #content section h1{font-size:28px!important;line-height:1.25!important}",
    "html.matrix-content-page #content section h2{font-size:25px!important;line-height:1.28!important}",
    "html.matrix-content-page #content section h3{font-size:22px!important;line-height:1.3!important}",
    "html.matrix-content-page #content section h4,html.matrix-content-page #content section h5,html.matrix-content-page #content section h6{font-size:19px!important;line-height:1.35!important}",
    "html.matrix-content-page #content section p,html.matrix-content-page #content section li{font-size:17px!important;line-height:1.55!important}",
    "html.matrix-content-page #content section td,html.matrix-content-page #content section th{font-size:16px!important;line-height:1.45!important}",
    "html.matrix-content-page #content section textarea,html.matrix-content-page #content section input,html.matrix-content-page #content section select,html.matrix-content-page #content section button{font-size:16px!important;line-height:1.4!important}",
    "html.matrix-content-page #content .matrix-work-title{font-size:24px!important;line-height:1.3!important;font-weight:400!important}",
    "html.matrix-content-page #content .matrix-work-title .matrix-work-title-prefix{font-weight:700!important}",
    "html.matrix-content-page #content .matrix-section-heading{font-size:21px!important;line-height:1.35!important;font-weight:700!important}",
    "html.matrix-content-page #content .matrix-figure-caption{font-size:16px!important;line-height:1.45!important;font-weight:400!important;text-align:center!important}",
    "html.matrix-content-page #content .matrix-figure-caption strong[data-figure-caption-prefix]{font-weight:700!important}",
    "@media(max-width:640px){html.matrix-content-page #content section h1{font-size:22px!important}html.matrix-content-page #content section h2{font-size:20px!important}html.matrix-content-page #content section h3{font-size:18px!important}html.matrix-content-page #content section h4,html.matrix-content-page #content section h5,html.matrix-content-page #content section h6{font-size:17px!important}html.matrix-content-page #content section p,html.matrix-content-page #content section li{font-size:16px!important}html.matrix-content-page #content .matrix-work-title{font-size:19px!important}html.matrix-content-page #content .matrix-section-heading{font-size:18px!important}html.matrix-content-page #content .matrix-figure-caption{font-size:15px!important}}"
  ].join("");
  document.head.appendChild(bookTypography);
  var contentPageMatch = location.pathname.match(/pg(\d{3})_sec\d+\.html$/i);
  if (contentPageMatch && Number(contentPageMatch[1]) >= 5) {
    document.documentElement.classList.add("matrix-content-page");
  }
  function boldWorkTitlePrefix() {
    document.querySelectorAll("[data-id]").forEach(function (node) {
      var text = (node.textContent || "").trim();
      var match = text.match(/^(Kazi ya kufanya namba\s+\d+:)\s+(.+)$/i);
      if (!match || node.querySelector(".matrix-work-title-prefix")) return;
      node.classList.add("matrix-work-title");
      node.textContent = "";
      node.style.fontWeight = "400";
      var prefix = document.createElement("strong");
      prefix.className = "matrix-work-title-prefix";
      prefix.style.fontWeight = "700";
      prefix.textContent = match[1];
      node.appendChild(prefix);
      node.appendChild(document.createTextNode(" " + match[2]));
    });
  }
  function normalizeSemanticTypography() {
    document.querySelectorAll("[data-id]").forEach(function (node) {
      var captionText = (node.textContent || "").trim();
      var captionMatch = captionText.match(/^((?:Kielelezo|Jedwali|Picha) namba\s+[^:.\n]+[:.])\s*(.*)$/i);
      if (!captionMatch) return;
      node.classList.add("matrix-figure-caption");
      if (!node.querySelector("strong[data-figure-caption-prefix]") && captionMatch[2]) {
        node.textContent = "";
        var captionPrefix = document.createElement("strong");
        captionPrefix.dataset.figureCaptionPrefix = "true";
        captionPrefix.textContent = captionMatch[1];
        node.appendChild(captionPrefix);
        node.appendChild(document.createTextNode(" " + captionMatch[2]));
      }
    });
    document.querySelectorAll("strong[data-figure-caption-prefix]").forEach(function (prefix) {
      var caption = prefix.closest("p,figcaption") || prefix.parentElement;
      if (caption) caption.classList.add("matrix-figure-caption");
    });
    document.querySelectorAll("[data-id]").forEach(function (node) {
      var text = (node.textContent || "").trim();
      if (/^(Hatua|Mahitaji|Matokeo|Hitimisho|Tahadhari|Maswali?|Sehemu\s+[A-D])[:.]?$/i.test(text)) {
        node.classList.add("matrix-section-heading");
      }
    });
    var mobileHeadingSizes = { H1: "22px", H2: "20px", H3: "18px", H4: "17px", H5: "17px", H6: "17px" };
    var desktopHeadingSizes = { H1: "28px", H2: "25px", H3: "22px", H4: "19px", H5: "19px", H6: "19px" };
    var headingSizes = window.matchMedia("(max-width:640px)").matches ? mobileHeadingSizes : desktopHeadingSizes;
    document.querySelectorAll("#content h1,#content h2,#content h3,#content h4,#content h5,#content h6").forEach(function (heading) {
      if (heading.querySelector(".matrix-work-title")) heading.classList.add("matrix-work-title");
      if (heading.querySelector(".matrix-section-heading")) heading.classList.add("matrix-section-heading");
      var size = headingSizes[heading.tagName] || headingSizes.H4;
      if (heading.classList.contains("matrix-work-title")) size = window.matchMedia("(max-width:640px)").matches ? "19px" : "24px";
      if (heading.classList.contains("matrix-section-heading")) size = window.matchMedia("(max-width:640px)").matches ? "18px" : "21px";
      heading.style.setProperty("font-size", size, "important");
      heading.style.setProperty("line-height", "1.3", "important");
    });
  }
  boldWorkTitlePrefix();
  normalizeSemanticTypography();
  new MutationObserver(function () {
    boldWorkTitlePrefix();
    normalizeSemanticTypography();
  }).observe(document.documentElement, {
    childList: true,
    characterData: true,
    subtree: true
  });
  window.addEventListener("resize", normalizeSemanticTypography);
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
  function improvePageTwentySevenReadingPlan() {
    if (pageName() !== "pg027_sec001.html" || document.querySelector("[data-page27-reading-plan]")) return;
    var section = document.querySelector('[data-section-id="pg027_sec001"]');
    var desktopTable = section && section.querySelector(".overflow-hidden.border.border-sky-400");
    if (!section || !desktopTable) return;
    var plan = document.createElement("div");
    plan.className = "sr-only";
    plan.dataset.page27ReadingPlan = "true";
    plan.dataset.id = "pg027_plan_audio";
    plan.textContent = "Namba moja. Picha ya namba moja. Pembetatu ya njano yenye ukingo mweusi. Ndani kuna mtu aliyesimama kwenye ukingo ulio karibu na maji yenye mistari ya mawimbi. Namba mbili. Picha ya namba mbili. Duara la buluu lenye mchoro mweupe wa uso wa mtu aliyevaa miwani ya kinga. Namba tatu. Picha ya namba tatu. Duara jekundu lenye mstari wa mshazari juu ya mtu anayekimbia. Namba nne. Picha ya namba nne. Mraba wa kijani wenye mikono miwili ikinawa chini ya bomba la maji. Machaguo ya Sehemu B. Chaguo aa, Katazo. Chaguo baa, Tahadhari. Chaguo chee, Dharura. Chaguo dee, Amri.";
    desktopTable.parentNode.insertBefore(plan, desktopTable);
    var staticIds = [
      "pg027_n0007", "pg027_n0009", "pg027_n0011", "pg027_n0014", "pg027_n0020", "pg027_n0026", "pg027_n0032",
      "pg027_im004", "pg027_im003", "pg027_im002", "pg027_im001",
      "pg027_im004_audio_desc", "pg027_im003_audio_desc", "pg027_im002_audio_desc", "pg027_im001_audio_desc"
    ];
    staticIds.forEach(function (id) {
      section.querySelectorAll('[data-id="' + id + '"]').forEach(function (node) {
        node.removeAttribute("data-id");
        node.setAttribute("aria-hidden", "true");
        if (node.tagName === "IMG") {
          node.setAttribute("alt", "");
          node.setAttribute("role", "presentation");
        }
      });
    });
    ["pg027_n0017", "pg027_n0023", "pg027_n0029", "pg027_n0035"].forEach(function (id) {
      section.querySelectorAll('[data-id="' + id + '"]').forEach(function (node) { node.removeAttribute("data-id"); });
    });
  }
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
    if (heading) {
      heading.classList.add("matrix-page39-heading");
      heading.removeAttribute("data-id");
    }
    [
      "pg032_n0012", "pg032_n0014", "pg032_n0019", "pg032_n0021",
      "pg032_n0026", "pg032_n0028", "pg032_n0033", "pg032_n0035",
      "pg032_n0040", "pg032_n0042"
    ].forEach(function (id) {
      document.querySelectorAll('[data-id="' + id + '"]').forEach(function (node) {
        node.removeAttribute("data-id");
      });
    });
    addPageThirtyNineAnswer("pg032_n0046", "Jibu la swali la 11 kuhusu umuhimu wa alama za usalama");
    addPageThirtyNineAnswer("pg032_n0048", "Jibu la swali la 12 kuhusu michezo muhimu kwa afya ya mwili");
  }
  function improvePageThirtyThreeTable() {
    if (pageName() !== "pg033_sec001.html") return;
    [
      "pg033_n0004", "pg033_n0006", "pg033_n0008",
      "pg033_im004", "pg033_im001", "pg033_im003", "pg033_im002"
    ].forEach(function (id) {
      document.querySelectorAll('[data-id="' + id + '"]').forEach(function (node) {
        node.removeAttribute("data-id");
      });
    });
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
    if (pageName() === "pg033_sec001.html") return;
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
        button.remove();
      }
    });
  }
  function keepSinglePageTwentySevenSubmit() {
    if (pageName() !== "pg027_sec001.html") return;
    var preferred = document.querySelector("#pg027-submit-matching");
    if (!preferred) return;
    Array.from(document.querySelectorAll("button")).forEach(function (button) {
      var isSubmit = /^(tuma|wasilisha)$/i.test((button.textContent || "").trim());
      if (isSubmit && button !== preferred) button.remove();
    });
  }
  function removePageOneSixtyEightSubmit() {
    if (pageName() !== "pg168_sec001.html") return;
    Array.from(document.querySelectorAll("button")).forEach(function (button) {
      if (/^(tuma|wasilisha)$/i.test((button.textContent || "").trim())) button.remove();
    });
  }
  function improveAudioReaderControls() {
    var status = document.querySelector("#matrix-audio-reader-status");
    if (!status) {
      status = document.createElement("p");
      status.id = "matrix-audio-reader-status";
      status.className = "sr-only";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      status.setAttribute("aria-atomic", "true");
      status.textContent = "Vidhibiti vya sauti viko tayari. Sauti ya ukurasa itaanza moja kwa moja.";
      document.body.appendChild(status);
    }

    var controls = document.querySelector('[aria-label="Vidhibiti vya kusoma kwa sauti"]');
    if (!controls) {
      var enableReader = document.querySelector('button[aria-label="Washa maandishi kwa sauti"]');
      if (enableReader && !document.documentElement.dataset.matrixReaderEnableAttempted) {
        document.documentElement.dataset.matrixReaderEnableAttempted = "true";
        window.setTimeout(function () {
          var currentEnableReader = document.querySelector('button[aria-label="Washa maandishi kwa sauti"]');
          if (currentEnableReader) {
            currentEnableReader.click();
            status.textContent = "Reader ya maandishi imewashwa. Vidhibiti vya Play vinafunguliwa.";
          }
        }, 350);
      }
      return false;
    }
    delete document.documentElement.dataset.matrixReaderEnableAttempted;
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", "Audio reader: vidhibiti vya kusoma kwa sauti");

    var buttons = Array.from(controls.querySelectorAll("button"));
    var previous = buttons.find(function (button) {
      return /sauti iliyopita/i.test(button.getAttribute("aria-label") || "");
    });
    var play = buttons.find(function (button) {
      return /^(cheza|play)/i.test(button.getAttribute("aria-label") || "");
    });
    var next = buttons.find(function (button) {
      return /sauti inayofuata/i.test(button.getAttribute("aria-label") || "");
    });
    var stop = buttons.find(function (button) {
      return /simamisha/i.test(button.getAttribute("aria-label") || "");
    });

    if (previous) {
      previous.setAttribute("aria-label", "Previous: nenda kwenye sauti iliyopita");
      previous.setAttribute("title", "Previous – sauti iliyopita");
    }
    if (play) {
      play.setAttribute("aria-label", "Play: cheza sauti ya ukurasa");
      play.setAttribute("title", "Play – cheza sauti");
    }
    if (next) {
      next.setAttribute("aria-label", "Next: nenda kwenye sauti inayofuata");
      next.setAttribute("title", "Next – sauti inayofuata");
    }
    if (stop) {
      stop.setAttribute("aria-label", "Stop: simamisha sauti ya ukurasa");
      stop.setAttribute("title", "Stop – simamisha sauti");
      if (!stop.dataset.matrixStopTracked) {
        stop.dataset.matrixStopTracked = "true";
        stop.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopImmediatePropagation();
          var pauseButton = document.querySelector('button[aria-label="Sitisha"]');
          if (pauseButton) pauseButton.click();
          window.setTimeout(function () {
            var resumedPlay = Array.from(controls.querySelectorAll("button")).find(function (button) {
              return /^(cheza|play)/i.test(button.getAttribute("aria-label") || "");
            });
            if (resumedPlay) resumedPlay.setAttribute("aria-label", "Play: cheza sauti ya ukurasa");
            status.textContent = "Stop: sauti imesimamishwa. Play iko tayari kuanza tena.";
          }, 80);
        }, true);
      }
    }

    Array.from(document.querySelectorAll("button")).forEach(function (button) {
      var label = button.getAttribute("aria-label") || "";
      if (/^Ukurasa uliopita$/i.test(label)) {
        button.setAttribute("aria-label", "Previous page: ukurasa uliopita");
        button.setAttribute("title", "Previous page – ukurasa uliopita");
      } else if (/^Ukurasa unaofuata$/i.test(label)) {
        button.setAttribute("aria-label", "Next page: ukurasa unaofuata");
        button.setAttribute("title", "Next page – ukurasa unaofuata");
      }
    });

    if (play && !document.documentElement.dataset.matrixAudioAutoplayScheduled) {
      document.documentElement.dataset.matrixAudioAutoplayScheduled = "true";
      window.setTimeout(function () {
        var currentControls = document.querySelector('[aria-label="Audio reader: vidhibiti vya kusoma kwa sauti"], [aria-label="Vidhibiti vya kusoma kwa sauti"]');
        var currentPlay = currentControls && Array.from(currentControls.querySelectorAll("button")).find(function (button) {
          return /^(cheza|play)/i.test(button.getAttribute("aria-label") || "");
        });
        document.documentElement.dataset.matrixAudioAutoplayAttempted = "true";
        if (currentPlay) currentPlay.click();
        window.setTimeout(function () {
          var remainingPlay = currentControls && Array.from(currentControls.querySelectorAll("button")).find(function (button) {
            return /^(cheza|play)/i.test(button.getAttribute("aria-label") || "");
          });
          status.textContent = remainingPlay
            ? "Play: browser imezuia sauti kuanza yenyewe. Bonyeza Play ili kuanza kusikiliza."
            : "Play: sauti ya ukurasa imeanza moja kwa moja.";
        }, 500);
      }, 1200);

      var startAfterGesture = function (event) {
        var activeControls = document.querySelector('[aria-label="Audio reader: vidhibiti vya kusoma kwa sauti"], [aria-label="Vidhibiti vya kusoma kwa sauti"]');
        if (activeControls && event.target && activeControls.contains(event.target)) {
          document.removeEventListener("pointerdown", startAfterGesture, true);
          document.removeEventListener("keydown", startAfterGesture, true);
          return;
        }
        window.setTimeout(function () {
          var currentPlay = activeControls && Array.from(activeControls.querySelectorAll("button")).find(function (button) {
            return /^(cheza|play)/i.test(button.getAttribute("aria-label") || "");
          });
          if (currentPlay) currentPlay.click();
        }, 0);
        document.removeEventListener("pointerdown", startAfterGesture, true);
        document.removeEventListener("keydown", startAfterGesture, true);
      };
      document.addEventListener("pointerdown", startAfterGesture, true);
      document.addEventListener("keydown", startAfterGesture, true);
      window.setTimeout(function () {
        var accessiblePlay = document.querySelector('[aria-label="Play: cheza sauti ya ukurasa"]');
        if (accessiblePlay && !document.querySelector(":focus-visible")) accessiblePlay.focus();
      }, 1800);
    }
    return true;
  }
  function improveMainMenuChapterNavigation() {
    if (document.querySelector("[data-matrix-book-toc]")) return;
    var firstChapter = document.querySelector("li[data-chapter-id]");
    var pageList = firstChapter && firstChapter.closest("ol");
    if (!pageList) return;
    var entries = [
      ["Shukurani", "4", "pg004_sec001.html"],
      ["Utangulizi", "5", "pg005_sec001.html"],
      ["Sura ya Kwanza: Kanuni za afya", "6", "pg007_sec001.html"],
      ["Sura ya Pili: Magonjwa", "34", "pg035_sec001.html"],
      ["Sura ya Tatu: Maada", "56", "pg056_sec001.html"],
      ["Sura ya Nne: Uunguaji wa vitu", "72", "pg071_sec001.html"],
      ["Sura ya Tano: Nishati", "84", "pg083_sec001.html"],
      ["Sura ya Sita: Usimbaji katika kompyuta", "119", "pg118_sec001.html"]
    ];
    var container = document.createElement("li");
    container.dataset.matrixBookToc = "true";
    container.style.padding = ".5rem .25rem 1rem";
    container.style.borderBottom = "2px solid #cbd5e1";
    container.style.marginBottom = ".5rem";
    var navigation = document.createElement("nav");
    navigation.setAttribute("aria-label", "Yaliyomo ya kitabu");
    var heading = document.createElement("h2");
    heading.textContent = "Yaliyomo";
    heading.style.fontSize = "1.1rem";
    heading.style.fontWeight = "700";
    heading.style.padding = ".45rem .55rem";
    navigation.appendChild(heading);
    entries.forEach(function (entry) {
      var button = document.createElement("button");
      button.type = "button";
      button.dataset.matrixTocTarget = entry[2];
      button.setAttribute("aria-label", entry[0] + ", ukurasa wa ADT " + entry[1] + ". Fungua mada.");
      button.style.display = "flex";
      button.style.width = "100%";
      button.style.alignItems = "center";
      button.style.justifyContent = "space-between";
      button.style.gap = ".75rem";
      button.style.padding = ".55rem .65rem";
      button.style.borderRadius = ".4rem";
      button.style.textAlign = "left";
      button.style.fontSize = ".98rem";
      var name = document.createElement("span");
      name.textContent = entry[0];
      var page = document.createElement("span");
      page.textContent = entry[1];
      page.style.fontWeight = "700";
      page.setAttribute("aria-hidden", "true");
      button.appendChild(name);
      button.appendChild(page);
      button.addEventListener("click", function () {
        window.location.href = entry[2];
      });
      navigation.appendChild(button);
    });
    container.appendChild(navigation);
    pageList.insertBefore(container, pageList.firstChild);
  }
  var matchingStyle = document.createElement("style");
  matchingStyle.textContent = ".matrix-match-select{display:block;width:100%;max-width:15rem;padding:.7rem .85rem;border:2px solid #38bdf8;border-radius:.65rem;background:#fff;color:#1f2937;font-size:1.05rem}.matrix-match-select:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-match-submit{margin-top:1rem;padding:.7rem 2rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-match-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}.matrix-page39-heading{max-width:100%!important;font-size:1.75rem!important;line-height:1.3!important;overflow-wrap:anywhere!important}.matrix-page39-answer-card{margin-top:.8rem;padding:1rem;border-radius:.85rem;background:rgba(255,255,255,.7)}.matrix-page39-answer{display:block;width:100%;min-height:7rem;margin-top:.75rem;padding:.75rem 1rem;border:1px solid #38bdf8;border-radius:.65rem;background:#fff;resize:vertical}.matrix-page39-answer:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-page39-note{margin:.7rem 0 0 3.5rem;color:#475569;font-size:.9rem;font-style:italic}.matrix-sign-meaning-answer{display:block;width:calc(100% - 1rem);min-height:10rem;margin:.5rem;padding:.75rem;border:2px solid #38bdf8;border-radius:.65rem;background:#fff;resize:vertical}.matrix-sign-meaning-answer:focus{outline:3px solid rgba(14,165,233,.35);outline-offset:2px}.matrix-sign-controls{text-align:center;padding:1.25rem 0 .25rem}.matrix-sign-feedback{min-height:1.5rem;margin:0 0 .75rem;font-weight:700}.matrix-sign-submit{padding:.7rem 2.2rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-sign-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}.matrix-response-controls{text-align:center;padding:1.25rem 0 .25rem}.matrix-response-feedback{min-height:1.5rem;margin:0 0 .75rem;font-weight:700}.matrix-response-submit{padding:.75rem 2.4rem;border:0;border-radius:.75rem;background:#374151;color:#fff;font-size:1.05rem;font-weight:700;box-shadow:0 3px 6px rgba(0,0,0,.24)}.matrix-response-submit:focus{outline:3px solid rgba(14,165,233,.45);outline-offset:3px}@media(max-width:640px){.matrix-page39-heading{font-size:1.3rem!important}.matrix-page39-note{margin-left:0}.matrix-sign-meaning-answer{min-height:7rem}}";
  document.head.appendChild(matchingStyle);
  improvePageTwentySevenReadingPlan();
  improvePageThirtyThreeMatching();
  improvePageThirtyNine();
  improvePageThirtyThreeTable();
  improveResponseSubmission();
  improveAudioReaderControls();
  improveMainMenuChapterNavigation();
  hideDockResponseSubmit();
  keepSinglePageTwentySevenSubmit();
  removePageOneSixtyEightSubmit();
  new MutationObserver(hideDockResponseSubmit).observe(document.body, { childList: true, subtree: true });
  new MutationObserver(keepSinglePageTwentySevenSubmit).observe(document.body, { childList: true, subtree: true });
  new MutationObserver(removePageOneSixtyEightSubmit).observe(document.body, { childList: true, subtree: true });
  var audioReaderObserver = new MutationObserver(function () {
    improveAudioReaderControls();
    improveMainMenuChapterNavigation();
  });
  audioReaderObserver.observe(document.body, { childList: true, subtree: true });
})();
