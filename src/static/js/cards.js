// --- Function to create a card for an internet offer ---
/**
 * Creates a card element for displaying an internet offer.
 * @param {Object} offer - The internet offer data.
 * @returns {HTMLElement} The card element containing the offer details.
 */

export function createCard(offer) { 
const col = document.createElement('div');
        col.className = 'col-12 mb-3';

        // Card hover effect
        col.addEventListener('mouseenter', () => {
            col.querySelector('.card').style.borderColor = '#A8A8A9';
            col.querySelector('.card').style.boxShadow = '0 0 0 0.2px #A8A8A9';
        });
        col.addEventListener('mouseleave', () => {
            col.querySelector('.card').style.borderColor = '';
            col.querySelector('.card').style.boxShadow = '';
        });

        // Card container
        const card = document.createElement('div');
        card.className = 'card h-100 p-3 justify-content-between';
        card.style.fontSize = '0.93rem';
        card.style.lineHeight = '1.2';

        // Card content row
        const row = document.createElement('div');
        row.className = 'd-flex justify-content-between align-items-start flex-row';

        // --- Left: Logo, name and info ---
        const left = document.createElement('div');
        left.className = 'd-flex flex-row align-items-start justify-content-start';
        left.style.minWidth = '0';

        // Image
        const img = document.createElement('img');
        img.className = 'rounded';
        img.alt = offer.provider + ' logo';
        img.src = `/static/images/${offer.provider}.jpeg`;
        img.style.width = '120px';
        img.style.height = '120px';

        // Name and info
        const nameContainer = document.createElement('div');
        nameContainer.className = 'ms-3 d-flex flex-column justify-content-start';
        nameContainer.style.fontSize = '0.98em';

        // Product name and details (age restriction, TV info)
        const infoContainer = document.createElement('div');
        infoContainer.style = 'flex-column justify-content-start';
        infoContainer.style.height = '95px'

        // Product name
        const title = document.createElement('div');
        title.className = 'fs-5 product-title fw-semibold mb-2';
        title.textContent = offer.name;
        infoContainer.appendChild(title);

        // Age restriction
        if (offer.max_age) {
            const ageWarning = document.createElement('div');
            ageWarning.className = 'small mb-1';
            ageWarning.style.fontSize = '0.92em';
            ageWarning.innerHTML = '&#9888; only for people under ' + offer.max_age;
            infoContainer.appendChild(ageWarning);
        }
        // TV info
        if (offer.tv) {
            const tvInfo = document.createElement('div');
            tvInfo.className = 'small mb-1';
            tvInfo.style.fontSize = '0.92em';
            tvInfo.innerHTML = '&#10003; incl. TV';
            infoContainer.appendChild(tvInfo);
        }
        nameContainer.appendChild(infoContainer);
        // Filler for spacing
        // const filler = document.createElement('div');
        // filler.style = 'flex-grow:1;';
        // nameContainer.appendChild(filler);

        // --- More info link (expand/collapse) ---
        const moreInfoContainer = document.createElement('div');
        moreInfoContainer.className = 'flex-column justify-content-start';

        const moreInfoLink = document.createElement('span');
        moreInfoLink.textContent = 'More info';
        moreInfoLink.style.cursor = 'pointer';
        moreInfoLink.className = 'small mb-1';
        moreInfoLink.tabIndex = 0;
        moreInfoLink.style.fontSize = '0.93em';

        // Hover underline
        moreInfoLink.addEventListener('mouseenter', () => {
            moreInfoLink.style.textDecoration = 'underline solid';
        });
        moreInfoLink.addEventListener('mouseleave', () => {
            moreInfoLink.style.textDecoration = '';
        });

        // Expand/collapse logic
        let expanded = false;
        let detailsDiv = null;
        moreInfoLink.addEventListener('click', () => {
            expanded = !expanded;
            const card = moreInfoLink.closest('.card');
            // On expand, set card height to auto to fit content
            if (expanded) {
                card.style.transition = 'all 0.2s';
                detailsDiv = document.createElement('div');
                detailsDiv.className = 'mt-2 small border-top pt-2';
                detailsDiv.style.fontSize = '0.92em';
                // set DSL connection type to "DSL" if it is lowercase
                let connectionType = offer.connection_type;
                if (connectionType && connectionType.toLowerCase() === 'dsl') {
                    connectionType = 'DSL';
                }
                // display additional details
                detailsDiv.innerHTML = `
                    <strong>Provider:</strong> ${offer.provider}<br>
                    <strong>Product:</strong> ${offer.name}<br>
                    <strong>Connection:</strong> ${connectionType}<br>
                    <strong>Min. contract duration:</strong> ${offer.duration_months} months<br>
                    <strong>Data limit:</strong> ${offer.limit_from_gb ? offer.limit_from_gb + ' GB' : 'Unlimited'}<br>
                    <strong>Installation included:</strong> ${offer.installation_included ? 'Yes' : 'No'}<br>
                    <strong>TV:</strong> ${offer.tv ? offer.tv : 'Not included'}<br>
                `;
                nameContainer.appendChild(detailsDiv);
                moreInfoLink.textContent = 'Less info';
                // Adjust card height to how it was before
            } else {
                card.style.minHeight = '';
                nameContainer.style.minHeight = '';
                // Remove addition details when collapsed
                if (detailsDiv) {
                    detailsDiv.remove();
                    detailsDiv = null;
                }
                moreInfoLink.textContent = 'More info';
            }
        });

        // Build more info container
        moreInfoContainer.appendChild(moreInfoLink);
        nameContainer.appendChild(moreInfoContainer);

        // Build left side of the card
        left.appendChild(img);
        left.appendChild(nameContainer);

        // --- Center and right: speed and price ---
        const centerRight = document.createElement('div');
        centerRight.className = 'd-flex justify-content-end align-items-right';
        centerRight.style.width = '40%';

        // --- Speed ---
        const speed = document.createElement('div');
        speed.className = 'fw-medium fs-4';
        speed.style.width = '50%';
        speed.textContent = `${offer.speed_mbps} Mbps`;
        centerRight.appendChild(speed);

        // --- Price ---
        const priceContainer = document.createElement('div');
        priceContainer.className = 'd-flex flex-column align-items-end';
        priceContainer.style.width = '50%';

        // Original price and discount
        if (offer.cost_eur && offer.cost_first_years_eur && offer.cost_eur !== offer.cost_first_years_eur) {
            const priceOriginalContainer = document.createElement('div');
            priceOriginalContainer.className = 'd-flex align-items-right justify-content-end w-100';

            const priceOriginal = document.createElement('div');
            priceOriginal.className = 'text-muted text-decoration-line-through me-2';
            priceOriginal.style.fontSize = '0.98em';
            priceOriginal.textContent = `€${offer.cost_eur.toFixed(2)}`;
            priceOriginalContainer.appendChild(priceOriginal);

            const discountPercent = ((offer.cost_eur - offer.cost_first_years_eur) / offer.cost_eur * 100).toFixed(0);
            const discountLabel = document.createElement('span');
            discountLabel.className = 'text-danger';
            discountLabel.style.fontSize = '0.98em';
            discountLabel.textContent = `-${discountPercent}%`;
            priceOriginalContainer.appendChild(discountLabel);

            priceContainer.appendChild(priceOriginalContainer);
        }

        // Promotional price
        const price = document.createElement('div');
        price.className = 'fw-bold text fs-4';
        const priceValue = offer.cost_first_years_eur;
        price.textContent = `€${priceValue ? priceValue.toFixed(2) : "N/A"}`;
        priceContainer.appendChild(price);

        // Price label ("Mean cost per month")
        const priceLabel = document.createElement('div');
        priceLabel.className = 'small text-muted';
        priceLabel.style.fontSize = '0.93em';
        priceLabel.textContent = 'Mean cost per month';
        priceContainer.appendChild(priceLabel);

        // Spacer between price and after two years price
        const spacer = document.createElement('div');
        spacer.style.height = '0.3em';
        priceContainer.appendChild(spacer);

        // After two years price
        const afterTwoYears = document.createElement('div');
        afterTwoYears.className = 'small text-end w-100';
        afterTwoYears.style.fontSize = '0.93em';
        afterTwoYears.textContent = `after 24 month: €${offer.after_two_years_eur.toFixed(2)}`;
        priceContainer.appendChild(afterTwoYears);
        centerRight.appendChild(priceContainer);

        // Assemble card
        row.appendChild(left);
        row.appendChild(centerRight);
        card.appendChild(row);
        col.appendChild(card);
        // Return the complete card element
        return col;
    }