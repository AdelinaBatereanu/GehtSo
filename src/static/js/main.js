import {
    installCheckbox,
    ageInput,
    showAllAgesCheckbox,
    selectedSpeed,
    selectedLimit,
    selectedMaxDuration,
    selectedTv,
    selectedSort,
    getSelectedConnectionTypes,
    getSelectedProviders,
    initFilters,
} from './filters.js';
import { createCard } from './cards.js';

// --- Sample offers for demo (used if no query params) ---
const sampleOffer = {
    provider: "ByteMe",
    name: "Super Fast Internet 1000",
    speed_mbps: 1000,
    cost_first_years_eur: 29.99,
    cost_eur: 34.99,
    duration_months: 24,
    tv: "TV Super",
    limit_from_gb: null,
    connection_type: "fiber",
    installation_included: true,
    max_age: 25,
    after_two_years_eur: 37.99
};
const sampleOffer2 = {
    provider: "ByteMe",
    name: "Super Fast Internet 1000",
    speed_mbps: 1000,
    cost_first_years_eur: 29.99,
    cost_eur: 34.99,
    duration_months: 24,
    tv: null,
    limit_from_gb: null,
    connection_type: "fiber",
    installation_included: true,
    max_age: null,
    after_two_years_eur: 37.99
};

// --- State and DOM references ---
let allOffers = [];

const searchBtn = document.getElementById('search-btn');

// --- Main search trigger ---
function triggerSearch() {
    console.log('Search triggered');
    // Get address fields
    const streetInput = document.getElementById('street');
    const houseNumberInput = document.getElementById('house_number');
    const plzInput = document.getElementById('plz');
    const cityInput = document.getElementById('city');

    // Validate address
    if (
        !streetInput.value.trim() ||
        !houseNumberInput.value.trim() ||
        !plzInput.value.trim() ||
        !cityInput.value.trim()
    ) {
        alert('Please fill in all address fields.');
        return;
    }

    // Restore connection type checkboxes from URL
    const typesFromUrl = getParam('connection_types', '').split(',').filter(Boolean);

    // Build query params for API
    const params = new URLSearchParams();
    params.set('street', streetInput.value.trim());
    params.set('house_number', houseNumberInput.value.trim());
    params.set('plz', plzInput.value.trim());
    params.set('city', cityInput.value.trim());

    // Fetch offers from backend
    const apiUrl = `/offers?${params.toString()}`;
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not OK');
            return response.json();
        })
        .then(data => {
            allOffers = data;
            applyFiltersAndUpdateResults();
        })
        .catch(err => console.error('Fetch error:', err));
}

// --- Update shareable URL and browser history ---
function updateShareUrlAndHistory() {
    // Gather all filter values
    const street = document.getElementById('street').value.trim();
    const houseNumber = document.getElementById('house_number').value.trim();
    const plz = document.getElementById('plz').value.trim();
    const city = document.getElementById('city').value.trim();

    const params = new URLSearchParams();
    if (street) params.set('street', street);
    if (houseNumber) params.set('house_number', houseNumber);
    if (plz) params.set('plz', plz);
    if (city) params.set('city', city);
    if (selectedSpeed) params.set('speed', selectedSpeed);
    if (selectedLimit) params.set('limit', selectedLimit);
    if (selectedMaxDuration) params.set('duration', selectedMaxDuration);
    if (selectedTv) params.set('tv', selectedTv);

    const selectedTypes = getSelectedConnectionTypes();
    if (selectedTypes.length > 0) params.set('connection_types', selectedTypes.join(','));

    const selectedProviders = getSelectedProviders();
    if (selectedProviders.length > 0) params.set('providers', selectedProviders.join(','));

    if (installCheckbox.checked) params.set('installation', 'true');
    if (!showAllAgesCheckbox.checked && ageInput.value.trim() !== "") {
        params.set('age', ageInput.value.trim());
    }
    if (selectedSort) params.set('sort', selectedSort);

    // Update browser URL and share field
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
    document.getElementById('share_url').value = window.location.href;
}

