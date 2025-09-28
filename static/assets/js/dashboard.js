// Initialize Lucide icons
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();

    // Add click handlers for dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');

    dashboardCards.forEach((card, index) => {
        card.addEventListener('click', function() {
            const title = card.querySelector('.card-title').textContent;
            console.log(`Navigating to ${title}`);

            // Add a visual feedback effect
            card.style.transform = 'scale(0.98)';
            setTimeout(() => {
                card.style.transform = '';
            }, 150);

            // You can add actual navigation logic here
            // For example: window.location.href = `/modules/${title.toLowerCase().replace(/\s+/g, '-')}`;
        });

        // Add hover effect enhancement
        card.addEventListener('mouseenter', function() {
            card.style.borderColor = 'hsl(210, 100%, 45%)';
        });

        card.addEventListener('mouseleave', function() {
            card.style.borderColor = '';
        });
    });

    // Add search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();

            dashboardCards.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-description').textContent.toLowerCase();

                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = searchTerm ? 'none' : 'block';
                }
            });
        });
    }

    // Add notification click handler
    const notificationBtn = document.querySelector('.header-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            alert('Notifications feature coming soon!');
        });
    }

    // Add activity card interactions
    const activityCards = document.querySelectorAll('.activity-card');
    activityCards.forEach(card => {
        card.addEventListener('click', function() {
            const label = card.querySelector('.activity-label').textContent;
            console.log(`Clicked on activity: ${label}`);

            // Add visual feedback
            card.style.background = 'hsl(210, 25%, 95%)';
            setTimeout(() => {
                card.style.background = '';
            }, 200);
        });
    });

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }

        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.search-input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.blur();
                searchInput.value = '';

                // Reset card visibility
                dashboardCards.forEach(card => {
                    card.style.display = 'block';
                });
            }
        }
    });
});