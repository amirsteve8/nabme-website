(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const root = document.documentElement;
  const reduceMQ = matchMedia("(prefers-reduced-motion: reduce)");
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
  };
  const motionOff = () => reduceMQ.matches || root.classList.contains("motion-off");
  if (store.get("nabme-motion") === "off") root.classList.add("motion-off");

  // ---------- Header shadow (rAF-throttled) ----------
  const header = $(".header");
  let ticking = false;
  addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { header && header.classList.toggle("is-scrolled", scrollY > 40); ticking = false; });
  }, { passive: true });

  // ---------- Desktop dropdowns (hover via CSS; click + keyboard here) ----------
  const items = $$(".nav__item");
  const closeAll = (except) => items.forEach((it) => {
    if (it === except) return;
    it.classList.remove("is-open");
    const b = $(".nav__top", it); b && b.setAttribute("aria-expanded", "false");
  });
  items.forEach((it) => {
    const btn = $("button.nav__top", it);
    if (!btn) return;
    btn.addEventListener("click", () => {
      const open = !it.classList.contains("is-open");
      closeAll(it);
      it.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("click", (e) => { if (!e.target.closest(".nav__item")) closeAll(); });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const open = items.find((i) => i.classList.contains("is-open"));
    if (open) { closeAll(); $(".nav__top", open).focus(); }
    closeMenu(true);
  });

  // ---------- Mobile menu ----------
  const burger = $(".burger");
  const mnav = $(".mnav");
  function closeMenu(focus) {
    if (!document.body.classList.contains("menu-open")) return;
    document.body.classList.remove("menu-open");
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", "Open menu");
    mnav.setAttribute("aria-hidden", "true");
    mnav.inert = true;
    if (focus) burger.focus();
  }
  if (burger && mnav) {
    mnav.inert = true;
    burger.addEventListener("click", () => {
      if (document.body.classList.contains("menu-open")) return closeMenu(true);
      document.body.classList.add("menu-open");
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Close menu");
      mnav.setAttribute("aria-hidden", "false");
      mnav.inert = false;
      setTimeout(() => { const f = $("summary, a", mnav); f && f.focus(); }, 50);
    });
    matchMedia("(min-width: 1181px)").addEventListener("change", (m) => m.matches && closeMenu(false));
  }

  // ---------- Count-up numbers (once, when seen) ----------
  const fmt = (n, dec) => n.toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const counters = $$("[data-count]");
  const runCount = (el) => {
    const end = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || "0", 10);
    const pre = el.dataset.prefix || "", suf = el.dataset.suffix || "";
    const plain = el.dataset.plain === "true"; // years: no thousands separator
    const show = (v) => { el.textContent = pre + (plain ? v.toFixed(dec) : fmt(v, dec)) + suf; };
    if (motionOff()) return show(end);
    const start = parseFloat(el.dataset.from || "0"), dur = 1400, t0 = performance.now();
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4);
      show(start + (end - start) * e);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if (counters.length) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { runCount(en.target); io.unobserve(en.target); }
    }), { threshold: 0.5 });
    counters.forEach((c) => io.observe(c));
  }

  // ---------- Countdown to the Summit ----------
  $$("[data-countdown]").forEach((el) => {
    const target = new Date(el.dataset.countdown).getTime();
    const parts = { d: $("[data-d]", el), h: $("[data-h]", el), m: $("[data-m]", el), s: $("[data-s]", el) };
    const tick = () => {
      let diff = Math.max(0, target - Date.now());
      const d = Math.floor(diff / 864e5); diff -= d * 864e5;
      const h = Math.floor(diff / 36e5); diff -= h * 36e5;
      const m = Math.floor(diff / 6e4); diff -= m * 6e4;
      const s = Math.floor(diff / 1e3);
      parts.d.textContent = d; parts.h.textContent = String(h).padStart(2, "0");
      parts.m.textContent = String(m).padStart(2, "0"); parts.s.textContent = String(s).padStart(2, "0");
    };
    tick();
    setInterval(() => { if (!document.hidden) tick(); }, 1000);
  });

  // ---------- Quote carousel ----------
  $$("[data-carousel]").forEach((car) => {
    const slides = $$(".qslide", car), dots = $(".qdots", car);
    let i = 0, timer = 0, hovering = false, visible = false;
    const go = (n) => {
      i = (n + slides.length) % slides.length;
      slides.forEach((s, k) => { s.classList.toggle("is-active", k === i); s.setAttribute("aria-hidden", String(k !== i)); s.inert = k !== i; });
      $$("button", dots).forEach((b, k) => b.setAttribute("aria-current", String(k === i)));
    };
    slides.forEach((_, k) => {
      const b = document.createElement("button");
      b.type = "button"; b.setAttribute("aria-label", `Show quote ${k + 1} of ${slides.length}`);
      b.addEventListener("click", () => { go(k); restart(); });
      dots.appendChild(b);
    });
    $("[data-prev]", car).addEventListener("click", () => { go(i - 1); restart(); });
    $("[data-next]", car).addEventListener("click", () => { go(i + 1); restart(); });
    const restart = () => {
      clearInterval(timer);
      if (motionOff() || hovering || !visible) return;
      timer = setInterval(() => { if (!document.hidden) go(i + 1); }, 7000);
    };
    car.addEventListener("pointerenter", () => { hovering = true; restart(); });
    car.addEventListener("pointerleave", () => { hovering = false; restart(); });
    car.addEventListener("focusin", () => { hovering = true; restart(); });
    car.addEventListener("focusout", () => { hovering = false; restart(); });
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; restart(); }).observe(car);
    go(0);
  });

  // ---------- Hero video: muted loop that alternates clips, pausable ----------
  const vid = $(".vhero video");
  const vbtn = $("[data-video-toggle]");
  if (vid) {
    const clips = (vid.dataset.clips || "").split(",").map((s) => s.trim()).filter(Boolean);
    let clip = 0, userPaused = false, onScreen = true;
    const setIcon = () => {
      if (!vbtn) return;
      const playing = !vid.paused;
      vbtn.setAttribute("aria-label", playing ? "Pause background video" : "Play background video");
      vbtn.innerHTML = playing ? '<i class="ph ph-pause"></i>' : '<i class="ph ph-play"></i>';
    };
    const load = (n) => { vid.src = clips[n]; vid.load(); };
    const sync = () => {
      if (userPaused || motionOff() || !onScreen || document.hidden) vid.pause();
      else vid.play().catch(() => {});
      setIcon();
    };
    vid.addEventListener("canplay", () => { vid.classList.add("is-ready"); sync(); });
    vid.addEventListener("ended", () => { clip = (clip + 1) % clips.length; load(clip); });
    vid.addEventListener("error", () => { // clip missing: try the next one, otherwise keep the poster photo
      if (clips.length > 1 && clip < clips.length - 1) { clip++; load(clip); }
      else if (vbtn) vbtn.hidden = true;
    });
    vid.addEventListener("play", setIcon); vid.addEventListener("pause", setIcon);
    if (clips.length) load(0);
    vbtn && vbtn.addEventListener("click", () => { userPaused = !vid.paused; sync(); if (!userPaused) vid.play().catch(() => {}); });
    new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; sync(); }).observe(vid);
    document.addEventListener("visibilitychange", sync);
    new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["class"] });
  }

  // ---------- Full film dialog ----------
  const film = $("#film");
  if (film) {
    const frame = $("iframe", film);
    $$("[data-film]").forEach((b) => b.addEventListener("click", () => { frame.src = frame.dataset.src; film.showModal(); }));
    film.addEventListener("close", () => { frame.src = "about:blank"; });
    $$("[data-close]", film).forEach((b) => b.addEventListener("click", () => film.close()));
    film.addEventListener("click", (e) => { if (e.target === film) film.close(); });
  }

  // ---------- Forms (front end only until connected to NABME's email tool / CRM) ----------
  const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
  const validateField = (field) => {
    if (field.hasAttribute("data-required-group")) { // a set of checkboxes where at least one must be ticked
      const ok = $$("input[type=checkbox]", field).some((b) => b.checked);
      field.classList.toggle("is-invalid", !ok);
      return ok;
    }
    const input = $("input, select, textarea", field);
    if (!input) return true;
    let ok = true;
    if (input.type === "checkbox") ok = !input.required || input.checked;
    else if (input.required && !input.value.trim()) ok = false;
    else if (input.type === "email" && input.value.trim() && !emailOk(input.value)) ok = false;
    else if (input.type === "url" && input.value.trim() && !/^https?:\/\/\S+\.\S+/.test(input.value.trim())) ok = false;
    field.classList.toggle("is-invalid", !ok);
    input.setAttribute("aria-invalid", String(!ok));
    return ok;
  };
  const validateScope = (scope) => {
    const fields = $$(".field", scope).filter((f) => !f.closest("[hidden]"));
    const bad = fields.filter((f) => !validateField(f));
    if (bad.length) { const inp = $("input, select, textarea", bad[0]); inp && inp.focus(); }
    return !bad.length;
  };
  $$(".field input, .field select, .field textarea").forEach((inp) => {
    inp.addEventListener("input", () => { const f = inp.closest(".field"); f.classList.contains("is-invalid") && validateField(f); });
    inp.addEventListener("blur", () => { const f = inp.closest(".field"); inp.value && validateField(f); });
  });

  // Multi-step forms
  $$("[data-steps]").forEach((wrap) => {
    const form = $("form", wrap), panels = $$(".step-panel", wrap), bar = $(".progress i", wrap);
    const label = $("[data-step-label]", wrap), count = $("[data-step-count]", wrap);
    const key = wrap.dataset.save ? "nabme-form-" + wrap.dataset.save : null;
    let i = 0;
    const show = (n) => {
      i = n;
      panels.forEach((p, k) => { p.hidden = k !== i; });
      if (bar) bar.style.setProperty("--p", ((i + 1) / panels.length) * 100 + "%");
      if (label) label.textContent = panels[i].dataset.title || "";
      if (count) count.textContent = `Step ${i + 1} of ${panels.length}`;
      const first = $("input, select, textarea", panels[i]);
      if (n > 0 && first) first.focus({ preventScroll: true });
      wrap.scrollIntoView({ block: "start", behavior: motionOff() ? "auto" : "smooth" });
    };
    if (key) { // restore saved progress
      try { const saved = JSON.parse(store.get(key) || "{}"); Object.entries(saved).forEach(([name, val]) => {
        $$(`[name="${CSS.escape(name)}"]`, form).forEach((el) => { if (el.type === "checkbox" || el.type === "radio") el.checked = [].concat(val).includes(el.value); else if (el.type !== "file") el.value = val; });
      }); } catch {}
      form.addEventListener("input", () => {
        const data = {};
        new FormData(form).forEach((v, k) => { if (v instanceof File) return; data[k] = data[k] ? [].concat(data[k], v) : v; });
        store.set(key, JSON.stringify(data));
      });
    }
    $$("[data-next]", wrap).forEach((b) => b.addEventListener("click", () => { if (validateScope(panels[i])) show(Math.min(i + 1, panels.length - 1)); }));
    $$("[data-back]", wrap).forEach((b) => b.addEventListener("click", () => show(Math.max(i - 1, 0))));
    show(0);
  });

  // Sliding photo strips: only run while on screen
  $$("[data-strip]").forEach((el) => {
    new IntersectionObserver(([e]) => el.classList.toggle("is-paused", !e.isIntersecting)).observe(el);
  });

  // "Other" role: reveal a text box to type it in
  $$("select[data-other]").forEach((sel) => {
    const box = $(`[data-other-for="${sel.id}"]`), inp = box && $("input", box);
    if (!box) return;
    const sync = () => { const on = sel.value === "Other"; box.hidden = !on; inp.required = on && sel.required; if (!on) box.classList.remove("is-invalid"); };
    sel.addEventListener("change", () => { sync(); if (!box.hidden) inp.focus(); });
    sync();
  });

  // Sends a form to /api/submit, which saves it in NABME's Airtable base.
  // Until Airtable is connected the server answers 503 "not configured", and the form shows success as before.
  const sendForm = async (form, table, extra = {}) => {
    const data = new FormData(form);
    data.set("_table", table);
    data.set("_page", location.pathname);
    Object.entries(extra).forEach(([k, v]) => data.set(k, v));
    try {
      const res = await fetch("/api/submit", { method: "POST", body: data });
      if (res.ok) return { ok: true };
      const body = await res.json().catch(() => ({}));
      if (res.status === 503 && body.configured === false) return { ok: true, preview: true };
      return { ok: false, error: body.error };
    } catch { return { ok: false }; }
  };
  const addTrap = (form) => { // hidden field people never see; bots fill it in
    const trap = document.createElement("input");
    Object.assign(trap, { type: "text", name: "company_website", tabIndex: -1, autocomplete: "off" });
    trap.setAttribute("aria-hidden", "true");
    trap.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0";
    form.appendChild(trap);
  };
  const tooBig = (form) => $$('input[type="file"][data-max-mb]', form).find((inp) => inp.files[0] && inp.files[0].size > inp.dataset.maxMb * 1048576);

  // Submit handling for every NABME form
  $$("form[data-form]").forEach((form) => {
    form.noValidate = true;
    addTrap(form);
    const wrap = form.closest(".form-wrap");
    const note = document.createElement("p");
    note.className = "form-error"; note.setAttribute("role", "alert");
    const btnRow = $("button[type=submit]", form)?.parentElement;
    (btnRow || form).appendChild(note);
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      note.textContent = "";
      if (!validateScope(form)) return;
      const big = tooBig(form);
      if (big) { note.textContent = "That file is larger than 4 MB. Please choose a smaller file."; big.focus(); return; }
      const btn = $("button[type=submit]", form);
      const label = btn ? btn.innerHTML : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      const result = await sendForm(form, form.dataset.form || "Contact Messages");
      if (btn) { btn.disabled = false; btn.innerHTML = label; }
      if (!result.ok) {
        note.textContent = (result.error ? result.error + " " : "We couldn't send this. ") + "Please try again, or email info@nabme.org.";
        return;
      }
      const saveKey = form.closest("[data-save]")?.dataset.save;
      if (saveKey) try { localStorage.removeItem("nabme-form-" + saveKey); } catch {}
      if (form.dataset.redirect) { location.href = form.dataset.redirect; return; } // e.g. Donate continues to PayPal
      if (wrap) { wrap.classList.add("is-done"); const s = $(".success", wrap); s && s.setAttribute("tabindex", "-1"); s && s.focus(); }
    });
  });

  // Inline signups (newsletter, notify me)
  $$("form[data-inline]").forEach((form) => {
    form.noValidate = true;
    const msg = $(".inline-msg", form.parentElement) || form.nextElementSibling;
    const email = $('input[type="email"]', form);
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!emailOk(email.value)) {
        email.setAttribute("aria-invalid", "true");
        if (msg) { msg.textContent = email.value ? "That email looks incomplete. Check it and try again." : "Enter your email address."; msg.classList.add("is-error"); }
        email.focus();
        return;
      }
      email.removeAttribute("aria-invalid");
      const btn = $("button", form); const label = btn.innerHTML; btn.disabled = true; btn.textContent = "Adding…";
      sendForm(form, form.dataset.table || "Newsletter", { source: form.dataset.source || "" }).then((result) => {
        if (!result.ok) {
          btn.disabled = false; btn.innerHTML = label;
          if (msg) { msg.textContent = "We couldn't add you just now. Please try again."; msg.classList.add("is-error"); }
          return;
        }
        btn.textContent = form.dataset.done || "You're on the list";
        email.readOnly = true;
        if (msg) { msg.classList.remove("is-error"); msg.textContent = form.dataset.thanks || "Thanks. Watch your inbox for NABME news."; }
        store.set("nabme-subscribed", "1");
      });
    });
  });
  $$("form[data-inline]").forEach(addTrap);

  // ---------- Job board filters (no listings yet) ----------
  const jobForm = $("[data-jobsearch]");
  if (jobForm) jobForm.addEventListener("submit", (e) => { e.preventDefault(); const out = $("[data-jobs-msg]"); out && (out.textContent = "No openings match yet. New positions are reviewed by NABME and posted here."); });

  // ---------- One newsletter pop-up: after 30s or on exit intent, desktop only ----------
  const pop = $("#newsletter-pop");
  if (pop && innerWidth >= 900 && !store.get("nabme-subscribed")) {
    const last = parseInt(store.get("nabme-pop") || "0", 10);
    if (Date.now() - last > 14 * 864e5) {
      let shown = false;
      const show = () => { if (shown || document.querySelector("dialog[open]")) return; shown = true; store.set("nabme-pop", String(Date.now())); pop.showModal(); };
      const t = setTimeout(show, 30000);
      document.addEventListener("mouseout", (e) => { if (!e.relatedTarget && e.clientY <= 0) { clearTimeout(t); show(); } });
      $$("[data-close]", pop).forEach((b) => b.addEventListener("click", () => pop.close()));
      pop.addEventListener("click", (e) => { if (e.target === pop) pop.close(); });
    }
  }

  // ---------- Pause motion toggle ----------
  $$(".motion-toggle").forEach((b) => {
    const label = () => { const off = root.classList.contains("motion-off"); b.textContent = off ? "Play motion" : "Pause motion"; b.setAttribute("aria-pressed", String(off)); };
    label();
    b.addEventListener("click", () => { root.classList.toggle("motion-off"); store.set("nabme-motion", root.classList.contains("motion-off") ? "off" : "on"); label(); });
  });

  // ---------- Year ----------
  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
