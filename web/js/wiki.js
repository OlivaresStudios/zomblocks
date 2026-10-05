/* Search, phone menu and list filters (classic script: works from file:// too) */
(function () {
	"use strict";
	var ROOT = document.documentElement.getAttribute("data-root") || "";

	// ------------------------------------------------------------------ search (window.WIKI_INDEX, search-index.js)
	var input = document.getElementById("q"), box = document.getElementById("results"), sel = -1;
	function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
	function render(list) {
		sel = -1;
		if (!list.length) { box.innerHTML = '<div class="none">Nothing found</div>'; box.classList.add("open"); return; }
		box.innerHTML = list.slice(0, 12).map(function (e) {
			return '<a href="' + ROOT + e.url + '">' + (e.icon ? '<img class="pix" src="' + ROOT + e.icon + '" alt="">' : "") + "<b>" + e.title + "</b><span>" + e.kind + "</span></a>";
		}).join("");
		box.classList.add("open");
	}
	function find(q) {
		q = norm(q.trim());
		if (!q) return [];
		var words = q.split(/\s+/);
		return (window.WIKI_INDEX || []).map(function (e) {
			var t = norm(e.title), k = norm(e.keys || "");
			var score = 0;
			for (var i = 0; i < words.length; i++) {
				var w = words[i];
				if (t.indexOf(w) === 0) score += 5; else if (t.indexOf(w) >= 0) score += 3; else if (k.indexOf(w) >= 0) score += 1; else return null;
			}
			return { e: e, s: score };
		}).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).map(function (x) { return x.e; });
	}
	if (input && box) {
		input.addEventListener("input", function () { var r = find(input.value); if (input.value.trim()) render(r); else box.classList.remove("open"); });
		input.addEventListener("keydown", function (ev) {
			var links = box.querySelectorAll("a");
			if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
				ev.preventDefault();
				sel = Math.max(0, Math.min(links.length - 1, sel + (ev.key === "ArrowDown" ? 1 : -1)));
				links.forEach(function (a, i) { a.classList.toggle("sel", i === sel); });
			} else if (ev.key === "Enter" && links.length) {
				window.location.href = links[Math.max(0, sel)].href;
			} else if (ev.key === "Escape") { box.classList.remove("open"); input.blur(); }
		});
		document.addEventListener("click", function (ev) { if (!box.contains(ev.target) && ev.target !== input) box.classList.remove("open"); });
		document.addEventListener("keydown", function (ev) {
			if (ev.key === "/" && document.activeElement !== input && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { ev.preventDefault(); input.focus(); }
		});
	}

	// ------------------------------------------------------------------ phone menu
	var btn = document.getElementById("menu"), side = document.querySelector(".side");
	if (btn && side) btn.addEventListener("click", function () { side.classList.toggle("open"); });

	// ------------------------------------------------------------------ list filters: cards with data-name / data-threat / data-tags
	var grid = document.querySelector("[data-filter-grid]");
	if (grid) {
		var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
		var text = document.getElementById("ftext"), sort = document.getElementById("fsort");
		var threat = 0, tag = "";
		function apply() {
			var q = norm(text ? text.value : "");
			var shown = 0;
			cards.forEach(function (c) {
				var ok = (!q || norm(c.getAttribute("data-name") + " " + c.getAttribute("data-tags")).indexOf(q) >= 0)
					&& (!threat || Number(c.getAttribute("data-threat")) === threat)
					&& (!tag || (" " + c.getAttribute("data-tags") + " ").indexOf(" " + tag + " ") >= 0);
				c.style.display = ok ? "" : "none";
				if (ok) shown++;
			});
			var empty = document.getElementById("fempty");
			if (empty) empty.style.display = shown ? "none" : "";
			var count = document.getElementById("fcount");
			if (count) count.textContent = shown;
		}
		document.querySelectorAll("[data-threat-btn]").forEach(function (b) {
			b.addEventListener("click", function () {
				var v = Number(b.getAttribute("data-threat-btn"));
				threat = threat === v ? 0 : v;
				document.querySelectorAll("[data-threat-btn]").forEach(function (o) { o.classList.toggle("on", Number(o.getAttribute("data-threat-btn")) === threat); });
				apply();
			});
		});
		document.querySelectorAll("[data-tag-btn]").forEach(function (b) {
			b.addEventListener("click", function () {
				var v = b.getAttribute("data-tag-btn");
				tag = tag === v ? "" : v;
				document.querySelectorAll("[data-tag-btn]").forEach(function (o) { o.classList.toggle("on", o.getAttribute("data-tag-btn") === tag); });
				apply();
			});
		});
		if (text) text.addEventListener("input", apply);
		function sortCards() {
			var key = sort.value;
			cards.sort(function (a, b) {
				if (key === "name") return a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"));
				var d = Number(b.getAttribute("data-" + key)) - Number(a.getAttribute("data-" + key));
				return d || a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"));
			});
			cards.forEach(function (c) { grid.appendChild(c); });
		}
		if (sort) { sort.addEventListener("change", sortCards); sortCards(); }
		apply();
	}
})();
