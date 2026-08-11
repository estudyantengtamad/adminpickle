/**
 * Pickle Legends Admin Platform - Core Frontend Script
 * Handles navigation, interactive AJAX actions, profile inspector, court grid toggles, and modals.
 */

// Toast Notifications System
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    document.body.appendChild(el);
    return el;
  })();

  const toast = document.createElement('div');
  const bgColor = type === 'success' ? 'bg-emerald-600' : (type === 'danger' ? 'bg-rose-600' : 'bg-indigo-600');
  
  toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-xl flex items-center space-x-3 mb-2 transition-all duration-300 transform translate-y-2 opacity-0 text-sm font-medium`;
  toast.innerHTML = `
    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Mobile Sidebar Toggle
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('mobileSidebarToggle');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('-translate-x-full');
      if (overlay) overlay.classList.toggle('hidden');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.add('-translate-x-full');
      overlay.classList.add('hidden');
    });
  }
});

// Quick Admin Actions (Executive Dashboard)
async function triggerQuickAction(actionType, customPayload = {}) {
  try {
    let endpoint = `/api/action/${actionType}`;
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customPayload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
    } else {
      showToast(data.message || 'Action failed.', 'danger');
    }
  } catch (err) {
    console.error(err);
    showToast('Network error triggering admin action.', 'danger');
  }
}

// User Profile Inspector Selection & Filter Logic
function selectPlayer(playerJson) {
  const player = typeof playerJson === 'string' ? JSON.parse(playerJson) : playerJson;
  const inspector = document.getElementById('profileInspector');
  if (!inspector) return;

  document.getElementById('inspPlayerId').innerText = player.id;
  document.getElementById('inspPlayerName').innerText = player.name;
  document.getElementById('inspElo').innerText = player.elo;
  document.getElementById('inspTier').innerText = player.tier;
  document.getElementById('inspWinRate').innerText = player.win_rate;
  document.getElementById('inspMatches').innerText = player.matches;
  document.getElementById('inspStatus').innerText = player.status;
  document.getElementById('inspNotes').innerText = player.notes || 'No notes available.';

  // Highlight status badge color
  const statusBadge = document.getElementById('inspStatus');
  statusBadge.className = 'px-2.5 py-1 rounded-full text-xs font-semibold ' + (
    player.status === 'Active' ? 'bg-emerald-100 text-emerald-800' :
    player.status === 'Frozen' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
  );

  // Set active row highlight
  document.querySelectorAll('.player-row').forEach(row => row.classList.remove('bg-indigo-50/70', 'border-l-4', 'border-indigo-600'));
  const selectedRow = document.getElementById(`row-${player.id}`);
  if (selectedRow) selectedRow.classList.add('bg-indigo-50/70', 'border-l-4', 'border-indigo-600');
}

