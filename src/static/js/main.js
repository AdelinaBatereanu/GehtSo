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
    setFilterState
} from './filters.js';

import { resetShareUrl } from './share.js';
import { createCard } from './card.js';
import { updateHistory } from './history.js';
import { updateSummary } from './summary.js';
import { renderPagination } from './pagination.js';
import { setupShare } from './share.js';
import { showMainContent, showSlogan } from './ui.js';
import { triggerSearch } from './search.js';

// Initialize page size for pagination
export const pageSize = 10; // Offers per page

// Global state for current page and offers
export const state = {
    currentPage: 1,
    allOffers: []
};

// --- Render offer cards in results area ---
export function updateResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    // Pagination logic
    const start = (state.currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageOffers = data.slice(start, end);

    pageOffers.forEach(offer => {
        const cardElement = createCard(offer);
        resultsDiv.appendChild(cardElement);
    });

    renderPagination(data.length, pageSize);
}

// --- Helper: get URL parameter or default ---
function getParam(name, defaultValue) {
    const params = new URLSearchParams(window.location.search);
    return params.has(name) ? params.get(name) : defaultValue;
}

// --- Apply all filters and update results ---
export function applyFiltersAndUpdateResults() {
    // Generate share URL each time filters are applied
    resetShareUrl();
    let filtered = state.allOffers;

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
    
    // Only reset if the current page is out of range (e.g. after filtering reduces results)
    if ((state.currentPage - 1) * pageSize >= filtered.length) {
        state.currentPage = 1;
    }

    updateSummary(filtered);
    updateResults(filtered);
    updateHistory();
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
        showMainContent();

        state.allOffers = window.snapshotOffers;

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
    } else {
        showSlogan(); // <--- Add this here
    }

    // Create share URL and set up sharing buttons
    setupShare({
        getOffers: () => state.allOffers,
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


initFilters({ getParam, applyFiltersAndUpdateResults });

