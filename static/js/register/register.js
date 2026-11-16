document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('register-form');
  if (!form) return;

  var pw1 = form.querySelector('#id_password1');
  var pw2 = form.querySelector('#id_password2');
  var hint = document.getElementById('password-match-hint');
  if (!pw1 || !pw2 || !hint) return;

  function checkMatch() {
    if (!pw2.value) {
      hint.textContent = '';
      hint.className = 'text-xs';
      return;
    }
    if (pw1.value === pw2.value) {
      hint.textContent = 'Passwords match.';
      hint.className = 'text-xs ok';
    } else {
      hint.textContent = 'Passwords do not match yet.';
      hint.className = 'text-xs mismatch';
    }
  }

  pw1.addEventListener('input', checkMatch);
  pw2.addEventListener('input', checkMatch);
});
