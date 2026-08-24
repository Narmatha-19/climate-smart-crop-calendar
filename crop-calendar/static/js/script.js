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
   Monsoon Insights Charts (Chart.js) — real 2005-2025 yearly series with a
   linear-regression trend line overlay, one chart for rainfall and one for
   temperature. Re-created (not just updated) on each district switch since
   the underlying label/data arrays change length.
   ========================================================================= */
let monsoonRainfallChart = null;
let monsoonTempChart = null;

function renderMonsoonCharts(data) {
  const rainfallCtx = document.getElementById('rainfallTrendChart');
  if (rainfallCtx) {
    if (monsoonRainfallChart) monsoonRainfallChart.destroy();
    monsoonRainfallChart = new Chart(rainfallCtx, {
      type: 'line',
      data: {
        labels: data.years,
        datasets: [
          {
            label: 'Observed',
            data: data.rainfall,
            borderColor: '#2e7d32',
            backgroundColor: 'rgba(46, 125, 50, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
          },
          {
            label: 'Trend line',
            data: data.rainfall_trendline,
            borderColor: '#d97706',
            borderDash: [6, 4],
            pointRadius: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } },
        scales: {
          y: { grid: { color: '#eef4ef' }, title: { display: true, text: 'mm/year', font: { size: 11 } } },
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        },
      },
    });
  }

  const tempCtx = document.getElementById('temperatureTrendChart');
  if (tempCtx) {
    if (monsoonTempChart) monsoonTempChart.destroy();
    monsoonTempChart = new Chart(tempCtx, {
      type: 'line',
      data: {
        labels: data.years,
        datasets: [
          {
            label: 'Observed',
            data: data.temperature,
            borderColor: '#e05a2b',
            backgroundColor: 'rgba(224, 90, 43, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
          },
          {
            label: 'Trend line',
            data: data.temperature_trendline,
            borderColor: '#2563eb',
            borderDash: [6, 4],
            pointRadius: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } },
        scales: {
          y: { grid: { color: '#eef4ef' }, title: { display: true, text: '°C', font: { size: 11 } } },
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        },
      },
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

    let isBestDay = false;
    let statusIcon = '';

    if (window_ && cellDate >= stripTime(window_.start) && cellDate <= stripTime(window_.end)) {
      if (bestDate && dateKey(cellDate) === dateKey(bestDate)) {
        cls += ' recommended best-day';
        isBestDay = true;
      } else {
        const dayOffset = Math.floor((cellDate - window_.start) / 86400000);
        cls += (dayOffset % 3 === 0) ? ' risk' : (dayOffset % 2 === 0 ? ' recommended' : ' acceptable');
      }
    }

    if (isBestDay) {
      statusIcon = '<i class="fa-solid fa-star cal-icon" title="Best sowing date"></i>';
    } else if (cls.includes('recommended')) {
      statusIcon = '<i class="fa-solid fa-seedling cal-icon" title="Recommended day"></i>';
    } else if (cls.includes('acceptable')) {
      statusIcon = '<i class="fa-solid fa-circle-check cal-icon" title="Acceptable day"></i>';
    } else if (cls.includes('risk')) {
      statusIcon = '<i class="fa-solid fa-triangle-exclamation cal-icon" title="High risk day"></i>';
    }

    if (dateKey(cellDate) === dateKey(today)) cls += ' today';

    html += `<div class="${cls}"><span class="cal-daynum">${cellDate.getDate()}</span>${statusIcon}</div>`;
  }

  daysWrap.innerHTML = html;
}

function stripTime(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

/* =========================================================================
   Crop Info Modal — dashboard crop chips open this without leaving the page.
   Modal shell lives in base.html; this wires up any [data-crop] trigger on
   the page against the given district.
   ========================================================================= */
function initCropInfoTriggers(district) {
  const overlay = document.getElementById('cropInfoOverlay');
  const closeBtn = document.getElementById('cropInfoClose');
  const body = document.getElementById('cropInfoBody');
  if (!overlay || !body) return;
  const i18n = window.cropInfoI18n || {};

  function openModal() {
    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    overlay.hidden = true;
    document.body.style.overflow = '';
  }
  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) closeModal(); });

  function renderCropInfo(data) {
    const seasonsHtml = data.seasons_display.map(function (s) {
      return '<div class="crop-modal-season-row">' +
        '<span class="season-name"><i class="fa-solid fa-seedling"></i> ' + s.label + '</span>' +
        (s.sowing_window ? '<span class="season-window">' + s.sowing_window + '</span>' : '') +
        '</div>';
    }).join('');

    const yieldBadgeClass = { Low: 'badge-low', Medium: 'badge-moderate', High: 'badge-high' }[data.yield_category] || 'badge-moderate';
    const yieldLabel = (i18n.yieldLabels && i18n.yieldLabels[data.yield_category]) || data.yield_category;

    body.innerHTML =
      '<div class="crop-modal-title" id="cropInfoTitle">' + data.crop_label + '</div>' +
      '<div class="crop-modal-sub">' + data.district_label + '</div>' +
      '<div class="crop-modal-section">' +
        '<div class="crop-modal-label">' + i18n.bestSeasons + '</div>' +
        '<div class="crop-modal-seasons">' + seasonsHtml + '</div>' +
      '</div>' +
      '<div class="crop-modal-section">' +
        '<div class="crop-modal-label">' + i18n.avgYield + '</div>' +
        '<div class="crop-modal-yield-row">' +
          '<span class="crop-modal-yield-num">' + data.avg_yield + ' ' + i18n.tonnesPerHectare + '</span>' +
          '<span class="badge ' + yieldBadgeClass + '">' + yieldLabel + ' ' + i18n.yieldLevel + '</span>' +
        '</div>' +
      '</div>' +
      '<div class="crop-modal-section">' +
        '<div class="crop-modal-label">' + i18n.typicalClimate + '</div>' +
        '<div class="crop-modal-stats">' +
          '<div class="crop-modal-stat"><div class="stat-num">' + data.avg_rainfall + ' mm</div><div class="stat-cap">' + i18n.rainfall + '</div></div>' +
          '<div class="crop-modal-stat"><div class="stat-num">' + data.avg_temperature + '°C</div><div class="stat-cap">' + i18n.temperature + '</div></div>' +
          '<div class="crop-modal-stat"><div class="stat-num">' + data.avg_humidity + '%</div><div class="stat-cap">' + i18n.humidity + '</div></div>' +
          '<div class="crop-modal-stat"><div class="stat-num">' + Math.round(data.total_area).toLocaleString() + '</div><div class="stat-cap">' + i18n.hectares + '</div></div>' +
        '</div>' +
      '</div>' +
      '<div class="crop-modal-note"><i class="fa-solid fa-circle-info"></i> ' + i18n.yearsLabel + ': ' + data.years_recorded + '</div>' +
      '<a class="btn btn-primary btn-block" style="margin-top:16px;" href="/recommendation?crop=' + encodeURIComponent(data.crop) + '">' +
        i18n.getRec +
      '</a>';
  }

  document.querySelectorAll('[data-crop]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const crop = btn.getAttribute('data-crop');
      body.innerHTML = '<div class="modal-loading">' + i18n.loading + '</div>';
      openModal();

      fetch('/api/crop-info/' + encodeURIComponent(district) + '/' + encodeURIComponent(crop))
        .then(function (res) {
          if (res.status === 404) return { notFound: true };
          if (!res.ok) throw new Error('crop info request failed');
          return res.json();
        })
        .then(function (data) {
          if (data.notFound) {
            body.innerHTML = '<div class="modal-error">' + i18n.noData + '</div>';
          } else {
            renderCropInfo(data);
          }
        })
        .catch(function () {
          body.innerHTML = '<div class="modal-error">' + i18n.error + '</div>';
        });
    });
  });
}
