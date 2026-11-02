/**
 * TankFill Calculator Module
 * Handles form validation, AJAX calculation requests, dynamic UI updates,
 * Water Tank 2D fluid animation, iteration table filtering, presets, and PDF download.
 */

(function () {
  'use strict';

  // DOM Elements
  const form = document.getElementById('tankCalculatorForm');
  const resetBtn = document.getElementById('resetFormBtn');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const resultsContainer = document.getElementById('resultsContainer');
  const tableSearchInput = document.getElementById('tableSearchInput');
  const presetChips = document.querySelectorAll('.preset-chip');
  const copyTimeBtn = document.getElementById('copyTimeBtn');
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');

  // Tank Visualizer Elements
  const tankWater = document.getElementById('tankWater');
  const tankTargetLine = document.getElementById('tankTargetLine');
  const tankTargetBadge = document.getElementById('tankTargetBadge');
  const tankPctReadout = document.getElementById('tankPctReadout');
  const tankLitresReadout = document.getElementById('tankLitresReadout');

  // Input fields
  const capacityInput = document.getElementById('capacity');
  const currentLevelInput = document.getElementById('current_level');
  const targetLevelInput = document.getElementById('target_level');
  const inflowRateInput = document.getElementById('inflow_rate');
  const drainRateInput = document.getElementById('drain_rate');
  const toleranceInput = document.getElementById('tolerance');
  const maxIterationsInput = document.getElementById('max_iterations');
  const flowModelSelect = document.getElementById('flow_model');

  /**
   * Display a floating toast notification.
   */
  function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /**
   * Client-side validation before sending request.
   */
  function validateClientSide() {
    let isValid = true;
    clearFieldErrors();

    const cap = parseFloat(capacityInput.value);
    const curr = parseFloat(currentLevelInput.value);
    const target = parseFloat(targetLevelInput.value);
    const inflow = parseFloat(inflowRateInput.value);
    const drain = parseFloat(drainRateInput.value || 0);

    if (isNaN(cap) || cap <= 0) {
      setFieldError('capacity', 'Capacity must be greater than 0 Litres.');
      isValid = false;
    }

    if (isNaN(curr) || curr < 0) {
      setFieldError('current_level', 'Current level cannot be negative.');
      isValid = false;
    }

    if (isNaN(target) || target <= 0) {
      setFieldError('target_level', 'Target level must be strictly positive.');
      isValid = false;
    }

    if (!isNaN(cap) && !isNaN(curr) && curr > cap) {
      setFieldError('current_level', `Current level cannot exceed tank capacity (${cap} L).`);
      isValid = false;
    }

    if (!isNaN(cap) && !isNaN(target) && target > cap) {
      setFieldError('target_level', `Target level cannot exceed tank capacity (${cap} L).`);
      isValid = false;
    }

    if (!isNaN(curr) && !isNaN(target)) {
      if (target < curr) {
        setFieldError('target_level', 'Target level must be greater than current water level.');
        isValid = false;
      } else if (target === curr) {
        setFieldError('target_level', 'Target is already reached (filling time is 0 mins).');
        isValid = false;
      }
    }

    if (isNaN(inflow) || inflow <= 0) {
      setFieldError('inflow_rate', 'Inflow rate must be greater than 0 L/min.');
      isValid = false;
    }

    if (!isNaN(inflow) && !isNaN(drain) && inflow <= drain) {
      setFieldError('drain_rate', 'Drain rate cannot equal or exceed inflow rate.');
      isValid = false;
    }

    return isValid;
  }

  function setFieldError(fieldId, message) {
    const el = document.getElementById(fieldId);
    if (el) {
      el.classList.add('is-invalid');
      el.classList.remove('is-valid');
      const parent = el.closest('.form-group');
      if (parent) {
        let feedback = parent.querySelector('.invalid-feedback');
        if (!feedback) {
          feedback = document.createElement('div');
          feedback.className = 'invalid-feedback';
          parent.appendChild(feedback);
        }
        feedback.textContent = message;
      }
    }
  }

  function clearFieldErrors() {
    document.querySelectorAll('.form-input').forEach((input) => {
      input.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach((el) => {
      el.textContent = '';
    });
  }

  /**
   * Update 2D Tank Simulation Visualizer.
   */
  function updateTankVisualizer(params, rootTime) {
    if (!tankWater) return;

    const cap = params.capacity;
    const target = params.target_level;
    const current = params.current_level;

    const targetPct = Math.min(100, Math.max(0, (target / cap) * 100));
    const currentPct = Math.min(100, Math.max(0, (current / cap) * 100));

    // Animate target line
    if (tankTargetLine) {
      tankTargetLine.style.bottom = `${targetPct}%`;
    }
    if (tankTargetBadge) {
      tankTargetBadge.textContent = `Target: ${target} L (${targetPct.toFixed(0)}%)`;
    }

    // Animate water filling to target level
    tankWater.style.height = `${targetPct}%`;

    // Update readout
    if (tankPctReadout) {
      tankPctReadout.textContent = `${targetPct.toFixed(1)}%`;
    }
    if (tankLitresReadout) {
      tankLitresReadout.textContent = `${target.toLocaleString()} / ${cap.toLocaleString()} L`;
    }
  }

  /**
   * Populate UI with calculation result.
   */
  function renderResults(result) {
    // 1. Update KPI values
    const kpiTime = document.getElementById('kpiRootTime');
    const kpiDuration = document.getElementById('kpiDuration');
    const kpiIters = document.getElementById('kpiIters');
    const kpiTheoIters = document.getElementById('kpiTheoIters');
    const kpiError = document.getElementById('kpiError');
    const kpiTolerance = document.getElementById('kpiTolerance');
    const kpiExecTime = document.getElementById('kpiExecTime');
    const statusMsg = document.getElementById('calcStatusMessage');

    if (kpiTime) kpiTime.textContent = `${result.root_time.toFixed(4)} min`;
    if (kpiDuration) kpiDuration.textContent = result.duration.human_readable;
    if (kpiIters) kpiIters.textContent = result.total_iterations;
    if (kpiTheoIters) kpiTheoIters.textContent = `Theory: ${result.theoretical_iterations} steps`;
    if (kpiError) kpiError.textContent = result.final_error.toExponential(4);
    if (kpiTolerance) kpiTolerance.textContent = `Target: < ${result.tolerance.toExponential()}`;
    if (kpiExecTime) kpiExecTime.textContent = `${result.execution_time_ms} ms`;
    if (statusMsg) statusMsg.textContent = result.status_message;

    // 2. Update Tank Visualizer
    updateTankVisualizer(result.tank_parameters, result.root_time);

    // 3. Update Equation Cards
    const eqSub = document.getElementById('equationSubstituted');
    if (eqSub) {
      eqSub.innerHTML = `\\[ ${result.equations.substituted_latex} \\]`;
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([eqSub]).catch((err) => console.log(err));
      }
    }

    // 4. Update Charts
    const levelCanvas = document.getElementById('waterLevelChart');
    const convCanvas = document.getElementById('convergenceChart');

    if (window.TankFillCharts) {
      if (levelCanvas && result.charts && result.charts.level_vs_time) {
        window.TankFillCharts.renderLevelChart(levelCanvas, result.charts.level_vs_time);
      }
      if (convCanvas && result.charts && result.charts.convergence) {
        window.TankFillCharts.renderConvergenceChart(
          convCanvas,
          result.charts.convergence,
          result.tolerance
        );
      }
    }

    // 5. Populate Iteration Table
    populateIterationTable(result.iterations);

    // Make results visible
    if (resultsContainer) {
      resultsContainer.style.display = 'block';
      resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  /**
   * Build HTML for Iteration Table rows.
   */
  function populateIterationTable(iterations) {
    const tbody = document.getElementById('iterationTableBody');
    const countBadge = document.getElementById('tableRowCountBadge');
    if (!tbody || !iterations) return;

    if (countBadge) {
      countBadge.textContent = `${iterations.length} Iterations`;
    }

    tbody.innerHTML = '';

    iterations.forEach((row, index) => {
      const isLast = index === iterations.length - 1;
      const tr = document.createElement('tr');
      if (isLast) tr.className = 'row-converged';

      const signClass = row.fa * row.fc < 0 ? 'badge-neg' : 'badge-pos';

      tr.innerHTML = `
        <td><strong>#${row.iteration}</strong></td>
        <td>${row.a.toFixed(6)}</td>
        <td>${row.b.toFixed(6)}</td>
        <td><strong class="text-primary">${row.c.toFixed(6)}</strong></td>
        <td>${row.fa.toFixed(5)}</td>
        <td>${row.fb.toFixed(5)}</td>
        <td>${row.fc.toFixed(5)}</td>
        <td><code>${row.error.toExponential(4)}</code></td>
        <td><span class="badge ${signClass}">${row.sign_test}</span></td>
        <td><small>${row.action}</small></td>
      `;
      tbody.appendChild(tr);
    });
  }

  /**
   * Handle AJAX Form Submission.
   */
  async function handleCalculationSubmit(e) {
    e.preventDefault();

    if (!validateClientSide()) {
      showToast('Please correct input errors highlighted below.', 'error');
      return;
    }

    // Show hydro loader
    if (loadingOverlay) loadingOverlay.classList.add('active');

    const formData = new FormData(form);
    const dataObj = Object.fromEntries(formData.entries());

    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(dataObj),
      });

      const data = await response.json();

      if (loadingOverlay) loadingOverlay.classList.remove('active');

      if (response.ok && data.success) {
        renderResults(data.result);
        showToast('Bisection calculation completed successfully!', 'success');
      } else {
        if (data.errors) {
          for (const [field, msg] of Object.entries(data.errors)) {
            setFieldError(field, msg);
          }
        }
        showToast(data.message || 'Calculation failed. Please verify inputs.', 'error');
      }
    } catch (err) {
      if (loadingOverlay) loadingOverlay.classList.remove('active');
      console.error('API Error:', err);
      showToast('Server communication error. Falling back to standard form submission...', 'error');
      form.submit(); // fallback to standard server POST
    }
  }

  /**
   * Preset Click Handler.
   */
  function handlePresetClick(e) {
    const chip = e.currentTarget;
    presetChips.forEach((c) => c.classList.remove('active'));
    chip.classList.add('active');

    const cap = chip.dataset.capacity;
    const curr = chip.dataset.current;
    const target = chip.dataset.target;
    const inflow = chip.dataset.inflow;
    const drain = chip.dataset.drain || '0';
    const tol = chip.dataset.tolerance || '1e-4';
    const iters = chip.dataset.iterations || '100';
    const model = chip.dataset.model || 'linear';

    if (capacityInput) capacityInput.value = cap;
    if (currentLevelInput) currentLevelInput.value = curr;
    if (targetLevelInput) targetLevelInput.value = target;
    if (inflowRateInput) inflowRateInput.value = inflow;
    if (drainRateInput) drainRateInput.value = drain;
    if (toleranceInput) toleranceInput.value = tol;
    if (maxIterationsInput) maxIterationsInput.value = iters;
    if (flowModelSelect) flowModelSelect.value = model;

    clearFieldErrors();
    showToast(`Loaded "${chip.textContent.trim()}" preset.`, 'info');

    // Trigger calculation automatically
    if (form) {
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  }

  /**
   * Filter table rows based on search input.
   */
  function filterTableRows() {
    const filter = (tableSearchInput.value || '').toLowerCase();
    const rows = document.querySelectorAll('#iterationTableBody tr');
    rows.forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(filter) ? '' : 'none';
    });
  }

  /**
   * Copy Root Time to Clipboard.
   */
  function copyRootTime() {
    const kpiTime = document.getElementById('kpiRootTime');
    if (!kpiTime) return;
    const text = kpiTime.textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast(`Copied ${text} to clipboard!`, 'success');
    }).catch(() => {
      showToast('Could not copy to clipboard.', 'error');
    });
  }

  /**
   * Download results as PDF using print dialog or html2pdf.
   */
  function downloadResultsPdf() {
    showToast('Preparing PDF report...', 'info');
    setTimeout(() => {
      window.print();
    }, 400);
  }

  /**
   * Reset form and results.
   */
  function resetForm() {
    if (form) form.reset();
    clearFieldErrors();
    presetChips.forEach((c) => c.classList.remove('active'));
    showToast('Form reset to default values.', 'info');
  }

  // Bind Events on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    if (form) {
      form.addEventListener('submit', handleCalculationSubmit);
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', resetForm);
    }
    if (tableSearchInput) {
      tableSearchInput.addEventListener('input', filterTableRows);
    }
    if (copyTimeBtn) {
      copyTimeBtn.addEventListener('click', copyRootTime);
    }
    if (downloadPdfBtn) {
      downloadPdfBtn.addEventListener('click', downloadResultsPdf);
    }
    presetChips.forEach((chip) => {
      chip.addEventListener('click', handlePresetClick);
    });

    // Check if initial simulation data exists in embedded JSON block
    const initialDataEl = document.getElementById('initialResultData');
    if (initialDataEl) {
      try {
        const initialResult = JSON.parse(initialDataEl.textContent);
        renderResults(initialResult);
      } catch (err) {
        console.warn('Could not parse initial data:', err);
      }
    }
  });

  // Global namespace for external access
  window.TankFillCalculator = {
    renderResults,
    updateTankVisualizer,
    showToast,
  };
})();
