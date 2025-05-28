export function getCostPopoverContent(offer) {
    // always display 2 digits after the decimal point
    const formatEur = val =>
        (val !== undefined && val !== null && !isNaN(val))
            ? `€${Number(val).toFixed(2)}`
            : '€0.00';

    // check if offer has any discounts
    const hasPercent = offer.voucher_percent !== undefined && offer.voucher_percent !== null;
    const hasFixed = offer.voucher_fixed_eur !== undefined && offer.voucher_fixed_eur !== null;

    // if no discounts, return just the base cost
    let discountRows = '';
    // if has both percent and fixed (max) discounts, show both
    if (hasPercent && hasFixed) {
        discountRows = `
            <div class="d-flex justify-content-between">
                <span>Voucher (over ${offer.promo_duration_months || '24'} months)</span>
                <span>${offer.voucher_percent}%</span> 
            </div>
            <div class="d-flex justify-content-between">
                <span>Max. discount</span>
                <span>${formatEur(offer.voucher_fixed_eur)}</span>
            </div>
        `;
    // if has only percent or fixed discount, show that
    } else if (hasPercent) {
        discountRows = `
            <div class="d-flex justify-content-between">
                <span>Voucher (over ${offer.promo_duration_months || '24'} months)</span>
                <span>${offer.voucher_percent}%</span> 
            </div>
        `;
    } else if (hasFixed) {
        discountRows = `
            <div class="d-flex justify-content-between">
                <span>One-time discount</span>
                <span>${formatEur(offer.voucher_fixed_eur)}</span>
            </div>
        `;
    }

    // display the cost breakdown: base cost, discounts, and total cost
    return `
        <div style="max-width: 270px;">
            <div class="fw-semibold mb-2">How this cost is calculated</div>
            <div class="d-flex justify-content-between">
                <span>Base cost</span>
                <span>${formatEur(offer.cost_eur)}</span>
            </div>
            ${discountRows}
            <hr class="my-2">
            <div class="d-flex justify-content-between fw-semibold">
                <span>Total cost</span>
                <span>${formatEur(offer.cost_first_years_eur)}</span>
            </div>
        </div>
    `;
}