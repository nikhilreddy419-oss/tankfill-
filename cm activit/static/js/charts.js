/**
 * TankFill Chart.js Visualizer Module
 * Renders and dynamically updates:
 * 1. Water Level vs. Time curve
 * 2. Bisection Convergence Error vs. Iterations (with theoretical upper bound comparison)
 * Responds automatically to Dark/Light theme shifts.
 */

(function () {
  'use strict';

  let levelChartInstance = null;
  let convergenceChartInstance = null;

  /**
   * Helper to determine theme-dependent colors.
   */
  function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      textColor: isDark ? '#94a3b8' : '#64748b',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      tooltipBg: isDark ? '#1e293b' : '#0f172a',
      primaryLine: isDark ? '#38bdf8' : '#0284c7',
      primaryFill: isDark ? 'rgba(56, 189, 248, 0.18)' : 'rgba(2, 132, 199, 0.12)',
      targetLine: '#10b981',
      theoLine: '#f59e0b',
      tolLine: '#ef4444',
      cardBg: isDark ? '#131c31' : '#ffffff',
    };
  }

  /**
   * Initialize or update Water Level vs Time Chart.
   * @param {HTMLCanvasElement} canvas
   * @param {Object} data - Contains labels, levels, percentages, target_level, capacity, initial_level
   */
  function renderLevelChart(canvas, data) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const colors = getThemeColors();

    if (levelChartInstance) {
      levelChartInstance.destroy();
    }

    // Gradient fill under the water level line
    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, colors.primaryFill);
    gradient.addColorStop(1, 'rgba(0,0,0,0)');

    levelChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Water Volume V(t)',
            data: data.levels,
            borderColor: colors.primaryLine,
            backgroundColor: gradient,
            fill: true,
            tension: 0.25,
            borderWidth: 3,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: colors.primaryLine,
            pointHoverBorderColor: '#ffffff',
            pointHoverBorderWidth: 2,
          },
          {
            label: `Target Level (${data.target_level} L)`,
            data: new Array(data.labels.length).fill(data.target_level),
            borderColor: colors.targetLine,
            borderDash: [6, 4],
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
          },
          {
            label: `Total Capacity (${data.capacity} L)`,
            data: new Array(data.labels.length).fill(data.capacity),
            borderColor: colors.textColor,
            borderDash: [3, 3],
            borderWidth: 1.5,
            fill: false,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: colors.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
              usePointStyle: true,
            },
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: '#ffffff',
            bodyColor: '#e2e8f0',
            borderColor: colors.gridColor,
            borderWidth: 1,
            padding: 12,
            callbacks: {
              title: (items) => `Time: ${items[0].label} mins`,
              label: (context) => {
                const val = context.raw;
                const pct = ((val / data.capacity) * 100).toFixed(1);
                return `${context.dataset.label}: ${val} L (${pct}%)`;
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Elapsed Time t (minutes)',
              color: colors.textColor,
              font: { weight: '600' },
            },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
          },
          y: {
            title: {
              display: true,
              text: 'Water Volume V (Litres)',
              color: colors.textColor,
              font: { weight: '600' },
            },
            min: 0,
            max: Math.ceil(data.capacity * 1.05),
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
          },
        },
      },
    });
  }

  /**
   * Initialize or update Convergence Error vs. Iterations Chart.
   * @param {HTMLCanvasElement} canvas
   * @param {Object} data - Contains labels, errors, theoretical, residuals
   * @param {number} tolerance - epsilon threshold
   */
  function renderConvergenceChart(canvas, data, tolerance = 1e-4) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const colors = getThemeColors();

    if (convergenceChartInstance) {
      convergenceChartInstance.destroy();
    }

    convergenceChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels.map((k) => `Iter ${k}`),
        datasets: [
          {
            label: 'Actual Error |b_k - a_k|/2',
            data: data.errors,
            borderColor: colors.primaryLine,
            backgroundColor: colors.primaryLine,
            borderWidth: 2.5,
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.1,
          },
          {
            label: 'Theoretical Bound (b0-a0)/2^k',
            data: data.theoretical,
            borderColor: colors.theoLine,
            borderDash: [5, 4],
            borderWidth: 2,
            pointRadius: 3,
            fill: false,
          },
          {
            label: `Tolerance ε (${tolerance.toExponential()})`,
            data: new Array(data.labels.length).fill(tolerance),
            borderColor: colors.tolLine,
            borderDash: [3, 3],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: colors.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
              usePointStyle: true,
            },
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: '#ffffff',
            bodyColor: '#e2e8f0',
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toExponential(4)}`,
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Bisection Iteration Step (k)',
              color: colors.textColor,
              font: { weight: '600' },
            },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
          },
          y: {
            type: 'logarithmic',
            title: {
              display: true,
              text: 'Error Bound (Log Scale)',
              color: colors.textColor,
              font: { weight: '600' },
            },
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textColor,
              callback: (val) => Number(val).toExponential(0),
            },
          },
        },
      },
    });
  }

  // Refresh chart color themes on theme change
  window.addEventListener('themeChanged', () => {
    if (levelChartInstance) {
      const colors = getThemeColors();
      levelChartInstance.options.scales.x.grid.color = colors.gridColor;
      levelChartInstance.options.scales.y.grid.color = colors.gridColor;
      levelChartInstance.options.scales.x.ticks.color = colors.textColor;
      levelChartInstance.options.scales.y.ticks.color = colors.textColor;
      levelChartInstance.options.plugins.legend.labels.color = colors.textColor;
      levelChartInstance.update();
    }
    if (convergenceChartInstance) {
      const colors = getThemeColors();
      convergenceChartInstance.options.scales.x.grid.color = colors.gridColor;
      convergenceChartInstance.options.scales.y.grid.color = colors.gridColor;
      convergenceChartInstance.options.scales.x.ticks.color = colors.textColor;
      convergenceChartInstance.options.scales.y.ticks.color = colors.textColor;
      convergenceChartInstance.options.plugins.legend.labels.color = colors.textColor;
      convergenceChartInstance.update();
    }
  });

  // Expose methods
  window.TankFillCharts = {
    renderLevelChart,
    renderConvergenceChart,
  };
})();
