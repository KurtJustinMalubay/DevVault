document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('menu-toggle');
  var navigation = document.getElementById('app-navigation');
  if (!toggle || !navigation) return;

  function closeMenu() {
    navigation.classList.remove('is-open');
    navigation.setAttribute('aria-hidden', 'true');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }

  function syncBreakpoint(event) {
    if (event.matches && navigation.classList.contains('is-open')) closeMenu();
  }

  toggle.addEventListener('click', function () {
    var isOpen = navigation.classList.toggle('is-open');
    navigation.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    toggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  });

  navigation.addEventListener('click', function (event) {
    if (event.target.closest('a')) closeMenu();
  });

  document.addEventListener('click', function (event) {
    if (!navigation.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && navigation.classList.contains('is-open')) {
      closeMenu();
      toggle.focus();
    }
  });

  var desktopNavigation = window.matchMedia('(min-width: 1100px)');
  if (desktopNavigation.addEventListener) {
    desktopNavigation.addEventListener('change', syncBreakpoint);
  } else if (desktopNavigation.addListener) {
    desktopNavigation.addListener(syncBreakpoint);
  }
});
