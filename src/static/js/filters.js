// Filter controls
export const installCheckbox = document.getElementById('installation_included');
export const speedButtons = document.querySelectorAll('#speed-buttons button');
export const limitButtons = document.querySelectorAll('#limit-buttons button');
export const connectionTypeCheckboxes = document.querySelectorAll('.connection-type');
export const durationButtons = document.querySelectorAll('#duration-buttons button');
export const tvButtons = document.querySelectorAll('#tv-buttons button');
export const providerCheckboxes = document.querySelectorAll('.provider');
export const ageInput = document.getElementById('age_input');
export const showAllAgesCheckbox = document.getElementById('show_all_ages');
export const sortBySelect = document.getElementById('sort_by');

// Filter state
export let selectedSpeed = "";
export let selectedLimit = "";
export let selectedMaxDuration = "";
export let selectedTv = "";
export let selectedSort = sortBySelect.value;

// --- Helper functions for filters ---
export function getSelectedConnectionTypes() {
    // Returns array of checked connection types
    return Array.from(connectionTypeCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
}
export function getSelectedProviders() {
    return Array.from(providerCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
}

export function initFilters({ getParam, applyFiltersAndUpdateResults }) {
        // Restore connection type checkboxes from URL
        const typesFromUrl = getParam('connection_types', '').split(',').filter(Boolean);
        connectionTypeCheckboxes.forEach(cb => {
            cb.checked = typesFromUrl.includes(cb.value);
            cb.addEventListener('change', applyFiltersAndUpdateResults);
        });

    // Speed buttons
    selectedSpeed = getParam('speed', "");
    speedButtons.forEach(b => {
        b.classList.toggle('active', b.dataset.speed === selectedSpeed);
        b.addEventListener('click', () => {
            selectedSpeed = b.dataset.speed;
            speedButtons.forEach(btn => btn.classList.remove('active'));
            b.classList.add('active');
            applyFiltersAndUpdateResults();
        });
    });

    // Limit buttons
    selectedLimit = getParam('limit', "");
    limitButtons.forEach(b => {
        b.classList.toggle('active', b.dataset.limit === selectedLimit);
        b.addEventListener('click', () => {
            selectedLimit = b.dataset.limit;
            limitButtons.forEach(btn => btn.classList.remove('active'));
            b.classList.add('active');
            applyFiltersAndUpdateResults();
        });
    });

    // Duration buttons
    selectedMaxDuration = getParam('duration', "");
    durationButtons.forEach(b => {
        b.classList.toggle('active', b.dataset.duration === selectedMaxDuration);
        b.addEventListener('click', () => {
            selectedMaxDuration = b.dataset.duration;
            durationButtons.forEach(btn => btn.classList.remove('active'));
            b.classList.add('active');
            applyFiltersAndUpdateResults();
        });
    });

    // TV buttons
    selectedTv = getParam('tv', "");
    tvButtons.forEach(b => {
        b.classList.toggle('active', b.dataset.tv === selectedTv);
        b.addEventListener('click', () => {
            selectedTv = b.dataset.tv;
            tvButtons.forEach(btn => btn.classList.remove('active'));
            b.classList.add('active');
            applyFiltersAndUpdateResults();
        });
    });

    // Installation included checkbox
    installCheckbox.checked = getParam('installation', 'false') === 'true';
    installCheckbox.addEventListener('change', applyFiltersAndUpdateResults);

    // Provider checkboxes from URL
    const providersFromUrl = getParam('providers', '').split(',').filter(Boolean);
    providerCheckboxes.forEach(cb => {
        cb.checked = providersFromUrl.includes(cb.value);
        cb.addEventListener('change', applyFiltersAndUpdateResults);
    });

    // Age input: typing disables "show all offers"
    ageInput.addEventListener('input', () => {
        if (ageInput.value.trim() !== "") {
            showAllAgesCheckbox.checked = false;
        }
        applyFiltersAndUpdateResults();
    });

    // "Show all offers" disables age input
    showAllAgesCheckbox.addEventListener('change', () => {
        if (showAllAgesCheckbox.checked) {
            ageInput.value = "";
        }
        applyFiltersAndUpdateResults();
    });

    // Sort select
    sortBySelect.addEventListener('change', () => {
        selectedSort = sortBySelect.value;
        applyFiltersAndUpdateResults();
    });
    selectedSort = getParam('sort', sortBySelect.value);
    sortBySelect.value = selectedSort;

}