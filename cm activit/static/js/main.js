/**
 * TankFill Main Global Script
 * Manages mobile responsive navbar, accordion toggles,
 * and overall interactive enhancements.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobileNavToggle');
    const navLinks = document.getElementById('navLinks');

    if (mobileToggle && navLinks) {
      mobileToggle.addEventListener('click', () => {
        navLinks.classList.toggle('show');
        const isExpanded = navLinks.classList.contains('show');
        mobileToggle.setAttribute('aria-expanded', isExpanded);
      });

      // Close mobile menu if clicked outside
      document.addEventListener('click', (e) => {
        if (!mobileToggle.contains(e.target) && !navLinks.contains(e.target)) {
          navLinks.classList.remove('show');
        }
      });
    }

    // 2. Advanced Parameters Accordion Toggle
    const accordionHeader = document.querySelector('.accordion-header');
    const accordionBody = document.querySelector('.accordion-body');
    const accordionIcon = document.getElementById('accordionChevron');

    if (accordionHeader && accordionBody) {
      accordionHeader.addEventListener('click', () => {
        const isOpen = accordionBody.classList.toggle('open');
        if (accordionIcon) {
          accordionIcon.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
          accordionIcon.style.transition = 'transform 0.25s ease';
        }
      });
    }
  });
})();
