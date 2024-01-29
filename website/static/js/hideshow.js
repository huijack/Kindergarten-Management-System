function setupTabs() {
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
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
});
