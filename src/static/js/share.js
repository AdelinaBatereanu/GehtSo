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
            let shareWindowUrl = '';
            if (platform === 'whatsapp') {
                shareWindowUrl = `https://wa.me/?text=${url}`;
            } else if (platform === 'telegram') {
                shareWindowUrl = `https://t.me/share/url?url=${url}`;
            } else if (platform === 'messenger') {
                shareWindowUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
            } else if (platform === 'email') {
                shareWindowUrl = `mailto:?subject=Check%20out%20these%20internet%20offers&body=${url}`;
            } else if (platform === 'copy') {
                await navigator.clipboard.writeText(lastShareUrl);
                btn.querySelector('img').alt = "Copied!";
                btn.classList.add('text-success');
                setTimeout(() => {
                    btn.querySelector('img').alt = "Copy link";
                    btn.classList.remove('text-success');
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