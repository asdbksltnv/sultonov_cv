(function(){
  "use strict";

  document.getElementById("year").textContent = new Date().getFullYear();

  /* ---------------- Header scroll state ---------------- */
  var header = document.getElementById("siteHeader");
  var progressBar = document.getElementById("progressBar");

  function onScroll(){
    var scrollTop = window.scrollY || document.documentElement.scrollTop;
    header.classList.toggle("scrolled", scrollTop > 40);

    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = pct + "%";
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
    if(window.innerWidth > 760) setNav(false);
  });

  /* ---------------- Reveal on scroll ---------------- */
  var revealEls = document.querySelectorAll(".reveal");
  var groups = {};
  revealEls.forEach(function(el){
    var parent = el.parentElement;
    var key = parent ? (parent.className || "root") + Array.prototype.indexOf.call(document.querySelectorAll(".section, .hero, .stats-strip"), el.closest(".section, .hero, .stats-strip")) : "root";
    if(!groups[key]) groups[key] = [];
    groups[key].push(el);
  });
  Object.keys(groups).forEach(function(key){
    groups[key].forEach(function(el, i){
      el.style.setProperty("--delay", Math.min(i * 0.08, 0.5) + "s");
    });
  });

  function revealAll(){
    revealEls.forEach(function(el){ el.classList.add("visible"); });
  }

  // Content is hidden until revealed, so never leave it hidden if the
  // observer is unavailable — better to show everything unanimated.
  if(!("IntersectionObserver" in window)){
    revealAll();
  } else {
    var revealObserver = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add("visible");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -60px 0px" });
    revealEls.forEach(function(el){ revealObserver.observe(el); });
  }

  /* ---------------- Stat counters ---------------- */
  var statEls = document.querySelectorAll(".stat-num");
  function animateCount(el){
    var target = parseFloat(el.getAttribute("data-count"));
    var suffix = el.getAttribute("data-suffix") || "";
    var isDecimal = String(target).indexOf(".") !== -1;
    var duration = 1400;
    var start = null;

    function step(ts){
      if(!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = target * eased;
      el.textContent = (isDecimal ? value.toFixed(2) : Math.round(value)) + suffix;
      if(progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var statObserver = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if(entry.isIntersecting){
        animateCount(entry.target);
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  statEls.forEach(function(el){ statObserver.observe(el); });

  /* ---------------- GPA chart ---------------- */
  var gpaData = [
    { label: "Fall 2019",   short: "F19", gpa: 3.53, credits: 30 },
    { label: "Spring 2020", short: "S20", gpa: 3.74, credits: 30 },
    { label: "Fall 2020",   short: "F20", gpa: 3.50, credits: 30 },
    { label: "Spring 2021", short: "S21", gpa: 3.62, credits: 30 },
    { label: "Fall 2021",   short: "F21", gpa: 3.88, credits: 30 },
    { label: "Spring 2022", short: "S22", gpa: 3.90, credits: 30 },
    { label: "Fall 2022",   short: "F22", gpa: 3.99, credits: 30 },
    { label: "Spring 2023", short: "S23", gpa: 3.78, credits: 30 },
    { label: "Fall 2023",   short: "F23", gpa: 3.94, credits: 30 },
    { label: "Spring 2024", short: "S24", gpa: 3.98, credits: 30 },
    { label: "Fall 2024",   short: "F24", gpa: 3.89, credits: 30 },
    { label: "Spring 2025", short: "S25", gpa: 3.93, credits: 30 }
  ];

  (function drawGpaChart(){
    var svg = document.querySelector(".gpa-chart");
    if(!svg) return;

    var W = 860, H = 300;
    var margin = { top: 20, right: 16, bottom: 34, left: 40 };
    var plotW = W - margin.left - margin.right;
    var plotH = H - margin.top - margin.bottom;

    var yMin = 3.4, yMax = 4.0;
    var yTicks = [3.4, 3.6, 3.8, 4.0];

    function xPos(i){ return margin.left + (i / (gpaData.length - 1)) * plotW; }
    function yPos(v){ return margin.top + (1 - (v - yMin) / (yMax - yMin)) * plotH; }

    var gridGroup = document.getElementById("gpaGrid");
    var frag = document.createDocumentFragment();
    yTicks.forEach(function(t){
      var y = yPos(t);
      var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", margin.left);
      line.setAttribute("x2", W - margin.right);
      line.setAttribute("y1", y);
      line.setAttribute("y2", y);
      line.setAttribute("class", "gpa-grid-line");
      frag.appendChild(line);

      var label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", margin.left - 10);
      label.setAttribute("y", y + 4);
      label.setAttribute("text-anchor", "end");
      label.setAttribute("class", "gpa-grid-label");
      label.textContent = t.toFixed(1);
      frag.appendChild(label);
    });
    gridGroup.appendChild(frag);

    var linePoints = gpaData.map(function(d, i){ return xPos(i) + "," + yPos(d.gpa); });
    var pathD = "M" + linePoints.join(" L");
    document.getElementById("gpaLine").setAttribute("d", pathD);

    var areaD = pathD +
      " L" + xPos(gpaData.length - 1) + "," + (margin.top + plotH) +
      " L" + xPos(0) + "," + (margin.top + plotH) + " Z";
    document.getElementById("gpaArea").setAttribute("d", areaD);

    var dotsGroup = document.getElementById("gpaDots");
    var labelsGroup = document.getElementById("gpaLabels");
    var tooltip = document.getElementById("gpaTooltip");
    var dotsFrag = document.createDocumentFragment();
    var labelsFrag = document.createDocumentFragment();

    var peakIndex = gpaData.reduce(function(best, d, i){ return d.gpa > gpaData[best].gpa ? i : best; }, 0);

    gpaData.forEach(function(d, i){
      var cx = xPos(i), cy = yPos(d.gpa);

      var dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", cx);
      dot.setAttribute("cy", cy);
      dot.setAttribute("r", 5);
      dot.setAttribute("class", "gpa-dot");
      dot.setAttribute("tabindex", "0");
      dot.setAttribute("role", "img");
      dot.setAttribute("aria-label", d.label + ": GPA " + d.gpa.toFixed(2));

      function activate(){
        document.querySelectorAll(".gpa-dot.active").forEach(function(o){ o.classList.remove("active"); });
        dot.classList.add("active");
        tooltip.textContent = d.label + " — GPA " + d.gpa.toFixed(2);
      }
      dot.addEventListener("mouseenter", activate);
      dot.addEventListener("focus", activate);
      dotsFrag.appendChild(dot);

      if(i % 2 === 0 || i === gpaData.length - 1){
        var xLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
        xLabel.setAttribute("x", cx);
        xLabel.setAttribute("y", H - 8);
        xLabel.setAttribute("text-anchor", "middle");
        // tagged so narrow screens can thin the axis out via CSS
        xLabel.setAttribute("data-idx", i);
        xLabel.textContent = d.short;
        labelsFrag.appendChild(xLabel);
      }

      if(i === peakIndex){
        var peakLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
        peakLabel.setAttribute("x", cx);
        peakLabel.setAttribute("y", cy - 14);
        peakLabel.setAttribute("text-anchor", "middle");
        peakLabel.setAttribute("class", "gpa-peak-label");
        peakLabel.textContent = "Peak " + d.gpa.toFixed(2);
        labelsFrag.appendChild(peakLabel);
      }
    });

    dotsGroup.appendChild(dotsFrag);
    labelsGroup.appendChild(labelsFrag);
    tooltip.textContent = gpaData[gpaData.length - 1].label + " — GPA " + gpaData[gpaData.length - 1].gpa.toFixed(2) + " (most recent)";

    var tableBody = document.getElementById("gpaTableBody");
    var rowsFrag = document.createDocumentFragment();
    gpaData.forEach(function(d){
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + d.label + "</td><td>" + d.gpa.toFixed(2) + "</td><td>" + d.credits + "</td>";
      rowsFrag.appendChild(tr);
    });
    tableBody.appendChild(rowsFrag);
  })();

  /* ---------------- Lightbox ---------------- */
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxCaption = document.getElementById("lightboxCaption");
  var lightboxClose = document.getElementById("lightboxClose");

  function openLightbox(src, caption){
    lightboxImg.src = src;
    lightboxImg.alt = caption;
    lightboxCaption.textContent = caption;
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeLightbox(){
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  document.querySelectorAll(".gallery-item").forEach(function(btn){
    btn.addEventListener("click", function(){
      openLightbox(btn.getAttribute("data-full"), btn.getAttribute("data-caption"));
    });
  });
  lightboxClose.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function(e){
    if(e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", function(e){
    if(e.key === "Escape") closeLightbox();
  });

})();
