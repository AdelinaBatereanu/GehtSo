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

import { setupShare, resetShareUrl } from './share.js';
import { createCard } from './card.js';
import { setFilterState } from './filters.js';

let allOffers = [];

// --- Main search trigger ---
async function triggerSearch() {
    allOffers = [];

    // Show loading spinner
    document.getElementById('loading-spinner').classList.remove('d-none');

    console.log('Search triggered');
    // Get address fields
    const streetInput = document.getElementById('street');
    const houseNumberInput = document.getElementById('house_number');
    const plzInput = document.getElementById('plz');
    const cityInput = document.getElementById('city');
    const errorDiv = document.getElementById('address-error');
    const ageInput = document.getElementById('age_input');

    // Validate address
    if (
        !streetInput.value.trim() ||
        !houseNumberInput.value.trim() ||
        !plzInput.value.trim() ||
        !cityInput.value.trim()
    ) {
        // Show error above PLZ
        errorDiv.textContent = "Please fill in all address fields.";
        errorDiv.classList.remove('d-none');
        document.getElementById('loading-spinner').classList.add('d-none');
        return;
    } else {
        // Hide error if present
        errorDiv.classList.add('d-none');
    }

    if (ageInput && ageInput.value.trim() !== "") {
        const ageValue = Number(ageInput.value.trim());
        if (isNaN(ageValue) || ageValue <= 0) {
            errorDiv.textContent = "Please enter a valid age";
            errorDiv.classList.remove('d-none');
            document.getElementById('loading-spinner').classList.add('d-none');
            ageInput.focus();
            document.getElementById('loading-spinner').classList.add('d-none');
            return;
        }
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
    if (!response.ok) {
        const errorDiv = document.getElementById('address-error');
        let errorMsg = "An error occurred. Please try again.";
        try {
            const errorData = await response.json();
            if (errorData && errorData.error) {
                if (errorData.error === "Invalid address.") {
                    errorMsg = "The address could not be found. Please check your input.";
                } else {
                    errorMsg = errorData.error;
                }
            }
        } catch (e) {}
        errorDiv.textContent = errorMsg;
        errorDiv.classList.remove('d-none');
        document.getElementById('loading-spinner').classList.add('d-none');
        // Clear previous results
        allOffers = [];
        // Update summary and results
        updateResults([]); 
        // Generate share URL (each time the search is triggered)
        resetShareUrl();
        return;
    }

    // Show main content (only if response is ok)
    document.getElementById('main-content').classList.remove('d-none');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

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
    document.getElementById('loading-spinner').classList.add('d-none');}

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

    // Prefill address fields from URL ONLY if present
    const street = getParam('street', null);
    const houseNumber = getParam('house_number', null);
    const plz = getParam('plz', null);
    const city = getParam('city', null);

    if (street !== null) document.getElementById('street').value = street;
    if (houseNumber !== null) document.getElementById('house_number').value = houseNumber;
    if (plz !== null) document.getElementById('plz').value = plz;
    if (city !== null) document.getElementById('city').value = city;

    // Clear other address fields when PLZ changes
    const plzInput = document.getElementById('plz');
    const streetInput = document.getElementById('street');
    const houseNumberInput = document.getElementById('house_number');
    const cityInput = document.getElementById('city');

    if (plzInput && streetInput && houseNumberInput && cityInput) {
        plzInput.addEventListener('input', () => {
            streetInput.value = '';
            houseNumberInput.value = '';
            cityInput.value = '';
        });
    }

    // Search button event
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', triggerSearch);
    }

    // Restore filter state from URL and load snapshot if available
    if (window.snapshotOffers && Array.isArray(window.snapshotOffers)) {
        document.getElementById('main-content').classList.remove('d-none');

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

    // Create share URL and set up sharing buttons
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
    // Generate share URL each time filters are applied
    resetShareUrl();
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
