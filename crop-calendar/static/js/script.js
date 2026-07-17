/* =========================================================================
   Climate-Smart Crop Calendar — Client Scripts
   ========================================================================= */

document.addEventListener('DOMContentLoaded', function () {
  // ---- Mobile sidebar toggle ----
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuToggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ---- Password show/hide toggle ----
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      const icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    });
  });

  // ---- Register form client-side validation ----
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      const mobile = document.getElementById('mobile').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password').value;
      const errors = [];

      if (!/^\d{10}$/.test(mobile)) errors.push('Mobile number must be exactly 10 digits.');
      if (password.length < 6) errors.push('Password must be at least 6 characters.');
      if (password !== confirmPassword) errors.push('Passwords do not match.');

      if (errors.length) {
        e.preventDefault();
        alert(errors.join('\n'));
      }
    });
  }

  // ---- Login form basic validation ----
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      const mobile = document.getElementById('mobile').value.trim();
      if (!/^\d{10}$/.test(mobile)) {
        e.preventDefault();
        alert('Please enter a valid 10-digit mobile number.');
      }
    });
  }
});

/* =========================================================================
   Dashboard Charts (Chart.js)
   ========================================================================= */
function initDashboardCharts(labels, rainfallValues, temperatureValues) {
  const rainfallCtx = document.getElementById('rainfallChart');
  if (rainfallCtx) {
    new Chart(rainfallCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Rainfall (mm)',
          data: rainfallValues,
          backgroundColor: '#66bb6a',
          borderRadius: 6,
          maxBarThickness: 28
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#eef4ef' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  const tempCtx = document.getElementById('temperatureChart');
  if (tempCtx) {
    new Chart(tempCtx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperature (°C)',
          data: temperatureValues,
          borderColor: '#2e7d32',
          backgroundColor: 'rgba(46, 125, 50, 0.12)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#2e7d32',
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: '#eef4ef' } },
          x: { grid: { display: false } }
        }
      }
    });
  }
}

/* =========================================================================
   Crop Calendar Rendering
   ========================================================================= */
let calCurrentDate = new Date();
let calRecData = null;

function initCropCalendar(recData) {
  calRecData = recData;

  if (recData && recData.best_sowing_date) {
    const parsed = new Date(recData.best_sowing_date);
    if (!isNaN(parsed)) calCurrentDate = new Date(parsed.getFullYear(), parsed.getMonth(), 1);
  }

  renderCalendar();

  const prevBtn = document.getElementById('prevMonthBtn');
  const nextBtn = document.getElementById('nextMonthBtn');
  if (prevBtn) prevBtn.addEventListener('click', () => { calCurrentDate.setMonth(calCurrentDate.getMonth() - 1); renderCalendar(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { calCurrentDate.setMonth(calCurrentDate.getMonth() + 1); renderCalendar(); });
}

function parseWindow(sowingWindow) {
  // Expected format: "24 Jun 2026 – 30 Jun 2026"
  if (!sowingWindow) return null;
  const parts = sowingWindow.split('–').map(s => s.trim());
  if (parts.length !== 2) return null;
  const start = new Date(parts[0]);
  const end = new Date(parts[1]);
  if (isNaN(start) || isNaN(end)) return null;
  return { start, end };
}

function dateKey(d) {
  return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
}

function renderCalendar() {
  const monthLabel = document.getElementById('calMonthLabel');
  const daysWrap = document.getElementById('calDays');
  if (!daysWrap) return;

  const year = calCurrentDate.getFullYear();
  const month = calCurrentDate.getMonth();
  const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  if (monthLabel) monthLabel.textContent = 'Crop Calendar - ' + monthNames[month] + ' ' + year;

  const window_ = calRecData ? parseWindow(calRecData.sowing_window) : null;
  const bestDate = calRecData && calRecData.best_sowing_date ? new Date(calRecData.best_sowing_date) : null;

  const firstDay = new Date(year, month, 1);
  // Monday-first offset
  let startOffset = firstDay.getDay() - 1;
  if (startOffset < 0) startOffset = 6;

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();
  const today = new Date();

  let html = '';
  const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;

  for (let i = 0; i < totalCells; i++) {
    const dayNum = i - startOffset + 1;
    let cellDate, otherMonth = false;

    if (dayNum < 1) {
      cellDate = new Date(year, month - 1, daysInPrevMonth + dayNum);
      otherMonth = true;
    } else if (dayNum > daysInMonth) {
      cellDate = new Date(year, month + 1, dayNum - daysInMonth);
      otherMonth = true;
    } else {
      cellDate = new Date(year, month, dayNum);
    }

    let cls = 'cal-day';
    if (otherMonth) cls += ' other-month';

    if (window_ && cellDate >= stripTime(window_.start) && cellDate <= stripTime(window_.end)) {
      if (bestDate && dateKey(cellDate) === dateKey(bestDate)) {
        cls += ' recommended';
      } else {
        const dayOffset = Math.floor((cellDate - window_.start) / 86400000);
        cls += (dayOffset % 3 === 0) ? ' risk' : (dayOffset % 2 === 0 ? ' recommended' : ' acceptable');
      }
    }

    if (dateKey(cellDate) === dateKey(today)) cls += ' today';

    html += `<div class="${cls}">${cellDate.getDate()}</div>`;
  }

  daysWrap.innerHTML = html;
}

function stripTime(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}
