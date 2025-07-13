// Show slogan, hide loading and main content
export function showSlogan() {
    document.getElementById('slogan-placeholder').classList.remove('d-none');
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('main-content').classList.add('d-none');
}

// Show loading, hide slogan and main content
export function showLoading() {
    document.getElementById('slogan-placeholder').classList.add('d-none');
    document.getElementById('loading-placeholder').classList.remove('d-none');
    document.getElementById('main-content').classList.add('d-none');
}

// Show main content, hide others
export function showMainContent() {
    document.getElementById('slogan-placeholder').classList.add('d-none');
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('main-content').classList.remove('d-none');
}