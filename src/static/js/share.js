export function setupShare({
    getOffers,
    getFilters
} = {}) {
    document.querySelectorAll('.share-link-btn').forEach(shareBtn => {
        shareBtn.addEventListener('click', async () => {
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
                    await navigator.clipboard.writeText(data.share_url);
                    const textSpan = shareBtn.querySelector('.share-link-text');
                    if (textSpan) {
                        textSpan.textContent = "Copied!";
                        setTimeout(() => {
                            textSpan.textContent = "Copy share link";
                        }, 1200);
                    }
                } else {
                    alert('Error creating share link: ' + data.error);
                }
            } catch (err) {
                alert('Network error: ' + err);
            }
        });
    });
}

// // // --- Share button functionality ---
// document.getElementById('share-btn').addEventListener('click', async () => {

//     const offers = allOffers;

//     const filters = {
//         speed: selectedSpeed,
//         limit: selectedLimit,
//         duration: selectedMaxDuration,
//         tv: selectedTv,
//         connection_types: getSelectedConnectionTypes(),
//         providers: getSelectedProviders(),
//         installation: installCheckbox.checked,
//         age: ageInput.value.trim(),
//         showAllAges: showAllAgesCheckbox.checked,
//         sort: selectedSort,
//     };
// // Ensure filters are properly formatted for JSON
//     try {
//         const resp = await fetch('/share', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ offers, filters })
//         });
//         const data = await resp.json();
  
//         if (resp.ok) {
//           await navigator.clipboard.writeText(data.share_url);
//           alert('Share link copied to clipboard!:\n' + data.share_url);
//         } else {
//           alert('Error creating share link: ' + data.error);
//         }
//       } catch (err) {
//         alert('Network error: ' + err);
//       }
//   });