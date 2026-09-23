(() => {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const code = btn.closest(".cmd")?.querySelector("code");
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code.textContent);
        const old = btn.textContent;
        btn.textContent = "کپی شد";
        setTimeout(() => { btn.textContent = old; }, 1200);
      } catch (err) {
        btn.textContent = "ناموفق";
      }
    });
  });

  const input = document.querySelector("[data-live-search]");
  const box = document.querySelector("[data-suggest]");
  if (!input || !box) return;

  const hide = () => { box.hidden = true; box.innerHTML = ""; };
  input.addEventListener("input", async () => {
    const q = input.value.trim();
    if (q.length < 2) { hide(); return; }
    const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!data.results.length) { hide(); return; }
    box.innerHTML = data.results
      .map((item) => `<a href="${item.url}">${item.is_flow ? "فلو" : "عمل"} · ${item.title}</a>`)
      .join("");
    const r = input.getBoundingClientRect();
    box.style.top = `${r.bottom + window.scrollY + 6}px`;
    box.style.left = `${r.left + window.scrollX}px`;
    box.style.width = `${r.width}px`;
    box.hidden = false;
  });
  document.addEventListener("click", (e) => {
    if (!box.contains(e.target) && e.target !== input) hide();
  });
})();
