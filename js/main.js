(function(){
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var hasIO = "IntersectionObserver" in window;

  var yearEl = document.getElementById("year");
  if(yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------------- Mobile menu ----------------
     Full height panel. Links arrive one after another, 60ms apart,
     with the whole sequence capped at 400ms. */
  var navToggle = document.getElementById("navToggle");
  var navPanel = document.getElementById("navPanel");

  if(navToggle && navPanel){
    var panelItems = navPanel.querySelectorAll("li, .btn");
    var step = Math.min(60, 400 / Math.max(1, panelItems.length));
    panelItems.forEach(function(el, i){
      el.style.setProperty("--stagger", Math.round(i * step) + "ms");
    });

    var setNav = function(open, returnFocus){
      navPanel.classList.toggle("is-open", open);
      navPanel.setAttribute("aria-hidden", open ? "false" : "true");
      if("inert" in navPanel) navPanel.inert = !open;
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.setAttribute("aria-label", open
        ? (navToggle.getAttribute("data-label-close") || "Close menu")
        : (navToggle.getAttribute("data-label-open") || "Open menu"));
      document.body.classList.toggle("menu-open", open);
      if(open){
        var first = navPanel.querySelector("a");
        if(first) first.focus({ preventScroll: true });
      } else if(returnFocus){
        navToggle.focus({ preventScroll: true });
      }
    };
    if("inert" in navPanel) navPanel.inert = true;

    navToggle.addEventListener("click", function(){
      setNav(!navPanel.classList.contains("is-open"), true);
    });
    navPanel.querySelectorAll("a").forEach(function(link){
      link.addEventListener("click", function(){ setNav(false, false); });
    });
    document.addEventListener("keydown", function(e){
      if(e.key === "Escape" && navPanel.classList.contains("is-open")) setNav(false, true);
    });
    window.addEventListener("resize", function(){
      // the toggle is hidden by CSS once the inline nav fits again
      if(navPanel.classList.contains("is-open") && getComputedStyle(navToggle).display === "none") setNav(false, false);
    });
  }

  /* ---------------- Current section in the nav ---------------- */
  var spyLinks = document.querySelectorAll('.nav-links a[href^="#"], .nav-panel a[href^="#"]');
  if(spyLinks.length && hasIO){
    var sections = [];
    spyLinks.forEach(function(a){
      var s = document.querySelector(a.getAttribute("href"));
      if(s && sections.indexOf(s) === -1) sections.push(s);
    });
    var setCurrent = function(id){
      spyLinks.forEach(function(a){
        if(a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
    };
    var spy = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting) setCurrent(entry.target.id);
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach(function(s){ spy.observe(s); });

    // above the first section nothing is current
    var top = document.getElementById("top");
    if(top){
      new IntersectionObserver(function(entries){
        if(entries[0].isIntersecting) setCurrent(null);
      }, { rootMargin: "-45% 0px -50% 0px" }).observe(top);
    }
  }

  /* ---------------- Scroll reveals ----------------
     Rise 32px and fade in once. Items entering together are
     staggered in reading order, capped so nothing waits long. */
  var revealEls = document.querySelectorAll(".reveal");
  if(!hasIO){
    revealEls.forEach(function(el){ el.classList.add("is-visible"); });
  } else {
    var revealObserver = new IntersectionObserver(function(entries){
      var batch = entries.filter(function(e){ return e.isIntersecting; });
      batch.forEach(function(entry, i){
        entry.target.style.setProperty("--delay", Math.min(i * 60, 240) + "ms");
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function(el){ revealObserver.observe(el); });
  }

  /* ---------------- Tagline reveal ----------------
     Each word starts muted and switches to full colour as it
     crosses a trigger line 35% above the bottom of the viewport. */
  document.querySelectorAll("[data-tagline]").forEach(function(block){
    var words = [];
    block.querySelectorAll(".line").forEach(function(line){
      var parts = line.textContent.trim().split(/\s+/);
      line.textContent = "";
      parts.forEach(function(w, i){
        var span = document.createElement("span");
        span.className = "word";
        span.textContent = w;
        line.appendChild(span);
        if(i < parts.length - 1) line.appendChild(document.createTextNode(" "));
        words.push(span);
      });
    });

    if(reduceMotion.matches || !hasIO){
      words.forEach(function(w){ w.classList.add("is-on"); });
      return;
    }

    var wordObserver = new IntersectionObserver(function(entries){
      var crossing = entries
        .filter(function(e){ return e.isIntersecting; })
        .map(function(e){ return e.target; })
        .sort(function(a, b){ return words.indexOf(a) - words.indexOf(b); });
      // words on the same line cross together; light them in reading order
      crossing.forEach(function(w, i){
        setTimeout(function(){ w.classList.add("is-on"); }, i * 70);
        wordObserver.unobserve(w);
      });
    }, { threshold: 1, rootMargin: "0px 0px -35% 0px" });
    words.forEach(function(w){ wordObserver.observe(w); });
  });

  /* ---------------- Copy email ---------------- */
  var copyBtn = document.getElementById("copyEmail");
  var copyStatus = document.getElementById("copyStatus");
  if(copyBtn && copyStatus){
    var clearTimer;
    var report = function(msg, isError){
      copyStatus.textContent = msg;
      copyStatus.classList.toggle("is-error", !!isError);
      clearTimeout(clearTimer);
      clearTimer = setTimeout(function(){ copyStatus.textContent = ""; }, 4000);
    };
    var msg = function(name, fallback){ return copyBtn.getAttribute("data-msg-" + name) || fallback; };
    copyBtn.addEventListener("click", function(){
      var email = copyBtn.getAttribute("data-email");
      if(!navigator.clipboard || !window.isSecureContext){
        report(msg("unavailable", "Copy is not available in this browser. Select the address above instead."), true);
        return;
      }
      navigator.clipboard.writeText(email).then(function(){
        report(msg("ok", "Email address copied."));
      }, function(){
        report(msg("error", "Copy failed. Select the address above instead."), true);
      });
    });
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
        tip.textContent = "";
        var b = document.createElement("b"); b.textContent = title;
        var s = document.createElement("span"); s.textContent = sub;
        tip.appendChild(b); tip.appendChild(s);
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
    var stepY = 1;
    while(scale(x0 + stepY) - scale(x0) < minGap) stepY++;
    for(var yr = Math.ceil(x0); yr <= x1; yr++){
      svgEl("line", { x1: scale(yr), x2: scale(yr), y1: top, y2: bottom, "class": "grid" }, svg);
      if((yr - Math.ceil(x0)) % stepY === 0){
        textEl(svg, scale(yr), bottom + 20, String(yr), "ax", "middle");
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
    var rowH = 48, barH = 10, top = 24, axisH = 32;
    var H = top + rows.length * rowH + axisH;
    var x0 = 2019, x1 = Math.max(2027, Math.ceil(nowYear));
    var scale = function(v){ return (v - x0) / (x1 - x0) * W; };

    var svg = svgEl("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, role: "group", "aria-label": plot.getAttribute("data-label") || "Timeline of roles from 2019 to today" });
    var plotBottom = top + rows.length * rowH;
    yearTicks(svg, x0, x1, top - 8, plotBottom, 40, scale);

    var nx = scale(nowYear);
    svgEl("line", { x1: nx, x2: nx, y1: top - 8, y2: plotBottom, "class": "now-line" }, svg);
    textEl(svg, nx, top - 12, plot.getAttribute("data-today") || "Today", "now-lbl", nx > W - 40 ? "end" : "middle");

    rows.forEach(function(r, i){
      var y = top + i * rowH;
      var bx = scale(r.start);
      var bw = Math.max(4, scale(r.end) - bx);
      var g = svgEl("g", {}, svg);

      var anchorEnd = bx > W * 0.55;
      var lx = anchorEnd ? Math.min(W, bx + bw) : bx;
      textEl(g, lx, y + 18, r.role, "lbl", anchorEnd ? "end" : "start");

      svgEl("rect", { x: bx, y: y + 26, width: bw, height: barH, rx: 4, "class": "bar" + (r.ongoing ? "" : " done") }, g);
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
        t: toYear(d) + 1 / 24,
        upcoming: r.tr.hasAttribute("data-upcoming")
      };
    });

    // lane keys match each row's data-lane; labels are what the chart shows
    var lanes = (plot.getAttribute("data-lanes") || "Publications|Presentations|Awards|Exams & credentials").split("|");
    var laneLabels = (plot.getAttribute("data-lane-labels") || lanes.join("|")).split("|");
    var W = plot.clientWidth;
    var narrow = W < 520;
    var labelW = narrow ? 0 : 176;
    var laneH = narrow ? 52 : 44, top = 8, axisH = 32;
    var H = top + lanes.length * laneH + axisH;
    var x0 = 2023, x1 = 2027;
    var pad = 12;
    var scale = function(v){ return labelW + pad + (v - x0) / (x1 - x0) * (W - labelW - pad * 2); };

    var svg = svgEl("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, role: "group", "aria-label": plot.getAttribute("data-label") || "Milestones by type from 2023 to 2026" });
    var plotBottom = top + lanes.length * laneH;

    for(var yr = x0; yr <= x1; yr++){
      svgEl("line", { x1: scale(yr), x2: scale(yr), y1: top, y2: plotBottom, "class": "grid" }, svg);
      if(yr < x1) textEl(svg, (scale(yr) + scale(yr + 1)) / 2, plotBottom + 20, String(yr), "ax", "middle");
    }

    lanes.forEach(function(lane, li){
      var y = top + li * laneH;
      var cy = narrow ? y + 36 : y + laneH / 2;
      var count = items.filter(function(it){ return it.lane === lane; }).length;
      var label = laneLabels[li] || lane;
      if(narrow){
        textEl(svg, scale(x0), y + 16, label + "  " + count, "lbl-sub");
      } else {
        textEl(svg, 0, cy + 5, label, "lbl");
        textEl(svg, labelW - 8, cy + 4, String(count), "lbl-sub", "end");
      }
      svgEl("line", { x1: scale(x0), x2: scale(x1), y1: cy, y2: cy, "class": "grid" }, svg);
    });

    items.forEach(function(it){
      var li = lanes.indexOf(it.lane);
      var y = top + li * laneH;
      var cy = narrow ? y + 36 : y + laneH / 2;
      var cx = scale(it.t);
      var g = svgEl("g", {}, svg);
      svgEl("circle", { cx: cx, cy: cy, r: 14, "class": "hit" }, g);
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
      plot.classList.remove("is-loading");
    }
    draw();
    if("ResizeObserver" in window) new ResizeObserver(draw).observe(plot);
    else window.addEventListener("resize", draw);
  });

  // printed copies get the tables, since the plots are screen only
  window.addEventListener("beforeprint", function(){
    document.querySelectorAll(".chart-table").forEach(function(d){ d.open = true; });
    document.querySelectorAll(".tagline-text .word").forEach(function(w){ w.classList.add("is-on"); });
  });

  /* ---------------- Lightbox ---------------- */
  var lightbox = document.getElementById("lightbox");
  if(!lightbox) return;
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxVideo = document.getElementById("lightboxVideo");
  var lightboxCaption = document.getElementById("lightboxCaption");
  var lightboxClose = document.getElementById("lightboxClose");
  var lastTrigger = null;

  function stopVideo(){
    if(!lightboxVideo) return;
    lightboxVideo.pause();
    lightboxVideo.removeAttribute("src");
    lightboxVideo.load();
  }

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
      if(lightboxVideo){ lightboxVideo.hidden = true; stopVideo(); }
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
    if(lightboxVideo && !lightboxVideo.hidden) stopVideo();
    if(lastTrigger) lastTrigger.focus();
  }

  document.querySelectorAll(".media-item[data-full]").forEach(function(btn){
    btn.addEventListener("click", function(){ openLightbox(btn); });
  });
  lightboxClose.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function(e){
    if(e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", function(e){
    if(!lightbox.classList.contains("open")) return;
    if(e.key === "Escape"){ closeLightbox(); return; }
    // keep keyboard focus inside the open dialog
    if(e.key === "Tab"){
      var focusables = [lightboxClose];
      if(lightboxVideo && !lightboxVideo.hidden) focusables.push(lightboxVideo);
      var idx = focusables.indexOf(document.activeElement);
      e.preventDefault();
      var next = e.shiftKey ? idx - 1 : idx + 1;
      if(next < 0) next = focusables.length - 1;
      if(next >= focusables.length) next = 0;
      focusables[next].focus();
    }
  });

})();
