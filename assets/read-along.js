(function () {
  "use strict";
  if (window.__sayansiReadAlongLoaded) return;
  window.__sayansiReadAlongLoaded = true;

  var state = { ready: false, idsByFile: {}, filesById: {}, timecodes: {}, texts: {}, maps: {}, active: null, queue: [], index: 0 };
  var pageWords = [];

  function clean(value) {
    return String(value || "").toLocaleLowerCase("sw-TZ").normalize("NFKD")
      .replace(/[^a-z0-9\u00c0-\u024f]+/g, "");
  }

  function clearHighlight() {
    document.querySelectorAll(".pdf-word.is-reading-word").forEach(function (word) {
      word.classList.remove("is-reading-word");
    });
  }

  function isReadable(text) {
    var value = String(text || "").replace(/\s+/g, " ").trim();
    return value &&
      !/FOR\s+ONLINE\s+(?:READING|USE)\s+ONLY/i.test(value) &&
      !/SAYANSI\s+DARASA\s+LA\s+IV\s+KITABU\s+CHA\s+MWANAFUNZI(?:\.indd)?/i.test(value) &&
      !/^\d{1,2}\/\d{1,2}\/\d{4}(?:\s+\d{1,2}:\d{2})?$/.test(value);
  }

  function mapFor(textId) {
    if (state.maps[textId]) return state.maps[textId];
    var wanted = String(state.texts[textId] || "").match(/\S+/g) || [];
    var result = [];
    var cursor = 0;
    wanted.forEach(function (token) {
      var target = clean(token);
      var found = -1;
      for (var i = cursor; i < pageWords.length; i += 1) {
        var candidate = clean(pageWords[i].textContent);
        if (candidate && (candidate === target || candidate.indexOf(target) === 0 || target.indexOf(candidate) === 0)) {
          found = i;
          break;
        }
      }
      if (found < 0) {
        for (var j = 0; j < pageWords.length; j += 1) {
          if (clean(pageWords[j].textContent) === target) { found = j; break; }
        }
      }
      result.push(found >= 0 ? pageWords[found] : null);
      if (found >= 0) cursor = found + 1;
    });
    state.maps[textId] = result;
    return result;
  }

  function entriesFor(textId) {
    var root = state.timecodes[textId];
    if (!root || !root.timecodes) return [];
    var group = root.timecodes.find(Boolean);
    return group && group.word_timestamps ? group.word_timestamps : [];
  }

  function update(audio) {
    if (!state.ready || !audio.src) return;
    var file = decodeURIComponent(audio.src.split("/").pop().split("?")[0]);
    var textId = state.idsByFile[file];
    if (!textId) return;
    var entries = entriesFor(textId);
    var index = -1;
    for (var i = 0; i < entries.length; i += 1) {
      if (audio.currentTime + 0.03 >= Number(entries[i].start || 0) &&
          audio.currentTime < Number(entries[i].end || entries[i].start || 0) + 0.05) {
        index = Number.isInteger(entries[i].display_index) ? entries[i].display_index : i;
        break;
      }
    }
    clearHighlight();
    var word = mapFor(textId)[index];
    if (word) word.classList.add("is-reading-word");
  }

  function attach(audio) {
    if (!(audio instanceof HTMLMediaElement) || audio.dataset.sayansiReadAlong) return;
    audio.dataset.sayansiReadAlong = "true";
    audio.addEventListener("play", function () {
      document.querySelectorAll("audio").forEach(function (other) {
        if (other !== audio && !other.paused) other.pause();
      });
      state.active = audio;
      update(audio);
    });
    audio.addEventListener("timeupdate", function () { update(audio); });
    audio.addEventListener("seeking", function () { update(audio); });
    audio.addEventListener("pause", function () { if (state.active === audio) clearHighlight(); });
    audio.addEventListener("ended", clearHighlight);
  }

  function stop() {
    if (state.active) {
      state.active.pause();
      state.active.currentTime = 0;
      state.active = null;
    }
    clearHighlight();
  }

  function playIndex(index) {
    if (!state.ready || !state.queue.length) return;
    stop();
    state.index = Math.max(0, Math.min(index, state.queue.length - 1));
    var textId = state.queue[state.index];
    var filename = state.filesById[textId];
    if (!filename) return;
    var audio = new Audio("./content/i18n/sw-TZ/audio/" + String(filename).split("/").pop().split("?")[0]);
    attach(audio);
    state.active = audio;
    audio.addEventListener("ended", function () {
      if (state.index + 1 < state.queue.length) playIndex(state.index + 1);
      else stop();
    }, { once: true });
    audio.play().catch(function (error) { console.warn("[sayansi-audio]", error); });
  }

  function controlName(button) {
    return [button.getAttribute("aria-label"), button.getAttribute("title"), button.textContent]
      .filter(Boolean).join(" ").replace(/\s+/g, " ").trim().toLocaleLowerCase("sw-TZ");
  }

  window.addEventListener("click", function (event) {
    var button = event.target && event.target.closest ? event.target.closest("button") : null;
    if (!button) return;
    var name = controlName(button);
    var handled = true;
    if (/^(cheza|play)\b/.test(name)) {
      if (state.active && state.active.paused) state.active.play(); else playIndex(state.index);
    } else if (/^(sitisha|pause)\b/.test(name)) {
      if (state.active) state.active.pause();
    } else if (/^(simamisha|stop)\b/.test(name)) {
      stop(); state.index = 0;
    } else if (/sauti inayofuata|next audio/.test(name)) {
      playIndex(state.index + 1);
    } else if (/sauti iliyopita|previous audio/.test(name)) {
      playIndex(state.index - 1);
    } else handled = false;
    if (handled) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }, true);

  async function load() {
    var base = "./content/i18n/sw-TZ/";
    var values = await Promise.all([
      fetch(base + "texts.json").then(function (r) { return r.json(); }),
      fetch(base + "audios.json").then(function (r) { return r.json(); }),
      fetch(base + "timecode/timecode_output.json").then(function (r) { return r.json(); })
    ]);
    state.texts = values[0];
    state.filesById = values[1];
    state.idsByFile = Object.fromEntries(Object.entries(values[1]).map(function (pair) {
      return [String(pair[1]).split("/").pop().split("?")[0], pair[0]];
    }));
    state.timecodes = values[2];
    pageWords = Array.prototype.slice.call(document.querySelectorAll(".pdf-word"));
    state.queue = Array.prototype.slice.call(document.querySelectorAll('.accessible-transcript[aria-label="Maandishi ya ukurasa"] [data-id], .accessible-transcript[aria-label="Maelezo ya ziada ya ufikivu"] [data-id]'))
      .map(function (node) { return node.getAttribute("data-id"); })
      .filter(function (id) { return Boolean(state.filesById[id]) && isReadable(state.texts[id]); });
    state.ready = true;
    document.querySelectorAll("audio").forEach(attach);
  }

  var nativePlay = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    attach(this);
    return nativePlay.apply(this, arguments);
  };
  new MutationObserver(function () { document.querySelectorAll("audio").forEach(attach); })
    .observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener("pagehide", function () {
    document.querySelectorAll("audio").forEach(function (audio) { audio.pause(); });
    clearHighlight();
  });
  load().catch(function (error) { console.warn("[sayansi-read-along]", error); });
})();
