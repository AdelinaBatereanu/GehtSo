// Helper to clear suggestions
function clearList(el) {
    el.innerHTML = "";
  }
  
  // Render a list of items under given <ul>
  function renderList(el, items, onClick) {
    clearList(el);
    items.forEach(item => {
      const li = document.createElement("li");
      li.textContent = item.display;
      li.addEventListener("click", () => onClick(item));
      el.appendChild(li);
    });
  }
  
  // Debounce factory
  function debounce(fn, delay=300) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }
  
document.addEventListener('DOMContentLoaded', function() {
  
  // --- PLZ field ---
  const plzInput = document.getElementById("plz");
  const plzList  = document.getElementById("plz-suggestions");
  const cityInput= document.getElementById("city");
  
  plzInput.addEventListener("input", debounce(() => {
    const q = plzInput.value.trim();
    if (q.length < 1) { clearList(plzList); return; }
  
    fetch(`/autocomplete?q=${encodeURIComponent(q)}&field=plz`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        renderList(plzList, data, item => {
          plzInput.value = item.postcode;
          cityInput.value = item.city;
          clearList(plzList);
        });
      })
      .catch(() => clearList(plzList));
  }));
  
  // --- Street field ---
  const streetInput = document.getElementById("street");
  const streetList  = document.getElementById("street-suggestions");
  
  streetInput.addEventListener("input", debounce(() => {
    const q = streetInput.value.trim();
    const city = cityInput.value.trim();
    if (q.length < 1 || !city) { clearList(streetList); return; }
  
    fetch(`/autocomplete?q=${encodeURIComponent(q)}&field=street&city=${encodeURIComponent(city)}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        renderList(streetList, data, item => {
          streetInput.value = item.display;
          clearList(streetList);
        });
      })
      .catch(() => clearList(streetList));
  }));
});