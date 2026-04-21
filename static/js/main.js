// File selection display
const fileInput = document.getElementById('fileInput');
const fileList  = document.getElementById('fileList');

fileInput.addEventListener('change', () => {
  fileList.innerHTML = '';
  Array.from(fileInput.files).forEach(f => {
    const chip = document.createElement('span');
    chip.className = 'file-chip';
    chip.textContent = f.name;
    fileList.appendChild(chip);
  });
});

// Form submit
document.getElementById('screenForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errDiv = document.getElementById('error');
  const results = document.getElementById('results');
  const btn = document.getElementById('submitBtn');
  errDiv.style.display = 'none';
  results.innerHTML = '';

  const jd = document.getElementById('jd').value.trim();
  if (!jd) { showError('Please enter a job description.'); return; }
  if (!fileInput.files.length) { showError('Please upload at least one PDF resume.'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Analyzing candidates…';

  const formData = new FormData(e.target);

  try {
    const resp = await fetch('/screen', { method: 'POST', body: formData });
    const data = await resp.json();
    if (data.error) { showError(data.error); return; }
    renderResults(data.candidates);
  } catch (err) {
    showError('Server error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Screen Candidates';
  }
});

function showError(msg) {
  const e = document.getElementById('error');
  e.textContent = msg;
  e.style.display = 'block';
}

function barColor(s) {
  if (s >= 75) return '#5340C9';
  if (s >= 55) return '#378ADD';
  return '#888780';
}

function scoreClass(s) {
  if (s >= 75) return 'sp-high';
  if (s >= 55) return 'sp-mid';
  return 'sp-low';
}

function rankBadgeClass(i) {
  return ['r1','r2','r3'][i] || 'rn';
}

function renderResults(candidates) {
  const area = document.getElementById('results');
  let html = `<h2>Results — ${candidates.length} candidate${candidates.length > 1 ? 's' : ''} ranked</h2>`;

  candidates.forEach((c, i) => {
    const matched = (c.matched_skills || []).slice(0, 8).map(s =>
      `<span class="skill-tag sk-match">${s}</span>`).join('');
    const missing = (c.missing_skills || []).slice(0, 6).map(s =>
      `<span class="skill-tag sk-miss">${s}</span>`).join('');

    html += `
    <div class="candidate-card ${i === 0 ? 'rank-1' : ''}">
      <div class="c-header">
        <div class="rank-badge ${rankBadgeClass(i)}">#${i + 1}</div>
        <div class="c-name">${c.name}</div>
        <div class="score-pill ${scoreClass(c.score)}">${c.score}/100</div>
      </div>
      <div class="bar-wrap">
        <div class="bar-fill" style="width:${c.score}%;background:${barColor(c.score)}"></div>
      </div>
      <div class="meta-row">
        <div>Verdict: <span>${c.verdict}</span></div>
        <div>Skill match: <span>${c.skill_match_pct}%</span></div>
        <div>TF-IDF similarity: <span>${c.tfidf_similarity}%</span></div>
        ${c.experience_years ? `<div>Experience: <span>~${c.experience_years} yrs</span></div>` : ''}
        <div>Education: <span>${c.education}</span></div>
      </div>
      ${matched ? `<div class="skills-row">${matched}</div>` : ''}
      ${missing ? `<div class="skills-row">${missing}</div>` : ''}
      <div class="reasoning">
        <strong>Strengths:</strong> ${c.strengths}<br>
        <strong>Gaps:</strong> ${c.gaps}
      </div>
    </div>`;
  });

  area.innerHTML = html;
}
