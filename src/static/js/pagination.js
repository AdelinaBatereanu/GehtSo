import { applyFiltersAndUpdateResults, state } from './main.js';

// --- Render pagination ---
export function renderPagination(totalOffers, pageSize) {
    const totalPages = Math.ceil(totalOffers / pageSize);
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = 'page-item' + (i === state.currentPage ? ' active' : '');
        const btn = document.createElement('button');
        btn.className = 'page-link';
        btn.textContent = i;
        btn.addEventListener('click', () => {
            state.currentPage = i;
            applyFiltersAndUpdateResults();
            document.getElementById('main-content').scrollIntoView({ behavior: 'smooth' });
        });
        li.appendChild(btn);
        pagination.appendChild(li);
    }
}