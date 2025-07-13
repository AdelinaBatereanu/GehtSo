// --- Update summary text based on current offers ---
export function updateSummary(data) {
    const providers = new Set(data.map(o => o.provider));
    const summary = `Found ${data.length} offer${data.length !== 1 ? 's' : ''} from ${providers.size} provider${providers.size !== 1 ? 's' : ''}`;
    document.getElementById('offers-summary').textContent = summary;
}