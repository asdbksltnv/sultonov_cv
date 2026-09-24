(function(){
  "use strict";

  document.getElementById("year").textContent = new Date().getFullYear();

  /* ---------------- Header scroll state ---------------- */
  var header = document.getElementById("siteHeader");

  function onScroll(){
    var scrollTop = window.scrollY || document.documentElement.scrollTop;
    header.classList.toggle("scrolled", scrollTop > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- Mobile nav ---------------- */
  var navToggle = document.getElementById("navToggle");
  var mainNav = document.getElementById("mainNav");

  function setNav(open){
    mainNav.classList.toggle("open", open);
    navToggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  navToggle.addEventListener("click", function(e){
    e.stopPropagation();
    setNav(!mainNav.classList.contains("open"));
  });

  mainNav.querySelectorAll("a").forEach(function(link){
    link.addEventListener("click", function(){ setNav(false); });
  });

  // tapping anywhere outside the open menu dismisses it
  document.addEventListener("click", function(e){
    if(!mainNav.classList.contains("open")) return;
    if(mainNav.contains(e.target) || navToggle.contains(e.target)) return;
    setNav(false);
  });

  document.addEventListener("keydown", function(e){
    if(e.key === "Escape") setNav(false);
  });

  // a resize past the breakpoint should never leave the panel stuck open
  window.addEventListener("resize", function(){
    if(window.innerWidth > 900) setNav(false);
  });

  /* ---------------- Reveal on scroll ---------------- */
  var revealEls = document.querySelectorAll(".reveal");

  // stagger siblings that enter together, but keep the cascade short
  var groups = new Map();
  revealEls.forEach(function(el){
    var key = el.closest(".sec-body, .hero, .section, .contact") || document.body;
    var list = groups.get(key) || [];
    list.push(el);
    groups.set(key, list);
  });
  groups.forEach(function(list){
    list.forEach(function(el, i){
      el.style.setProperty("--delay", Math.min(i * 0.05, 0.25) + "s");
    });
  });

  // Content is hidden until revealed, so never leave it hidden if the
  // observer is unavailable — better to show everything unanimated.
  if(!("IntersectionObserver" in window)){
    revealEls.forEach(function(el){ el.classList.add("visible"); });
  } else {
    var revealObserver = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add("visible");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function(el){ revealObserver.observe(el); });
  }

  /* ---------------- Charts ----------------
     Each chart reads its rows from the table inside the same <figure>,
     so the table view and the plot can never disagree. */
  var SVG_NS = "http://www.w3.org/2000/svg";

  function svgEl(name, attrs, parent){
    var el = document.createElementNS(SVG_NS, name);
    Object.keys(attrs || {}).forEach(function(k){ el.setAttribute(k, attrs[k]); });
    if(parent) parent.appendChild(el);
    return el;
  }

  function textEl(parent, x, y, str, cls, anchor){
    var t = svgEl("text", { x: x, y: y, "class": cls, "text-anchor": anchor || "start" }, parent);
    t.textContent = str;
    return t;
  }

  var now = new Date();
  var nowYear = now.getFullYear() + now.getMonth() / 12 + (now.getDate() - 1) / 365;

  // "2024-06" -> 2024.4167 (start of that month); "now" -> today
  function toYear(str){
    if(str === "now") return nowYear;
    var p = str.split("-");
    return +p[0] + (+p[1] - 1) / 12;
  }

  function rowsOf(table){
    return Array.prototype.map.call(table.tBodies[0].rows, function(tr){
      return { tr: tr, cells: Array.prototype.map.call(tr.cells, function(td){ return td.textContent; }) };
    });
  }

  // one tooltip per plot; shows on hover and on keyboard focus
  function makeTip(plot){
    var tip = document.createElement("div");
    tip.className = "chart-tip";
    tip.setAttribute("aria-hidden", "true");
    plot.appendChild(tip);
    return {
      show: function(x, y, title, sub){
        tip.innerHTML = "";
        var b = document.createElement("b"); b.textContent = title;
        var s = document.createElement("span"); s.textContent = sub;
        tip.appendChild(b); tip.appendChild(s);
        // keep the tip inside the plot horizontally
        var half = Math.min(120, tip.offsetWidth / 2 || 100);
        var cx = Math.max(half, Math.min(plot.clientWidth - half, x));
        tip.style.left = cx + "px";
        tip.style.top = y + "px";
        tip.classList.add("show");
      },
      hide: function(){ tip.classList.remove("show"); }
    };
  }

  function bindMark(g, tip, x, y, title, sub){
    g.setAttribute("tabindex", "0");
    g.setAttribute("role", "img");
    g.setAttribute("aria-label", title + ", " + sub);
    g.setAttribute("class", "mark");
    var show = function(){ tip.show(x, y, title, sub); };
    g.addEventListener("mouseenter", show);
    g.addEventListener("focus", show);
    g.addEventListener("mouseleave", tip.hide);
    g.addEventListener("blur", tip.hide);
  }

  function yearTicks(svg, x0, x1, top, bottom, minGap, scale){
    var step = 1;
    while(scale(x0 + step) - scale(x0) < minGap) step++;
    for(var yr = Math.ceil(x0); yr <= x1; yr++){
      svgEl("line", { x1: scale(yr), x2: scale(yr), y1: top, y2: bottom, "class": "grid" }, svg);
      if((yr - Math.ceil(x0)) % step === 0){
        textEl(svg, scale(yr), bottom + 18, String(yr), "ax", "middle");
      }
    }
  }

  /* Roles over time: one row per role, label above its bar. */
  function renderCareer(plot, table, tip){
    var rows = rowsOf(table).map(function(r){
      return {
        role: r.cells[0], org: r.cells[1], dates: r.cells[2],
        start: toYear(r.tr.getAttribute("data-start")),
        end: toYear(r.tr.getAttribute("data-end")),
        ongoing: r.tr.getAttribute("data-end") === "now"
      };
    });

    var W = plot.clientWidth;
    var rowH = 46, barH = 10, top = 22, axisH = 28;
    var H = top + rows.length * rowH + axisH;
    var x0 = 2019, x1 = Math.max(2027, Math.ceil(nowYear));
    var scale = function(v){ return (v - x0) / (x1 - x0) * W; };

    var svg = svgEl("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, role: "group", "aria-label": "Timeline of roles from 2019 to today" });
    var plotBottom = top + rows.length * rowH;
    yearTicks(svg, x0, x1, top - 8, plotBottom, 38, scale);

    // today marker
    var nx = scale(nowYear);
    svgEl("line", { x1: nx, x2: nx, y1: top - 8, y2: plotBottom, "class": "now-line" }, svg);
    textEl(svg, nx, top - 12, "Today", "now-lbl", nx > W - 40 ? "end" : "middle");

    rows.forEach(function(r, i){
      var y = top + i * rowH;
      var bx = scale(r.start);
      var bw = Math.max(4, scale(r.end) - bx);
      var g = svgEl("g", {}, svg);

      // label sits above the bar, anchored to whichever side has room
      var anchorEnd = bx > W * 0.55;
      var lx = anchorEnd ? Math.min(W, bx + bw) : bx;
      textEl(g, lx, y + 16, r.role, "lbl", anchorEnd ? "end" : "start");

      svgEl("rect", { x: bx, y: y + 24, width: bw, height: barH, rx: 3, "class": "bar" + (r.ongoing ? "" : " done") }, g);
      // generous invisible hit area over the whole row span of the bar
      svgEl("rect", { x: bx - 4, y: y + 2, width: bw + 8, height: rowH - 4, "class": "hit" }, g);

      bindMark(g, tip, bx + bw / 2, y + 22, r.role + " · " + r.org, r.dates);
    });

    svgEl("line", { x1: 0, x2: W, y1: plotBottom, y2: plotBottom, "class": "baseline" }, svg);
    return svg;
  }

  /* Milestones: swim lanes by type, one dot per dated milestone. */
  function renderMilestones(plot, table, tip){
    var items = rowsOf(table).map(function(r){
      var d = r.tr.getAttribute("data-date");
      return {
        when: r.cells[0], what: r.cells[2],
        lane: r.tr.getAttribute("data-lane"),
        // centre the dot inside its month
        t: toYear(d) + 1 / 24,
        upcoming: r.tr.hasAttribute("data-upcoming")
      };
    });

    var lanes = ["Publications", "Presentations", "Awards", "Exams & credentials"];
    var W = plot.clientWidth;
    var narrow = W < 520;
    var labelW = narrow ? 0 : 150;
    var laneH = narrow ? 50 : 40, top = 8, axisH = 28;
    var H = top + lanes.length * laneH + axisH;
    var x0 = 2023, x1 = 2027;
    var pad = 10;
    var scale = function(v){ return labelW + pad + (v - x0) / (x1 - x0) * (W - labelW - pad * 2); };

    var svg = svgEl("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, role: "group", "aria-label": "Milestones by type from 2023 to 2026" });
    var plotBottom = top + lanes.length * laneH;

    // year bands: a hairline at each boundary, the year centred in its band
    for(var yr = x0; yr <= x1; yr++){
      svgEl("line", { x1: scale(yr), x2: scale(yr), y1: top, y2: plotBottom, "class": "grid" }, svg);
      if(yr < x1) textEl(svg, (scale(yr) + scale(yr + 1)) / 2, plotBottom + 18, String(yr), "ax", "middle");
    }

    lanes.forEach(function(lane, li){
      var y = top + li * laneH;
      var cy = narrow ? y + 34 : y + laneH / 2;
      var count = items.filter(function(it){ return it.lane === lane; }).length;
      var label = lane + "  " + count;
      if(narrow){
        textEl(svg, scale(x0), y + 15, label, "lbl-sub");
      } else {
        textEl(svg, 0, cy + 4, lane, "lbl");
        textEl(svg, labelW - 8, cy + 4, String(count), "lbl-sub", "end");
      }
      svgEl("line", { x1: scale(x0), x2: scale(x1), y1: cy, y2: cy, "class": "grid" }, svg);
    });

    items.forEach(function(it){
      var li = lanes.indexOf(it.lane);
      var y = top + li * laneH;
      var cy = narrow ? y + 34 : y + laneH / 2;
      var cx = scale(it.t);
      var g = svgEl("g", {}, svg);
      svgEl("circle", { cx: cx, cy: cy, r: 13, "class": "hit" }, g);
      svgEl("circle", { cx: cx, cy: cy, r: it.upcoming ? 5 : 6, "class": "dot" + (it.upcoming ? " upcoming" : "") }, g);
      bindMark(g, tip, cx, cy - 10, it.what, it.when);
    });

    svgEl("line", { x1: scale(x0), x2: scale(x1), y1: plotBottom, y2: plotBottom, "class": "baseline" }, svg);
    return svg;
  }

  var renderers = { career: renderCareer, milestones: renderMilestones };

  document.querySelectorAll(".chart-plot[data-chart]").forEach(function(plot){
    var table = document.getElementById(plot.getAttribute("data-source"));
    var render = renderers[plot.getAttribute("data-chart")];
    if(!table || !render) return;

    var tip = makeTip(plot);
    var lastW = 0;
    function draw(){
      var w = plot.clientWidth;
      if(!w || w === lastW) return;
      lastW = w;
      var old = plot.querySelector("svg");
      var svg = render(plot, table, tip);
      if(old) plot.replaceChild(svg, old); else plot.insertBefore(svg, plot.firstChild);
    }
    draw();
    if("ResizeObserver" in window) new ResizeObserver(draw).observe(plot);
    else window.addEventListener("resize", draw);
  });

  // printed copies get the tables, since the plots are screen-only
  window.addEventListener("beforeprint", function(){
    document.querySelectorAll(".chart-table").forEach(function(d){ d.open = true; });
  });

  /* ---------------- Lightbox ---------------- */
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxVideo = document.getElementById("lightboxVideo");
  var lightboxCaption = document.getElementById("lightboxCaption");
  var lightboxClose = document.getElementById("lightboxClose");
  var lastTrigger = null;

  function openLightbox(btn){
    var caption = btn.getAttribute("data-caption");
    var videoSrc = btn.getAttribute("data-video");
    lastTrigger = btn;

    if(videoSrc && lightboxVideo){
      lightboxImg.hidden = true;
      lightboxImg.removeAttribute("src");
      lightboxVideo.hidden = false;
      lightboxVideo.src = videoSrc;
      lightboxVideo.poster = btn.getAttribute("data-full") || "";
      lightboxVideo.play().catch(function(){});
    } else {
      if(lightboxVideo){ lightboxVideo.hidden = true; lightboxVideo.pause(); lightboxVideo.removeAttribute("src"); lightboxVideo.load(); }
      lightboxImg.hidden = false;
      lightboxImg.src = btn.getAttribute("data-full");
      lightboxImg.alt = caption;
    }
    lightboxCaption.textContent = caption;
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    lightboxClose.focus();
  }
  function closeLightbox(){
    if(!lightbox.classList.contains("open")) return;
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if(lightboxVideo && !lightboxVideo.hidden){
      lightboxVideo.pause();
      lightboxVideo.removeAttribute("src");
      lightboxVideo.load();
    }
    if(lastTrigger) lastTrigger.focus();
  }

  document.querySelectorAll(".gallery-item").forEach(function(btn){
    btn.addEventListener("click", function(){ openLightbox(btn); });
  });
  lightboxClose.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function(e){
    if(e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", function(e){
    if(e.key === "Escape") closeLightbox();
  });

})();
