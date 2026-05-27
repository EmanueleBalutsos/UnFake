/* ═══════════════════════════════════════════════════════════════
 *  app.js — 
 *  Talks to Flask backend at the same origin 
 ═ *══════════════════════════════════════════════════════════════ */

// ── State ─────────────────────────────────────────────────────
let currentQuery       = "";
let allArticles        = [];
let selectedSources    = [];
let selectedSentiments = ["positive", "neutral", "negative"];
let feedbackRating     = null;
let pieChart           = null;
let barChart           = null;

// ── SVG Icons ─────────────────────────────────────────────────
const ICONS = {
  search: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
  filter: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>`,
  tags:   `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>`,
  brain:  `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2a2.5 2.5 0 0 1 5 0v1.5"/><path d="M14.5 3.5a5 5 0 0 1 4.5 5v1a2 2 0 0 1 0 4v1a5 5 0 0 1-5 5h-4a5 5 0 0 1-5-5v-1a2 2 0 0 1 0-4v-1a5 5 0 0 1 4.5-5"/></svg>`,
  thumbUp:   `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>`,
  thumbDown: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3z"/><path d="M17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/></svg>`,
  meh:       `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="15" x2="16" y2="15"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`,
};

// ── DOM references ─────────────────────────────────────────────
const searchSection  = document.getElementById("search-section");
const resultsSection = document.getElementById("results-section");
const mainSearchInput  = document.getElementById("main-search-input");
const inlineSearchInput = document.getElementById("inline-search-input");
const queryLabel     = document.getElementById("query-label");
const headlinesCount = document.getElementById("headlines-count");
const headlinesList  = document.getElementById("headlines-list");
const sourceFilters  = document.getElementById("source-filters");
const sentimentFilters = document.getElementById("sentiment-filters");
const analysisCol    = document.getElementById("analysis-col");
const errorMsg       = document.getElementById("error-message");
const feedbackSection = document.getElementById("feedback-section");

// ── Search ─────────────────────────────────────────────────────
async function handleSearch(query) {
  if (!query.trim()) return;

  currentQuery    = query;
  feedbackRating  = null;

  // Switch to results view
  searchSection.style.display  = "none";
  resultsSection.style.display = "block";
  queryLabel.textContent       = `"${query}"`;
  inlineSearchInput.value      = query;
  errorMsg.style.display       = "none";
  feedbackSection.style.display = "none";

  // Show skeletons while loading
  showSkeletons();

  try {
    const res  = await fetch("/search", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ event: query }),
    });

    if (!res.ok) throw new Error("Search failed");

    const data = await res.json();

    allArticles = (data.articles || []).map((a, i) => ({
      id:        a.url || String(i),
                                                       headline:  a.title || a.headline || "No Title",
                                                       source:    a.source || "Unknown Source",
                                                       sentiment: a.sentiment || "neutral",
                                                       actors:    a.actors    || [],
                                                       tone:      a.tone      || "Neutral",
                                                       tone_intensity: a.tone_intensity || 3, 
                                                       firstWord: a.firstWord || a.key_phrase || "",
                                                       url:       a.url       || null,
                                                       description: a.description || "",
    }));

    // Auto-select all sources from fresh results
    selectedSources    = [...new Set(allArticles.map(a => a.source))];
    selectedSentiments = ["positive", "neutral", "negative"];

    buildFilters();
    renderResults();
    feedbackSection.style.display = "block";
    resetFeedbackForm();

  } catch (err) {
    console.error(err);
    errorMsg.textContent   = "An error occurred during the search. Please try again.";
    errorMsg.style.display = "block";
    headlinesList.innerHTML = "";
    analysisCol.style.display = "none";
  }
}

// ── Skeletons ──────────────────────────────────────────────────
function showSkeletons() {
  headlinesList.innerHTML = `
  <div class="loading-cards">
  ${[1,2,3].map(() => `
    <div class="skeleton-card">
    <div class="skeleton-line" style="width:40%;height:12px;"></div>
    <div class="skeleton-line" style="width:90%;height:20px;margin-top:14px;"></div>
    <div class="skeleton-line" style="width:70%;height:16px;"></div>
    <div class="skeleton-line" style="width:50%;height:12px;"></div>
    </div>`).join("")}
    </div>`;
    analysisCol.style.display = "none";
}

// ── Filters ────────────────────────────────────────────────────
function buildFilters() {
  const sources = [...new Set(allArticles.map(a => a.source))];

  // Source checkboxes
  sourceFilters.innerHTML = `<p class="filter-group-label">Source</p>`;
  sources.forEach(src => {
    const label = document.createElement("label");
    label.className = "filter-item";
    label.innerHTML = `<input type="checkbox" ${selectedSources.includes(src) ? "checked" : ""}/><span title="${esc(src)}">${esc(src)}</span>`;
    label.querySelector("input").addEventListener("change", () => {
      toggleFilter(selectedSources, src);
      renderResults();
      // rebuild to keep checkbox state in sync
      buildFilters();
    });
    sourceFilters.appendChild(label);
  });

  // Sentiment checkboxes
  sentimentFilters.innerHTML = `<p class="filter-group-label">Sentiment</p>`;
  ["positive", "neutral", "negative"].forEach(s => {
    const label = document.createElement("label");
    label.className = "filter-item capitalize";
    label.innerHTML = `<input type="checkbox" ${selectedSentiments.includes(s) ? "checked" : ""}/><span>${s}</span>`;
    label.querySelector("input").addEventListener("change", () => {
      toggleFilter(selectedSentiments, s);
      renderResults();
      buildFilters();
    });
    sentimentFilters.appendChild(label);
  });
}

function toggleFilter(arr, value) {
  const idx = arr.indexOf(value);
  if (idx === -1) arr.push(value);
  else arr.splice(idx, 1);
}

// ── Render results ─────────────────────────────────────────────
function renderResults() {
  const filtered = allArticles.filter(a =>
  selectedSources.includes(a.source) &&
  selectedSentiments.includes(a.sentiment)
  );

  headlinesCount.textContent = `Headlines (${filtered.length})`;
  headlinesList.innerHTML    = "";

  if (filtered.length === 0) {
    headlinesList.innerHTML = `<p class="no-results">No articles match your selected filters.</p>`;
    analysisCol.style.display = "none";
    return;
  }

  analysisCol.style.display = "flex";
  filtered.forEach(article => headlinesList.appendChild(buildCard(article)));
  renderCharts(filtered);
  renderActors(filtered);
}

// ── Result card ────────────────────────────────────────────────
function buildCard(article) {
  //const badgeClass = { positive: "badge-positive", negative: "badge-negative", neutral: "badge-neutral" }[article.sentiment] || "badge-neutral";
  //const icon       = { positive: ICONS.thumbUp, negative: ICONS.thumbDown, neutral: ICONS.meh }[article.sentiment] || ICONS.meh;

  // Highlight first two words
  const idx = article.headline.indexOf(article.firstWord);
  let headlineHTML = esc(article.headline);
  if (idx !== -1 && article.firstWord) {
    headlineHTML =
    esc(article.headline.slice(0, idx)) +
    `<mark class="headline-highlight">${esc(article.firstWord)}</mark>` +
    esc(article.headline.slice(idx + article.firstWord.length));
  }

  const actorTags = (article.actors || []).map(a => `<span class="actor-tag">${esc(a)}</span>`).join("");  const urlLine   = article.url ? `<div class="card-url"><a href="${esc(article.url)}" target="_blank" rel="noopener">Read original article ↗</a></div>` : "";
  
  const analysisTags = [
    article.frame   ? `<span class="analysis-tag tag-frame">Frame: ${esc(article.frame)}</span>`   : "",
    article.genre   ? `<span class="analysis-tag tag-genre">Genre: ${esc(article.genre)}</span>`   : "",
    article.focus   ? `<span class="analysis-tag tag-focus">Focus: ${esc(article.focus)}</span>`   : "",
    article.tone    ? `<span class="analysis-tag tag-tone">Tone: ${esc(article.tone)}</span>`      : "",
    article.biases  ? `<span class="analysis-tag tag-bias">Bias: ${esc(article.biases)}</span>`    : "",
  ].filter(Boolean).join("");
  
  const card = document.createElement("article");
  card.className = "result-card";
  card.innerHTML = `
  <div class="card-top">
    <div class="source-info">
      <div class="source-avatar">${esc(article.source.charAt(0))}</div>
      <span class="source-name">${esc(article.source)}</span>
    </div>
  </div>
  <h3 class="card-headline">${headlineHTML}</h3>
  <div class="card-meta">
  ${analysisTags ? `<div class="analysis-tags">${analysisTags}</div>` : ""}
  ${actorTags ? `<div class="meta-actors">${ICONS.tags}<div class="actor-tags">${actorTags}</div></div>` : ""}
  </div>
  ${urlLine}
  <div class="card-footer">${buildStarRating(article)}</div>
  `;
  return card;
}

// ── Star rating (Mostra il voto dell'Intelligenza Artificiale) ──
function buildStarRating(article) {
  const intensity = article.tone_intensity || 3;

  let starsHtml = "";
  for (let i = 1; i <= 5; i++) {
    if (i <= intensity) {
      starsHtml += `<span class="star filled" style="color: #f59e0b; font-size: 1.2rem;">★</span>`;
    } else {
      starsHtml += `<span class="star" style="color: #e2e8f0; font-size: 1.2rem;">★</span>`;
    }
  }

  return `
  <div class="star-rating">
  <span class="rating-label">AI Tone Intensity: ${intensity}/5</span>
  <div class="stars">
  ${starsHtml}
  </div>
  </div>`;
}

// ── Charts ─────────────────────────────────────────────────────
function renderCharts(articles) {
  // Tone pie
  const toneCounts = {};
  articles.forEach(a => {
    const t = (a.tone || "Unknown").trim();
    toneCounts[t] = (toneCounts[t] || 0) + 1;
  });

  // Auto-assign a color to each unique tone
  const toneColorPalette = [
    "#4f46e5", "#10b981", "#f59e0b", "#f43f5e", "#64748b",
    "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16", "#f97316"
  ];
  const toneLabels = Object.keys(toneCounts);
  const toneColors = toneLabels.map((_, i) => toneColorPalette[i % toneColorPalette.length]);

  if (pieChart) pieChart.destroy();
  pieChart = new Chart(document.getElementById("pie-chart"), {
    type: "doughnut",
    data: {
      labels: toneLabels,
      datasets: [{ data: Object.values(toneCounts), backgroundColor: toneColors, borderWidth: 0, hoverOffset: 6 }],
    },
    options: {responsive: true,maintainAspectRatio: true,cutout: "65%",
      plugins: {legend: {position: "bottom",align: "start",
          labels: {usePointStyle: true,pointStyle: "circle",padding: 16,
            font: { family: "'DM Sans'", size: 12 },
            color: "#717182",
          },
        },
      },
    },
  });

  // Source bar
  const srcCounts = {};
  articles.forEach(a => { srcCounts[a.source] = (srcCounts[a.source] || 0) + 1; });

  if (barChart) barChart.destroy();
  barChart = new Chart(document.getElementById("bar-chart"), {
    type: "bar",
    data: {
      labels: Object.keys(srcCounts),
                       datasets: [{ label: "Articles", data: Object.values(srcCounts), backgroundColor: "#4f46e5", borderRadius: 5, barThickness: 28 }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, border: { display: false }, ticks: { font: { family: "'DM Sans'", size: 11 }, color: "#717182" } },
        y: { grid: { color: "#f0f0f2" }, border: { display: false }, ticks: { precision: 0, font: { family: "'DM Sans'", size: 11 }, color: "#717182" } },
      },
    },
  });
}

// ── Actors ─────────────────────────────────────────────────────
function renderActors(articles) {
  const counts = {};
  articles.forEach(a => a.actors.forEach(actor => { counts[actor] = (counts[actor] || 0) + 1; }));
  const top = Object.entries(counts).sort((a,b) => b[1]-a[1]).slice(0, 5);

  document.getElementById("actors-list").innerHTML = top.length > 0
  ? top.map(([actor, count]) => `<div class="actor-chip">${esc(actor)}<span class="actor-chip-count">${count}</span></div>`).join("")
  : `<p style="font-size:.85rem;color:var(--text-400)">No actors identified yet.</p>`;
}

// ── Global feedback form ───────────────────────────────────────
function resetFeedbackForm() {
  feedbackRating = null;
  document.getElementById("feedback-success").style.display = "none";
  document.getElementById("feedback-form").style.display    = "block";
  document.getElementById("feedback-comment").value         = "";
  document.querySelectorAll(".rating-buttons button").forEach(b => b.classList.remove("active"));
}

document.querySelectorAll(".rating-buttons button").forEach(btn => {
  btn.addEventListener("click", () => {
    feedbackRating = +btn.dataset.rating;
    document.querySelectorAll(".rating-buttons button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

document.getElementById("feedback-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!feedbackRating) return;

  const comment  = document.getElementById("feedback-comment").value;
  const language = navigator.language.split("-")[0] || "en";

  try {
    await fetch("/feedback", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ event: currentQuery, rating: feedbackRating, comment, language }),
    });
    document.getElementById("feedback-form").style.display    = "none";
    document.getElementById("feedback-success").style.display = "block";
  } catch(err) { console.error("Global feedback error:", err); }
});

// ── Event listeners ────────────────────────────────────────────
document.getElementById("main-search-btn").addEventListener("click", () => {
  handleSearch(mainSearchInput.value);
});
mainSearchInput.addEventListener("keydown", e => { if (e.key === "Enter") handleSearch(mainSearchInput.value); });

document.getElementById("inline-search-btn").addEventListener("click", () => {
  handleSearch(inlineSearchInput.value);
});
inlineSearchInput.addEventListener("keydown", e => { if (e.key === "Enter") handleSearch(inlineSearchInput.value); });

// ── Utility ────────────────────────────────────────────────────
function esc(str) {
  return String(str || "")
  .replace(/&/g,"&amp;").replace(/</g,"&lt;")
  .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
