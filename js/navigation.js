// Navigation JavaScript für alle Seiten
document.addEventListener('DOMContentLoaded', () => {
    // Mobile Navigation (Burger Menu)
    const navbarBurger = document.querySelector('.navbar-burger');
    if (navbarBurger) {
        navbarBurger.addEventListener('click', () => {
            const target = navbarBurger.dataset.target;
            const navbarMenu = document.getElementById(target);
            
            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            navbarBurger.classList.toggle('is-active');
            navbarMenu.classList.toggle('is-active');
        });
    }
});
