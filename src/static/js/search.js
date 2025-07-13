import { showLoading, showSlogan, showMainContent } from "./ui.js";
import { state, updateResults, applyFiltersAndUpdateResults } from "./main.js";
import { resetShareUrl } from "./share.js";

// --- Main search trigger ---
export async function triggerSearch() {
    state.currentPage = 1; // Reset to first page on new search
    state.allOffers = [];
    showLoading(); // Show loading state

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
    validateAddress(streetInput, houseNumberInput, plzInput, cityInput, errorDiv);

    if (ageInput && ageInput.value.trim() !== "") {
        const ageValue = Number(ageInput.value.trim());
        if (isNaN(ageValue) || ageValue <= 0) {
            errorDiv.textContent = "Please enter a valid age";
            errorDiv.classList.remove('d-none');
            document.getElementById('loading-spinner').classList.add('d-none');
            ageInput.focus();
            document.getElementById('loading-spinner').classList.add('d-none');
            showSlogan(); // Show slogan if age is invalid
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
        state.allOffers = [];
        // Update summary and results
        updateResults([]); 
        // Generate share URL (each time the search is triggered)
        resetShareUrl();
        showSlogan(); // Show slogan if there was an error
        return;
    }

    // Show main content (only if response is ok)
    document.getElementById('loading-placeholder').classList.add('d-none');
    showMainContent();

    // Handle streaming response
    await handleStreamingResponse(response, state.allOffers);

    document.getElementById('loading-spinner').classList.add('d-none');
    // Always show sorted offers and update summary
    applyFiltersAndUpdateResults();
}

// --- Helper functions ---

// Validate address
function validateAddress(street, houseNumber, plz, city, errorDiv) {
    if (
        !street.value.trim() ||
        !houseNumber.value.trim() ||
        !plz.value.trim() ||
        !city.value.trim()
    ) {
        // Show error above PLZ
        errorDiv.textContent = "Please fill in all address fields.";
        errorDiv.classList.remove('d-none');
        document.getElementById('loading-spinner').classList.add('d-none');
        showSlogan(); // Show slogan if address is invalid
        return;
    } else {
        // Hide error if present
        errorDiv.classList.add('d-none');
    }
}

// Handle streaming response
async function handleStreamingResponse(response, allOffers) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

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
                // Update summary and results
                applyFiltersAndUpdateResults();
            } catch (e) {
                // incomplete JSON, wait for more data
            }
        }
    }
}

