// Mobile menu toggle with keyboard support. Everything else works without JS.
(function () {
  "use strict";
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("nav-menu");
  var desktop = window.matchMedia("(min-width: 960px)");

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", String(open));
    menu.classList.toggle("is-open", open);
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    desktop.addEventListener("change", function () { setOpen(false); });
  }

  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
