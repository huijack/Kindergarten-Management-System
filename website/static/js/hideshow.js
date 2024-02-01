function setupTabs() {
    const currentTab = localStorage.getItem('activeTab') || '1'; // Retrieve the active tab from localStorage, default to '1'

    document.querySelectorAll('.menu-link').forEach(button => {
        button.addEventListener('click', () => {
            const tabNumber = button.dataset.forTab;

            document.querySelectorAll('.content-container').forEach(container => {
                container.classList.remove('content-container--active');
            });

            const activeContentContainer = document.querySelector(`.content-container[data-tab="${tabNumber}"]`);
            if (activeContentContainer) {
                activeContentContainer.classList.add('content-container--active');
            }

            document.querySelectorAll('.menu-link').forEach(link => {
                link.classList.remove('menu-link--active');
            });

            button.classList.add('menu-link--active');

            // Update the hidden input field with the current tab
            document.getElementById('currentTab').value = tabNumber;

            // Store the active tab in localStorage
            localStorage.setItem('activeTab', tabNumber);
        });
    });

    // Set the initial active tab based on the value from localStorage
    const initialActiveTab = document.querySelector(`.menu-link[data-for-tab="${currentTab}"]`);
    if (initialActiveTab) {
        initialActiveTab.click();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
});
