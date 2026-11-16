document.addEventListener('DOMContentLoaded', function () {
  var darkModeInput = document.getElementById('id_dark_mode');
  if (!darkModeInput) return;

  darkModeInput.addEventListener('change', function () {
    document.body.classList.toggle('theme-light', !darkModeInput.checked);
  });

  var reducedMotionInput = document.getElementById('id_reduced_motion');
  if (reducedMotionInput) {
    reducedMotionInput.addEventListener('change', function () {
      document.body.classList.toggle('reduced-motion', reducedMotionInput.checked);
      document.documentElement.classList.toggle('reduced-motion', reducedMotionInput.checked);
    });
  }
});
