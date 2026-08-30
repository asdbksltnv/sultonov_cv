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

  /* ---------------- Lightbox ---------------- */
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxVideo = document.getElementById("lightboxVideo");
  var lightboxCaption = document.getElementById("lightboxCaption");
  var lightboxClose = document.getElementById("lightboxClose");

  function openLightbox(btn){
    var caption = btn.getAttribute("data-caption");
    var videoSrc = btn.getAttribute("data-video");

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
  }
  function closeLightbox(){
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if(lightboxVideo && !lightboxVideo.hidden){
      lightboxVideo.pause();
      lightboxVideo.removeAttribute("src");
      lightboxVideo.load();
    }
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
