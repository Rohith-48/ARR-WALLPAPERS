const toggleButton = document.querySelector('.dark-light');
const colors = document.querySelectorAll('.color');
const body = document.body;

// Function to set the mode and update the UI
function setMode(mode) {
  body.classList.remove('dark-mode', 'light-mode');
  body.classList.add(mode);
  localStorage.setItem('selectedMode', mode);
  updateSelectedColor(mode);
}

// Function to update the selected color indicator
function updateSelectedColor(mode) {
  colors.forEach(color => {
    const dataColor = color.getAttribute('data-color');
    if (dataColor === mode) {
      color.classList.add('selected');
    } else {
      color.classList.remove('selected');
    }
  });
}

// Event listener for color selection
colors.forEach(color => {
  color.addEventListener('click', e => {
    colors.forEach(c => c.classList.remove('selected'));
    const theme = color.getAttribute('data-color');
    setMode(theme);
  });
});

// Event listener for mode toggle
toggleButton.addEventListener('click', () => {
  const currentMode = body.classList.contains('dark-mode') ? 'dark-mode' : 'light-mode';
  const newMode = currentMode === 'dark-mode' ? 'light-mode' : 'dark-mode';
  setMode(newMode);
});

// Check if mode is stored in local storage and apply it
const storedMode = localStorage.getItem('selectedMode');
if (storedMode) {
  setMode(storedMode);
} else {
  // Default mode if not stored
  setMode('light-mode');
}