// --- Render offer cards in results area ---
function updateResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    data.forEach(offer => {
        const cardElement = createCard(offer);
        resultsDiv.appendChild(cardElement);
    });

    const providers = new Set(data.map(o => o.provider));
    const summary = `Found ${data.length} offer${data.length !== 1 ? 's' : ''} from ${providers.size} provider${providers.size !== 1 ? 's' : ''}`;
    document.getElementById('offers-summary').textContent = summary;

    // Update share field
    document.getElementById('share_url').value = window.location.href;
}

// --- On page load: initialize filters, restore state from URL, set up events ---
document.addEventListener('DOMContentLoaded', () => {
    // Show sample offers if no query params
    if (!window.location.search) {
        updateResults([sampleOffer, sampleOffer2]);
    }

    // Prefill address fields from URL
    const street = getParam('street', '');
    const houseNumber = getParam('house_number', '');
    const plz = getParam('plz', '');
    const city = getParam('city', '');
    document.getElementById('street').value = street;
    document.getElementById('house_number').value = houseNumber;
    document.getElementById('plz').value = plz;
    document.getElementById('city').value = city;

    // If all address fields are present, trigger search
    if (street && houseNumber && plz && city) {
        triggerSearch();
    }
    // Search button
    searchBtn.addEventListener('click', triggerSearch);
});

// --- Helper: get URL parameter or default ---
function getParam(name, defaultValue) {
    const params = new URLSearchParams(window.location.search);
    return params.has(name) ? params.get(name) : defaultValue;
}

// --- Apply all filters and update results ---
export function applyFiltersAndUpdateResults() {
    let filtered = allOffers;

    // Speed filter
    if (selectedSpeed) {
        filtered = filtered.filter(o => o.speed_mbps >= Number(selectedSpeed));
    }
    // Data limit filter
    if (selectedLimit && selectedLimit !== "none") {
        filtered = filtered.filter(o => !o.limit_from_gb || o.limit_from_gb >= Number(selectedLimit));
    }
    if (selectedLimit === "none") {
        filtered = filtered.filter(o => !o.limit_from_gb);
    }
    // Contract duration filter
    if (selectedMaxDuration) {
        filtered = filtered.filter(o => o.duration_months <= Number(selectedMaxDuration));
    }
    // TV filter
    if (selectedTv) {
        filtered = filtered.filter(o => selectedTv === "true" ? o.tv : !o.tv);
    }
    // Connection type filter
    const selectedTypes = getSelectedConnectionTypes();
    if (selectedTypes.length > 0) {
        filtered = filtered.filter(o => selectedTypes.includes(o.connection_type));
    }
    // Provider filter
    const selectedProviders = getSelectedProviders();
    if (selectedProviders.length > 0) {
        filtered = filtered.filter(o => selectedProviders.includes(o.provider));
    }
    // Installation included filter
    if (installCheckbox.checked) {
        filtered = filtered.filter(o => o.installation_included);
    }
    // Age filter
    if (!showAllAgesCheckbox.checked && ageInput.value.trim() !== "") {
        const userAge = Number(ageInput.value.trim());
        if (!isNaN(userAge)) {
            filtered = filtered.filter(o => !o.max_age || userAge <= o.max_age);
        }
    }

    // Sorting
    if (selectedSort === "cost_first_years_eur") {
        filtered = filtered.slice().sort((a, b) => a.cost_first_years_eur - b.cost_first_years_eur);
    } else if (selectedSort === "after_two_years_eur") {
        filtered = filtered.slice().sort((a, b) => a.after_two_years_eur - b.after_two_years_eur);
    } else if (selectedSort === "speed_mbps") {
        filtered = filtered.slice().sort((a, b) => b.speed_mbps - a.speed_mbps);
    }

    updateResults(filtered);
    updateShareUrlAndHistory();
}

initFilters({ getParam, applyFiltersAndUpdateResults });
