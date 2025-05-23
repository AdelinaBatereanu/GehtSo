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
            row.className = 'd-flex align-items-start';

            // --- Left: Logo and name ---
            const left = document.createElement('div');
            left.className = 'd-flex flex-row align-items-start justify-content-start';
            left.style.minWidth = '0';

            const img = document.createElement('img');
            img.className = 'rounded';
            img.alt = offer.provider + ' logo';
            img.src = `/static/images/${offer.provider}.jpeg`;
            img.style.width = '120px';
            img.style.height = '120px';

            // Name and info
            const nameContainer = document.createElement('div');
            nameContainer.className = 'ms-3 d-flex flex-column justify-content-start';
            nameContainer.style.height = '110px';
            nameContainer.style.fontSize = '0.98em';

            const title = document.createElement('div');
            title.className = 'fs-5 product-title fw-semibold mb-2';
            title.textContent = offer.name;
            nameContainer.appendChild(title);

            // Age restriction
            if (offer.max_age) {
                const ageWarning = document.createElement('div');
                ageWarning.className = 'small mb-1';
                ageWarning.style.fontSize = '0.92em';
                ageWarning.innerHTML = '&#9888; Available for people under ' + offer.max_age;
                nameContainer.appendChild(ageWarning);
            }
            // TV info
            if (offer.tv) {
                const tvInfo = document.createElement('div');
                tvInfo.className = 'small mb-1';
                tvInfo.style.fontSize = '0.92em';
                tvInfo.innerHTML = '&#10003; incl. TV';
                nameContainer.appendChild(tvInfo);
            }
            // Filler for spacing
            const filler = document.createElement('div');
            filler.style = 'flex-grow:1;';
            nameContainer.appendChild(filler);

            // --- More info link (expand/collapse) ---
            const moreInfoContainer = document.createElement('div');
            moreInfoContainer.className = 'mt-auto align-end';

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
                if (expanded) {
                    card.style.transition = 'all 0.2s';
                    card.style.minHeight = '280px';
                    detailsDiv = document.createElement('div');
                    detailsDiv.className = 'mt-2 small border-top pt-2';
                    detailsDiv.style.fontSize = '0.92em';
                    detailsDiv.innerHTML = `
                        <strong>Provider:</strong> ${offer.provider}<br>
                        <strong>Product:</strong> ${offer.name}<br>
                        <strong>Connection:</strong> ${offer.connection_type}<br>
                        <strong>Min. contract duration:</strong> ${offer.duration_months} months<br>
                        <strong>Data limit:</strong> ${offer.limit_from_gb ? offer.limit_from_gb + ' GB' : 'Unlimited'}<br>
                        <strong>Installation included:</strong> ${offer.installation_included ? 'Yes' : 'No'}<br>
                        <strong>TV:</strong> ${offer.tv ? offer.tv : 'Not included'}<br>
                    `;
                    nameContainer.style.minHeight = '239px';
                    nameContainer.appendChild(detailsDiv);
                    moreInfoLink.textContent = 'Less info';
                } else {
                    card.style.minHeight = '';
                    nameContainer.style.minHeight = '';
                    nameContainer.style.height = '110px';
                    if (detailsDiv) {
                        detailsDiv.remove();
                        detailsDiv = null;
                    }
                    moreInfoLink.textContent = 'More info';
                }
            });

            moreInfoContainer.appendChild(moreInfoLink);
            nameContainer.appendChild(moreInfoContainer);

            left.appendChild(img);
            left.appendChild(nameContainer);

            const centerRight = document.createElement('div');
            centerRight.className = 'd-flex justify-content-end align-items-right flex-grow-1';
            centerRight.style.width = '260px';

            const speed = document.createElement('div');
            speed.className = 'fw-medium fs-4';
            speed.textContent = `${offer.speed_mbps} Mbps`;
            centerRight.appendChild(speed);

            // --- Right: Price ---
            const priceContainer = document.createElement('div');
            priceContainer.className = 'd-flex flex-column align-items-end';
            priceContainer.style.width = '200px';

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

            // Price label
            const priceLabel = document.createElement('div');
            priceLabel.className = 'small text-muted';
            priceLabel.style.fontSize = '0.93em';
            priceLabel.textContent = 'Mean cost per month';
            priceContainer.appendChild(priceLabel);
            // After two years price
            if (offer.after_two_years_eur) {
                const spacer = document.createElement('div');
                spacer.style.height = '0.3em';
                priceContainer.appendChild(spacer);

                const afterTwoYears = document.createElement('div');
                afterTwoYears.className = 'small text-end w-100';
                afterTwoYears.style.fontSize = '0.93em';
                afterTwoYears.textContent = `after 24 month: €${offer.after_two_years_eur.toFixed(2)}`;
                priceContainer.appendChild(afterTwoYears);
            }
            centerRight.appendChild(priceContainer);

            // Assemble card
            row.appendChild(left);
            row.appendChild(centerRight);
            card.appendChild(row);
            col.appendChild(card);
            return col;
        }