async function performPlayerAction(action) {
  const playerId = document.getElementById('inspPlayerId').innerText;
  if (!playerId || playerId === '-') {
    showToast('Please select a player first.', 'info');
    return;
  }

  try {
    const res = await fetch(`/api/users/${playerId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      if (data.status) {
        document.getElementById('inspStatus').innerText = data.status;
        const rowStatus = document.getElementById(`status-${playerId}`);
        if (rowStatus) {
          rowStatus.innerText = data.status;
          rowStatus.className = 'px-2.5 py-1 rounded-full text-xs font-semibold ' + (
            data.status === 'Active' ? 'bg-emerald-100 text-emerald-800' :
            data.status === 'Frozen' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
          );
        }
      }
      if (data.elo !== undefined) {
        document.getElementById('inspElo').innerText = data.elo;
        const rowElo = document.getElementById(`elo-${playerId}`);
        if (rowElo) rowElo.innerText = data.elo;
      }
    } else {
      showToast(data.message || 'Player action failed.', 'danger');
    }
  } catch (err) {
    showToast('Failed to connect to backend server.', 'danger');
  }
}

// User Search & Filter Handler
function filterPlayers() {
  const query = document.getElementById('userSearchInput')?.value.toLowerCase() || '';
  const tierFilter = document.getElementById('tierFilterSelect')?.value || 'ALL';
  const statusFilter = document.getElementById('statusFilterSelect')?.value || 'ALL';

  document.querySelectorAll('.player-row').forEach(row => {
    const name = row.getAttribute('data-name').toLowerCase();
    const id = row.getAttribute('data-id').toLowerCase();
    const tier = row.getAttribute('data-tier');
    const status = row.getAttribute('data-status');

    const matchesSearch = name.includes(query) || id.includes(query);
    const matchesTier = tierFilter === 'ALL' || tier === tierFilter;
    const matchesStatus = statusFilter === 'ALL' || status === statusFilter;

    if (matchesSearch && matchesTier && matchesStatus) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

// Matchmaking Controls
async function saveMatchmakingParams() {
  const maxSkillGap = document.getElementById('skillGapInput')?.value || 50;
  const densityMult = document.getElementById('densityMultiplierInput')?.value || 1.25;
  const smartMatch = document.getElementById('smartMatchToggle')?.checked ?? True;

  try {
    const res = await fetch('/api/matchmaking/save_params', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        max_skill_gap: maxSkillGap,
        density_multiplier: densityMult,
        smart_matchmaking: smartMatch
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
    }
  } catch (err) {
    showToast('Error saving matchmaking parameters.', 'danger');
  }
}

async function forceMatchSearch() {
  try {
    const res = await fetch('/api/matchmaking/force_search', { method: 'POST' });
    const data = await res.json();
    showToast(data.message, 'success');
  } catch (err) {
    showToast('Error forcing match search.', 'danger');
  }
}

async function emergencyResetMatchmaker() {
  if (!confirm('Are you sure you want to trigger an emergency reset on the matchmaking engine?')) return;
  try {
    const res = await fetch('/api/matchmaking/reset', { method: 'POST' });
    const data = await res.json();
    showToast(data.message, 'danger');
  } catch (err) {
    showToast('Error resetting matchmaking engine.', 'danger');
  }
}

// Venue & Court Grid Matrix Interactions
async function toggleCourtSlot(timeSlot, court) {
  try {
    const res = await fetch('/api/venues/toggle_slot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time_slot: timeSlot, court: court })
    });
    const data = await res.json();
    if (data.success) {
      const cell = document.getElementById(`slot-${timeSlot.replace(/[^a-zA-Z0-9]/g, '')}-${court.replace(/\s+/g, '')}`);
      if (cell) {
        cell.className = `court-cell p-3 rounded-lg text-center font-semibold text-xs transition-all shadow-sm status-${data.new_status}`;
        cell.innerText = data.new_status;
      }
      showToast(data.message, 'success');
    }
  } catch (err) {
    showToast('Failed to toggle court status.', 'danger');
  }
}

async function addCourtTimeSlot() {
  const time = prompt('Enter new schedule time slot (e.g. 08:00 PM):', '08:00 PM');
  if (!time) return;

  try {
    const res = await fetch('/api/venues/add_slot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(data.message, 'danger');
    }
  } catch (err) {
    showToast('Error adding time slot.', 'danger');
  }
}

async function blockTimeSlot() {
  const slot = prompt('Enter time slot to block all courts for maintenance (e.g. 04:00 PM):', '04:00 PM');
  if (!slot) return;

  try {
    const res = await fetch('/api/venues/block_time', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time_slot: slot })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'warning');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(data.message, 'danger');
    }
  } catch (err) {
    showToast('Error blocking time slot.', 'danger');
  }
}

async function cancelBookingPrompt() {
  const court = prompt('Enter Court Name to cancel & refund (e.g. Court 1):', 'Court 1');
  if (!court) return;
  const slot = prompt('Enter Time Slot (e.g. 10:00 AM):', '10:00 AM');
  if (!slot) return;

  try {
    const res = await fetch('/api/venues/cancel_booking', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ court, time_slot: slot })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(data.message, 'danger');
    }
  } catch (err) {
    showToast('Error cancelling booking.', 'danger');
  }
}

// Moderation Actions
async function handleReportAction(reportId, action) {
  try {
    const res = await fetch('/api/moderation/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_id: reportId, action })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      const badge = document.getElementById(`rep-status-${reportId}`);
      if (badge) {
        badge.innerText = data.status;
        badge.className = 'px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800';
      }
    }
  } catch (err) {
    showToast('Error handling moderation report.', 'danger');
  }
}

async function submitNewEvent(event) {
  event.preventDefault();
  const title = document.getElementById('evtTitle').value;
  const venue = document.getElementById('evtVenue').value;
  const date = document.getElementById('evtDate').value;
  const tag = document.getElementById('evtTag').value;

  try {
    const res = await fetch('/api/moderation/create_event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, venue, date, tag })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(() => location.reload(), 800);
    }
  } catch (err) {
    showToast('Error creating tournament posting.', 'danger');
  }
}

// System Settings RECIPE Sliders Handler
async function saveRecipeSettings(event) {
  event.preventDefault();
  const payload = {
    recognition: document.getElementById('recVal').value,
    engagement: document.getElementById('engVal').value,
    competition: document.getElementById('compVal').value,
    improvement: document.getElementById('impVal').value,
    play: document.getElementById('playVal').value,
    experience: document.getElementById('expVal').value,
  };

  try {
    const res = await fetch('/api/settings/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      setTimeout(() => location.reload(), 1000);
    }
  } catch (err) {
    showToast('Failed to save RECIPE settings.', 'danger');
  }
}
