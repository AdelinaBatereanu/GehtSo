// --- Share functionality ---
let lastShareUrl = null;

export function setupShare({ getOffers, getFilters } = {}) {
    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            // Only generate the share URL if we haven't already
            if (!lastShareUrl) {
                const offers = typeof getOffers === 'function' ? getOffers() : [];
                const filters = typeof getFilters === 'function' ? getFilters() : {};
                try {
                    const resp = await fetch('/share', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ offers, filters })
                    });
                    const data = await resp.json();
                    if (resp.ok) {
                        lastShareUrl = data.share_url;
                    } else {
                        alert('Error creating share link: ' + data.error);
                        return;
                    }
                } catch (err) {
                    alert('Network error: ' + err);
                    return;
                }
            }

            // Now handle the platform-specific sharing
            const platform = btn.getAttribute('data-platform');
            const url = encodeURIComponent(lastShareUrl);
            const messageText = "Look what I found! Check out these internet offers!";
            const message = encodeURIComponent(`${messageText} ${lastShareUrl}`);
            let shareWindowUrl = '';
            if (platform === 'whatsapp') {
                shareWindowUrl = `https://wa.me/?text=${message}`;
            } else if (platform === 'telegram') {
                shareWindowUrl = `https://t.me/share/url?url=${encodeURIComponent(lastShareUrl)}&text=${messageText}`;
            } else if (platform === 'email') {
                shareWindowUrl = `mailto:?subject=Internet%20offers%20comparison&body=${message}`;
            } else if (platform === 'copy') {
                await navigator.clipboard.writeText(lastShareUrl);
                const originalText = btn.textContent;
                btn.textContent = "Copied!";
                btn.classList.add('copied-feedback');
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.classList.remove('copied-feedback');
                }, 1200);
                return;
            }
            if (shareWindowUrl) {
                window.open(shareWindowUrl, '_blank', 'noopener,noreferrer');
            }
        });
    });
}

export function resetShareUrl() {
    lastShareUrl = null;
}