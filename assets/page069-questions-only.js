(function () {
  "use strict";

  var questionLabels = {
    pg069_n0015: "Swali la sita",
    pg069_n0022: "Swali la saba",
    pg069_n0029: "Swali la nane",
    pg069_n0036: "Swali la tisa",
    pg069_n0043: "Swali la kumi"
  };
  var answerIds = [
    "pg069_n0018", "pg069_n0020", "pg069_n0025", "pg069_n0027",
    "pg069_n0032", "pg069_n0034", "pg069_n0039", "pg069_n0041",
    "pg069_n0046", "pg069_n0048"
  ];

  function applyQuestionReadingRules() {
    Object.keys(questionLabels).forEach(function (id) {
      var element = document.querySelector('[data-id="' + id + '"]');
      if (element) element.setAttribute("aria-label", questionLabels[id]);
    });
    answerIds.forEach(function (id) {
      var element = document.querySelector('[data-id="' + id + '"]');
      if (element) element.removeAttribute("data-id");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyQuestionReadingRules);
  } else {
    applyQuestionReadingRules();
  }
  new MutationObserver(applyQuestionReadingRules).observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
