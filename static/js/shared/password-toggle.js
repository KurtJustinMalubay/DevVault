document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.password-toggle').forEach(function (toggle) {
    var input = document.getElementById(toggle.getAttribute('aria-controls'));
    var label = toggle.querySelector('.password-toggle__label');
    if (!input || !label) return;

    function syncToggleVisibility() {
      if (!input.value) {
        input.type = 'password';
        toggle.setAttribute('aria-label', 'Show password');
        toggle.setAttribute('aria-pressed', 'false');
        label.textContent = 'Show';
        toggle.hidden = true;
        return;
      }

      toggle.hidden = false;
    }

    input.addEventListener('input', syncToggleVisibility);
    input.addEventListener('change', syncToggleVisibility);
    syncToggleVisibility();

    toggle.addEventListener('click', function () {
      var isVisible = input.type === 'password';
      input.type = isVisible ? 'text' : 'password';
      label.textContent = isVisible ? 'Hide' : 'Show';
      toggle.setAttribute('aria-label', isVisible ? 'Hide password' : 'Show password');
      toggle.setAttribute('aria-pressed', isVisible ? 'true' : 'false');
    });
  });
});
