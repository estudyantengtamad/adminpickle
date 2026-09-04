// Executive Dashboard - Matchmaking Health & Latency Chart Initializer
document.addEventListener('DOMContentLoaded', () => {
  const chartCanvas = document.getElementById('matchmakingHealthChart');
  if (!chartCanvas) return;

  const ctx = chartCanvas.getContext('2d');

  // Create subtle gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(79, 70, 229, 0.25)');
  gradient.addColorStop(1, 'rgba(79, 70, 229, 0.0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
      datasets: [
        {
          label: 'Queue Latency (ms)',
          data: [18, 15, 28, 42, 35, 22],
          borderColor: '#4F46E5',
          borderWidth: 2.5,
          backgroundColor: gradient,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#FFFFFF',
          pointBorderColor: '#4F46E5',
          pointBorderWidth: 2,
          pointHoverRadius: 6,
        },
        {
          label: 'Target Peak (ms)',
          data: [35, 35, 35, 35, 35, 35],
          borderColor: '#94A3B8',
          borderWidth: 1.5,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12 }
          }
        },
        tooltip: {
          backgroundColor: '#0F172A',
          titleFont: { family: 'Inter', size: 13, weight: 'bold' },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 12,
          cornerRadius: 8,
          displayColors: false
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#64748B' }
        },
        y: {
          grid: { color: '#F1F5F9' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#64748B', callback: (val) => val + ' ms' }
        }
      }
    }
  });
});
