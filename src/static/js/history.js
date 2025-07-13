import {
    selectedSpeed,
    selectedLimit,
    selectedMaxDuration,
    selectedTv,
    selectedSort,
    getSelectedConnectionTypes,
    getSelectedProviders,
    installCheckbox,
    showAllAgesCheckbox,
    ageInput
} from './filters.js';

// --- Update browser history ---
export function updateHistory() {
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
