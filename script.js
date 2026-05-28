const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const marksForm = $('#marks-form');
const markInputs = $$('#marks-form input[type="number"]');
const queueItems = $$('#script-queue li');
const searchInput = $('#script-search');
const timer = $('#timer');
const toast = $('#toast');
const totalMarks = $('#total-marks');

const TOAST_DURATION_MS = 2400;
const TIMER_DURATION_SECONDS = 18 * 60;

let toastTimeout;
let secondsLeft = TIMER_DURATION_SECONDS;

function maxMarks() {
  return markInputs.reduce((total, input) => total + Number(input.max || 0), 0);
}

function awardedMarks() {
  return markInputs.reduce((total, input) => total + Number(input.value || 0), 0);
}

function updateTotal() {
  totalMarks.textContent = `${awardedMarks()} / ${maxMarks()}`;
}

function showToast(message) {
  window.clearTimeout(toastTimeout);
  toast.textContent = message;
  toast.classList.add('show');

  toastTimeout = window.setTimeout(() => {
    toast.classList.remove('show');
  }, TOAST_DURATION_MS);
}

function selectScript(item) {
  queueItems.forEach((queueItem) => queueItem.classList.remove('active'));
  item.classList.add('active');

  const rollNumber = item.querySelector('strong').textContent;
  showToast(`${rollNumber} opened in the demo viewer`);
}

function filterScripts() {
  const query = searchInput.value.trim().toLowerCase();

  queueItems.forEach((item) => {
    const label = item.textContent.toLowerCase();
    const status = item.dataset.status.toLowerCase();
    item.hidden = Boolean(query && !label.includes(query) && !status.includes(query));
  });
}

function formatTimer(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function tickTimer() {
  secondsLeft = Math.max(0, secondsLeft - 1);
  timer.textContent = formatTimer(secondsLeft);
}

markInputs.forEach((input) => input.addEventListener('input', updateTotal));
queueItems.forEach((item) => item.addEventListener('click', () => selectScript(item)));
searchInput.addEventListener('input', filterScripts);

marksForm.addEventListener('submit', (event) => {
  event.preventDefault();
  showToast('Demo evaluation submitted. No real data was sent.');
});

updateTotal();
window.setInterval(tickTimer, 1000);
