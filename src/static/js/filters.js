// Filters module for the comparison page

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

    // Reset filters button
    document.getElementById('reset-filters').addEventListener('click', () => {
        // Reset all filter controls to default values
        document.querySelectorAll('#filters input[type="checkbox"]').forEach(cb => cb.checked = false);
        document.querySelectorAll('#filters button').forEach(btn => btn.classList.remove('active'));
        ageInput.value = "";
        showAllAgesCheckbox.checked = false;

        // Reset filter state variables
        selectedSpeed = "";
        selectedLimit = "";
        selectedMaxDuration = "";
        selectedTv = "";

        // Trigger filter update logic
        applyFiltersAndUpdateResults();
    });

}

// --- Filter state management ---
// Sets the filter state based on the provided filter object (updates the UI to reflect the current filter state)
export function setFilterState(f) {
    // Speed (button group)
    if (f.speed !== undefined) {
        selectedSpeed = f.speed;
        speedButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-speed') == f.speed);
        });
    }
    // TV (button group)
    if (f.tv !== undefined) {
        selectedTv = f.tv;
        tvButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tv') == f.tv);
        });
    }
    // Data limit (button group)
    if (f.limit !== undefined) {
        selectedLimit = f.limit;
        limitButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-limit') == f.limit);
        });
    }
    // Contract duration (button group)
    if (f.duration !== undefined) {
        selectedMaxDuration = f.duration;
        durationButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-duration') == f.duration);
        });
    }
    // Connection types (checkboxes)
    if (Array.isArray(f.connection_types)) {
        connectionTypeCheckboxes.forEach(cb => {
            cb.checked = f.connection_types.includes(cb.value);
        });
    }
    // Providers (checkboxes)
    if (Array.isArray(f.providers)) {
        providerCheckboxes.forEach(cb => {
            cb.checked = f.providers.includes(cb.value);
        });
    }
    // Installation included (checkbox)
    if (typeof f.installation !== "undefined") {
        installCheckbox.checked = !!f.installation;
    }
    // Age input
    if (f.age !== undefined) {
        ageInput.value = f.age;
    }
    // Show all ages (checkbox)
    if (typeof f.showAllAges !== "undefined") {
        showAllAgesCheckbox.checked = !!f.showAllAges;
    }
    // Sort select
    if (f.sort !== undefined) {
        selectedSort = f.sort;
        sortBySelect.value = f.sort;
    }
}