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

import { setupShare } from './share.js';
import { createCard } from './card.js';
import { setFilterState } from './filters.js';

let allOffers = [];

// --- Main search trigger ---
async function triggerSearch() {
    document.getElementById('loading-spinner').style.display = 'block';

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

    // Build query params for API
    const params = new URLSearchParams();
    params.set('street', streetInput.value.trim());
    params.set('house_number', houseNumberInput.value.trim());
    params.set('plz', plzInput.value.trim());
    params.set('city', cityInput.value.trim());

    // Fetch offers from backend
    const apiUrl = `/offers?${params.toString()}`;
    const response = await fetch(apiUrl);

    // Check for errors
    const reader = response.body.getReader();
    let decoder = new TextDecoder();
    let buffer = '';
    let resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    allOffers = [];

    // Handle streaming response
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // Split buffer into complete JSON objects
        let offers = buffer.split('\n');
        buffer = offers.pop(); // last chunk may be incomplete

        // Process each complete offer
        for (let offerStr of offers) {
            if (!offerStr.trim()) continue;
            try {
                let offer = JSON.parse(offerStr);
                allOffers.push(offer);
                // Always show sorted offers
                applyFiltersAndUpdateResults();
                // Update results immediately
                updateSummary();
            } catch (e) {
                // incomplete JSON, wait for more data
            }
        }
    }
    document.getElementById('loading-spinner').style.display = 'none';
}

// --- Update browser history ---
function updateHistory() {
    // Get current filter values
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

    // Update browser URL
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
}

// --- Update summary text based on current offers ---
function updateSummary(data) {
    const providers = new Set(data.map(o => o.provider));
    const summary = `Found ${data.length} offer${data.length !== 1 ? 's' : ''} from ${providers.size} provider${providers.size !== 1 ? 's' : ''}`;
    document.getElementById('offers-summary').textContent = summary;
}

// --- Render offer cards in results area ---
function updateResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    data.forEach(offer => {
        const cardElement = createCard(offer);
        resultsDiv.appendChild(cardElement);
    });
}

// --- On page load: initialize filters, restore state from URL, set up events ---
document.addEventListener('DOMContentLoaded', () => {

    // Prefill address fields from URL
    const street = getParam('street', '');
    const houseNumber = getParam('house_number', '');
    const plz = getParam('plz', '');
    const city = getParam('city', '');
    document.getElementById('street').value = street;
    document.getElementById('house_number').value = houseNumber;
    document.getElementById('plz').value = plz;
    document.getElementById('city').value = city;

    if (window.snapshotOffers && Array.isArray(window.snapshotOffers)) {
        allOffers = window.snapshotOffers;

        if (window.snapshotFilters) {
            setFilterState(window.snapshotFilters);
        }
        
        applyFiltersAndUpdateResults();
        updateSummary && updateSummary();
        // Hide the loading spinner if present
        const spinner = document.getElementById('loading-spinner');
        if (spinner) spinner.style.display = 'none';
        return; // Don't auto-trigger search if snapshot is loaded
    }

    // If all address fields are present, trigger search
    if (street && houseNumber && plz && city) {
        triggerSearch();
    }

    setupShare({
        getOffers: () => allOffers,
        getFilters: () => ({
            speed: selectedSpeed,
            limit: selectedLimit,
            duration: selectedMaxDuration,
            tv: selectedTv,
            connection_types: getSelectedConnectionTypes(),
            providers: getSelectedProviders(),
            installation: installCheckbox.checked,
            age: ageInput.value.trim(),
            showAllAges: showAllAgesCheckbox.checked,
            sort: selectedSort,
        })
    });
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

    updateSummary(filtered);
    updateResults(filtered);
    updateHistory();
}

initFilters({ getParam, applyFiltersAndUpdateResults });
