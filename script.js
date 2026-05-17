const markInputs = document.querySelectorAll('#marks-form input[type="number"]');
const totalMarks = document.querySelector('#total-marks');
const queueItems = document.querySelectorAll('#script-queue li');
const searchInput = document.querySelector('#script-search');
const toast = document.querySelector('#toast');
const timer = document.querySelector('#timer');
const form = document.querySelector('#marks-form');

function updateTotal() {
  const total = [...markInputs].reduce((sum, input) => sum + Number(input.value || 0), 0);
  totalMarks.textContent = `${total} / 25`;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2400);
}

markInputs.forEach((input) => input.addEventListener('input', updateTotal));

queueItems.forEach((item) => {
  item.addEventListener('click', () => {
    queueItems.forEach((queueItem) => queueItem.classList.remove('active'));
    item.classList.add('active');
    showToast(`${item.querySelector('strong').textContent} opened in demo viewer`);
  });
});

searchInput.addEventListener('input', (event) => {
  const query = event.target.value.trim().toLowerCase();
  queueItems.forEach((item) => {
    const text = item.textContent.toLowerCase();
    item.hidden = query && !text.includes(query) && !item.dataset.status.includes(query);
  });
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  showToast('Demo evaluation submitted. No real data was sent.');
});

let secondsLeft = 18 * 60;
window.setInterval(() => {
  secondsLeft = Math.max(0, secondsLeft - 1);
  const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const seconds = String(secondsLeft % 60).padStart(2, '0');
  timer.textContent = `${minutes}:${seconds}`;
}, 1000);

updateTotal();
