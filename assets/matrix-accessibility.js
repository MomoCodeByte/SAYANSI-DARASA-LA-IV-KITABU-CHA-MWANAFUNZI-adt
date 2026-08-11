(function () {
  "use strict";
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
  fetch("./content/accessibility-overrides.json?v=matrix-v1-1", { cache: "no-store" })
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
