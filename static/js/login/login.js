document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('toggle-password');
  var form = document.getElementById('login-form');
  if (!toggle || !form) return;

  var input = document.getElementById(toggle.getAttribute('aria-controls'));
  if (!input) return;

  function syncToggleVisibility() {
    toggle.hidden = input.value.length === 0;
  }

  input.addEventListener('input', syncToggleVisibility);
  syncToggleVisibility();

  toggle.addEventListener('click', function () {
    var isVisible = input.type === 'password';
    input.type = isVisible ? 'text' : 'password';
    toggle.querySelector('.password-toggle__label').textContent = isVisible ? 'Hide' : 'Show';
    toggle.setAttribute('aria-label', isVisible ? 'Hide password' : 'Show password');
    toggle.setAttribute('aria-pressed', isVisible ? 'true' : 'false');
  });
});
