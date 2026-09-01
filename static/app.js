/* ═══════════════════════════════════════════════════════════════
 * app.js
 * Talks to Flask backend at the same origin
 ═ *═══════════**═══════════════════════════════════════════════════ */

// ── State ─────────────────────────────────────────────────────
let currentQuery       = "";
let allArticles        = [];
let selectedSources    = [];
let selectedSentiments = ["positive", "neutral", "negative"];
let feedbackRating     = null;
let pieChart           = null;
let genreChart         = null;
let barChart           = null;
let secondaryEmotionChart = null;

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

// ── Tag Tooltips ───────────────────────────────────────────────
const TAG_TOOLTIPS = {
  frame: {
    CONFLICT:       "Presents opposing actors, forces, or interpretations in tension.",
    GAME_STRATEGY:  "Focuses on actors pursuing goals, gaining advantage, or mobilizing support",
    THEMATIC:       "Centers on a broader social/political issue or systemic concern.",
    HUMAN_INTEREST: "Tells the story through the personal experience of individuals directly affected by the issue.",
    EPISODIC:       "Presents a specific event as an isolated occurrence without connecting it to wider trends or causes.",
    OTHER:          "Headline does not fit any of the generic framing categories.",
  },
  genre: {
    INFORMATIVE:    "Straightforward reporting of facts and events with minimal interpretation.",
    INVESTIGATIVE:  "Aims to expose hidden truths or systemic issues.",
    ANALYTIC:       "Explains causes, context, or implications beyond the immediate surface facts.",
    EDITORIAL:      "Persuasive, opinion-driven piece that expresses a viewpoint, argument, or endorsement.",
    ENTERTAINMENT:  "Lifestyle, culture, soft news primarily aimed at engaging or amusing the audience.",
    OTHER:          "Headline does not clearly fit a standard category for the genre/intent.",
  },
  focus: {
    ECONOMIC:       "Framed around financial cost, trade, economic growth, or fiscal impact.",
    RESOURCES:      "Centered on natural resources, energy, land, or supply chains.",
    MORALITY:       "Raises ethical questions, values, or moral judgements.",
    FAIRNESS:       "Concerns justice, equality, rights, or distribution of outcomes.",
    LEGAL:          "Involves legislation, regulation, court decisions, or legal accountability.",
    POLICY:         "Discusses government decisions, public policy, or institutional action.",
    CRIME:          "Relates to criminal activity, law enforcement, or public order.",
    SECURITY:       "Covers threats, conflict, military action, or national security.",
    HEALTH:         "Focuses on physical or mental health, medicine, or epidemiology.",
    QOL:            "Addresses quality of life, wellbeing, housing, or social conditions.",
    CULTURAL_ID:    "Touches on cultural values, identity, religion, or social cohesion.",
    PUBLIC_OPINION: "Highlights polls, popular sentiment, or public reaction.",
    POLITICAL:      "Centers on electoral dynamics, party politics, or power relations.",
    OTHER:          "Headline does not clearly fit a standard category for focus.",
  },
  agency: {
    ACTIVE:     "Directly driving or performing the actions described in the headline.",
    PASSIVE:    "Affected by events but not the initiator of the actions.",
    MENTIONNED: "Referenced in the headline but not central to the described action.",
  },
  bias: {
    POLITICAL:      "Favors or disparages a political group, party, or ideology.",
    GENDER:         "Uses language that stereotypes or unequally represents genders.",
    CULTURAL:       "Frames an issue through a specific cultural lens, marginalizing others.",
    AGE:            "Stereotypes or dismisses individuals based on their age group.",
    RELIGION:       "Portrays a religious group or belief system in a skewed way.",
    DISABILITY:     "Uses language that stigmatizes or misrepresents people with disabilities.",
    STATEMENT:      "Presents an unverified claim or allegation as established fact.",
    OMISSION:       "Leaves out key context or facts that would change the reader's interpretation.",
    SENSATIONALISM: "Uses exaggerated or dramatic language to provoke a strong emotional reaction.",
    NEGATIVITY:     "Disproportionately emphasizes negative aspects while ignoring positives.",
    SUBJECTIVE:     "Injects personal opinion or value-laden language into what should be neutral reporting.",
    ADHOMINEM:      "Attacks a person's character rather than addressing the substance of the issue.",
    OPINION:        "Presents an editorial opinion or judgement as if it were objective reporting.",
  },
};

const TONE_INTENSITY_TOOLTIP =
"1: Neutral, factual  ·  2: Mildly toned  ·  3: Moderately emotive  ·  4: Highly charged  ·  5: Strongly sensational";

    function tagTooltip(type, value) {
      const map = TAG_TOOLTIPS[type] || {};
      return map[(value || "").toUpperCase()] || "No description available.";
    }

    // ── DOM References ─────────────────────────────────────────────
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
    async function handleSearch(query, country = "US", engine = "duckduckgo") {
      if (!query.trim()) return;

      document.getElementById("main-engine-select").value = engine;
      document.getElementById("inline-engine-select").value = engine;

      currentQuery    = query;
      feedbackRating  = null;

      searchSection.style.display  = "none";
      resultsSection.style.display = "block";
      queryLabel.textContent       = `"${query}"`;
      inlineSearchInput.value      = query;

      document.getElementById("inline-country-select").value = country;
      document.getElementById("main-country-select").value = country;

      errorMsg.style.display       = "none";
      feedbackSection.style.display = "none";

      showSkeletons();

      try {
        const res  = await fetch("/search", {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify({ event: query, country: country, engine: engine }),
        });

        if (!res.ok) throw new Error("Search failed");

        const data = await res.json();

        allArticles = (data.articles || []).map((a, i) => ({
          id:          a.url || String(i),
                                                           headline:    a.title || a.headline || "No Title",
                                                           source:      a.source || "Unknown Source",
                                                           sentiment:   Array.isArray(a.sentiment) ? a.sentiment : [a.sentiment || "NEUTRAL"],
                                                           actors:      a.actors    || [],
                                                           frame:       a.frame     || "OTHER",
                                                           biases:      a.biases    || {},
                                                           focuses:     a.focuses   || [],
                                                           genre:       a.genre      || "OTHER",
                                                           tone_intensity: a.tone_intensity || 3,
                                                           firstWord:   a.firstWord || a.key_phrase || "",
                                                           url:         a.url       || null,
                                                           description: a.description || "",
        }));

        selectedSources = [...new Set(allArticles.map(a => a.source))];
        const emotionsSet = new Set();
        allArticles.forEach(a => {
          if (Array.isArray(a.sentiment)) {
            a.sentiment.forEach(emo => emotionsSet.add(emo));
          } else {
            emotionsSet.add(a.sentiment);
          }
        });
        selectedSentiments = [...emotionsSet];

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

    // ── Filters ─────────────────────────────────────────────────────
    function buildFilters() {
      const sources = [...new Set(allArticles.map(a => a.source))];
      const webSources = sources.filter(src => src.includes('.'));
      const traditionalSources = sources.filter(src => !src.includes('.'));

      sourceFilters.innerHTML = `<p class="filter-group-label" style="font-size:1.1rem; margin-bottom: 12px;">Sources</p>`;

      const allSelected = sources.length > 0 && selectedSources.length === sources.length;
      const tradSelected = traditionalSources.length > 0 && traditionalSources.every(s => selectedSources.includes(s));
      const webSelected = webSources.length > 0 && webSources.every(s => selectedSources.includes(s));

      const safeUpdate = () => {
        try {
          renderResults();
        } catch (err) {
          console.warn("Chart.js ha bloccato il render per mancanza di dati. Resetto la vista manualmente.", err);
          const headlinesList = document.getElementById("headlines-list");
          const headlinesCount = document.getElementById("headlines-count");
          if (headlinesList) headlinesList.innerHTML = `<p style="padding: 20px; color: #666;">Nessuna fonte selezionata. Seleziona una fonte a sinistra.</p>`;
          if (headlinesCount) headlinesCount.textContent = "Headlines (0)";
        }
        buildFilters();
      };

      const masterTogglesContainer = document.createElement("div");
      masterTogglesContainer.style.display = "flex";
      masterTogglesContainer.style.flexDirection = "column";
      masterTogglesContainer.style.gap = "8px";
      masterTogglesContainer.style.borderBottom = "1px solid var(--border-light)";
      masterTogglesContainer.style.paddingBottom = "12px";
      masterTogglesContainer.style.marginBottom = "12px";

      const allLabel = document.createElement("label");
      allLabel.className = "filter-item";
      allLabel.style.fontWeight = "bold";
      allLabel.innerHTML = `<input type="checkbox" ${allSelected ? "checked" : ""} /><span>All Sources</span>`;
      allLabel.querySelector("input").addEventListener("change", (e) => {
        selectedSources = e.target.checked ? [...sources] : [];
        safeUpdate();
      });
      masterTogglesContainer.appendChild(allLabel);

      if (traditionalSources.length > 0) {
        const tradLabel = document.createElement("label");
        tradLabel.className = "filter-item";
        tradLabel.style.fontWeight = "600";
        tradLabel.style.marginLeft = "12px";
        tradLabel.innerHTML = `<input type="checkbox" ${tradSelected ? "checked" : ""} /><span style="color: #4f46e5;">All Traditional Media</span>`;
        tradLabel.querySelector("input").addEventListener("change", (e) => {
          if (e.target.checked) {
            traditionalSources.forEach(s => { if (!selectedSources.includes(s)) selectedSources.push(s); });
          } else {
            selectedSources = selectedSources.filter(s => !traditionalSources.includes(s));
          }
          safeUpdate();
        });
        masterTogglesContainer.appendChild(tradLabel);
      }

      if (webSources.length > 0) {
        const webLabel = document.createElement("label");
        webLabel.className = "filter-item";
        webLabel.style.fontWeight = "600";
        webLabel.style.marginLeft = "12px";
        webLabel.innerHTML = `<input type="checkbox" ${webSelected ? "checked" : ""} /><span style="color: #4f46e5;">All New Media</span>`;
        webLabel.querySelector("input").addEventListener("change", (e) => {
          if (e.target.checked) {
            webSources.forEach(s => { if (!selectedSources.includes(s)) selectedSources.push(s); });
          } else {
            selectedSources = selectedSources.filter(s => !webSources.includes(s));
          }
          safeUpdate();
        });
        masterTogglesContainer.appendChild(webLabel);
      }

      sourceFilters.appendChild(masterTogglesContainer);

      const columnsContainer = document.createElement("div");
      columnsContainer.style.display = "grid";
      columnsContainer.style.gridTemplateColumns = "1fr 1fr";
      columnsContainer.style.gap = "16px";
      columnsContainer.style.width = "100%";
      columnsContainer.style.minWidth = "300px";

      const renderCategoryColumn = (sourceList, categoryTitle) => {
        const col = document.createElement("div");
        col.style.display = "flex";
        col.style.flexDirection = "column";
        col.style.gap = "6px";
        col.style.minWidth = "0";

        const catHeader = document.createElement("div");
        catHeader.style.fontWeight = "bold";
        catHeader.style.fontSize = "0.70rem";
        catHeader.style.textTransform = "uppercase";
        catHeader.style.color = "#6b7280";
        catHeader.style.borderBottom = "1px solid #e5e7eb";
        catHeader.style.paddingBottom = "4px";
        catHeader.style.marginBottom = "6px";
        catHeader.textContent = categoryTitle;
        col.appendChild(catHeader);

        sourceList.forEach(src => {
          const label = document.createElement("label");
          label.className = "filter-item";
          label.style.overflow = "hidden";
          label.style.textOverflow = "ellipsis";
          label.style.whiteSpace = "nowrap";

          label.innerHTML = `<input type="checkbox" ${selectedSources.includes(src) ? "checked" : ""}/><span title="${src}">${src}</span>`;

          label.querySelector("input").addEventListener("change", () => {
            if (selectedSources.includes(src)) {
              selectedSources = selectedSources.filter(s => s !== src);
            } else {
              selectedSources.push(src);
            }
            safeUpdate();
          });

          col.appendChild(label);
        });

        return col;
      };

      columnsContainer.appendChild(renderCategoryColumn(traditionalSources, "Traditional"));
      columnsContainer.appendChild(renderCategoryColumn(webSources, "New Media"));

      sourceFilters.appendChild(columnsContainer);

      const emotionsSet = new Set();
      allArticles.forEach(a => {
        if (Array.isArray(a.sentiment)) {
          a.sentiment.forEach(emo => emotionsSet.add(emo));
        } else {
          emotionsSet.add(a.sentiment);
        }
      });
      const emotions = [...emotionsSet];

      sentimentFilters.innerHTML = `<p class="filter-group-label" style="font-size:1.1rem; margin-top:20px; margin-bottom: 12px;">Sentiment</p>`;

      const allEmotionsSelected = emotions.length > 0 && selectedSentiments.length === emotions.length;
      const selectAllEmotions = document.createElement("label");
      selectAllEmotions.className = "filter-item";
      selectAllEmotions.style.fontWeight = "bold";
      selectAllEmotions.style.borderBottom = "1px solid var(--border-light)";
      selectAllEmotions.style.paddingBottom = "12px";
      selectAllEmotions.style.marginBottom = "12px";
      selectAllEmotions.innerHTML = `<input type="checkbox" ${allEmotionsSelected ? "checked" : ""} /><span>All Sentiments</span>`;

      selectAllEmotions.querySelector("input").addEventListener("change", (e) => {
        selectedSentiments = e.target.checked ? [...emotions] : [];
        safeUpdate();
      });
      sentimentFilters.appendChild(selectAllEmotions);

      emotions.forEach(s => {
        const label = document.createElement("label");
        label.className = "filter-item capitalize";
        label.innerHTML = `<input type="checkbox" ${selectedSentiments.includes(s) ? "checked" : ""}/><span>${s.toLowerCase()}</span>`;

        label.querySelector("input").addEventListener("change", () => {
          if (selectedSentiments.includes(s)) {
            selectedSentiments = selectedSentiments.filter(em => em !== s);
          } else {
            selectedSentiments.push(s);
          }
          safeUpdate();
        });
        sentimentFilters.appendChild(label);
      });
    }

    // ── Render Results ─────────────────────────────────────────────
    function renderResults() {
      const filtered = allArticles.filter(a =>
      selectedSources.includes(a.source) &&
      (Array.isArray(a.sentiment) ? a.sentiment.some(s => selectedSentiments.includes(s)) : selectedSentiments.includes(a.sentiment))
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

    // ── Result Card ────────────────────────────────────────────────
    function buildCard(article) {
      const NEGATIVE_EMOTIONS = new Set(["ANGER","ANNOYANCE","DISAPPOINTMENT","DISAPPROVAL","DISGUST","EMBARRASSMENT","FEAR","GRIEF","NERVOUSNESS","REMORSE","SADNESS"]);
      const POSITIVE_EMOTIONS = new Set(["ADMIRATION","AMUSEMENT","APPROVAL","CARING","DESIRE","EXCITEMENT","GRATITUDE","JOY","LOVE","OPTIMISM","PRIDE","RELIEF"]);

      const primarySentiment = Array.isArray(article.sentiment) ? article.sentiment[0] : article.sentiment;
      const valence = NEGATIVE_EMOTIONS.has(primarySentiment) ? "negative"
      : POSITIVE_EMOTIONS.has(primarySentiment) ? "positive"
      : "neutral";

      const badgeClass = { positive: "badge-positive", negative: "badge-negative", neutral: "badge-neutral" }[valence];
      const icon       = { positive: ICONS.thumbUp, negative: ICONS.thumbDown, neutral: ICONS.meh }[valence];
      const displaySentiment = Array.isArray(article.sentiment) ? article.sentiment.join(" / ") : article.sentiment;

      let headlineHTML = esc(article.headline);
      const headlineLower = article.headline.toLowerCase();

      article.actors.forEach(actor => {
        const actorLower = actor.name.toLowerCase();
        const actorIndex = headlineLower.indexOf(actorLower);

        if (actorIndex !== -1) {
          const actorText = article.headline.substring(actorIndex, actorIndex + actor.name.length);
          headlineHTML = headlineHTML.replace(
            new RegExp(`\\b${esc(actorText)}\\b`, 'gi'),
                                              `<mark class="headline-highlight">${esc(actorText)}</mark>`
          );
        }
      });

      const actorTags = article.actors.map(a =>
      `<span class="actor-tag">${esc(a.name)} <em class="actor-role"><span class="tooltip-wrapper" data-tooltip="${tagTooltip('agency', a.role)}">${esc(a.role)}</span></em></span>`
      ).join("");

      const focusTags = (article.focus || []).map(f =>
      `<span class="focus-tag"><span class="tooltip-wrapper" data-tooltip="${tagTooltip('focus', f)}">${esc(f)}</span></span>`
      ).join("");

      const urlLine = article.url ? `<div class="card-url"><a href="${esc(article.url)}" target="_blank" rel="noopener">Read original article ↗</a></div>` : "";

      const card = document.createElement("article");
      card.className = "result-card";
      card.innerHTML = `
      <div class="card-top">
      <div class="source-info">
      <div class="source-avatar">${esc(article.source.charAt(0))}</div>
      <span class="source-name">${esc(article.source)}</span>
      </div>
      <div class="sentiment-badge ${badgeClass}">${icon} ${displaySentiment}</div>
      </div>
      <h3 class="card-headline">${headlineHTML}</h3>

      <div class="analysis-tags">
      <span class="analysis-tag tag-frame">
      <span class="tooltip-wrapper" data-tooltip="${tagTooltip('frame', article.frame)}">
      Frame: ${esc(article.frame)}
      </span>
      </span>
      <span class="analysis-tag tag-genre">
      <span class="tooltip-wrapper" data-tooltip="${tagTooltip('genre', article.genre)}">
      Genre: ${esc(article.genre)}
      </span>
      </span>
      </div>

      <div class="card-meta">
      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px; margin-bottom: 8px; width: 100%;">
      ${article.actors.length > 0 ? `
        <div class="meta-actors" style="margin: 0; display: inline-flex; align-items: center;">
        ${ICONS.tags}
        <div class="actor-tags" style="display: flex; gap: 4px; flex-wrap: wrap; margin-left: 6px;">
        ${actorTags}
        </div>
        </div>` : ""}

        <div class="meta-biases-colored" style="display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap;">
        <span style="font-size: 12px; font-weight: bold; color: #475569;">Biases:</span>
        <div style="display: inline-flex; gap: 6px; flex-wrap: wrap;">
        ${buildBiasTags(article.biases)}
        </div>
        </div>
        </div>

        ${focusTags ? `<div class="meta-focus" style="margin-top: 4px;"><span class="meta-label">Focus:</span><div class="focus-tags">${focusTags}</div></div>` : ""}
        </div>

        ${urlLine}
        <div class="card-footer">${buildStarRating(article)}</div>
        `;
        return card;
    }

    // ── Tone Intensity Bar ─────────────────────────────────────────
    function buildStarRating(article) {
      const intensity = article.tone_intensity || 3;

      const colors = {
        1: "#10b981",
        2: "#84cc16",
        3: "#f59e0b",
        4: "#f97316",
        5: "#ef4444"
      };

      const barColor = colors[intensity] || "#f59e0b";
      const percentage = (intensity / 5) * 100;

      return `
      <div class="star-rating" style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
      <span class="rating-label tooltip-wrapper" data-tooltip="${TONE_INTENSITY_TOOLTIP}" style="white-space: nowrap;">Tone Intensity: ${intensity}/5</span>
      <div style="width: 80px; min-width: 180px; height: 8px; background-color: #e2e8f0; border-radius: 4px; overflow: hidden;">
      <div style="width: ${percentage}%; height: 100%; background-color: ${barColor}; border-radius: 4px;"></div>
      </div>
      </div>`;
    }

    // ── Build Colored Bias Tags ────────────────────────────────────
    function buildBiasTags(biasesObj) {
      if (!biasesObj || Object.keys(biasesObj).length === 0) {
        return '<span style="font-size: 12px; color: #64748b; font-style: italic;">No bias detected</span>';
      }

      return Object.entries(biasesObj).map(([bias, score]) => {
        let intensityLabel = 'Low';
        let color = '#3b82f6';

        if (score === 2) {
          intensityLabel = 'Med';
          color = '#f59e0b';
        } else if (score === 3) {
          intensityLabel = 'High';
          color = '#ef4444';
        }

        return `
        <span style="display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 12px; background-color: ${color}15; color: ${color}; font-size: 12px; font-weight: 600; border: 1px solid ${color}30;">
        ${bias} <span style="opacity: 0.7; margin-left: 4px; font-size: 10px;">(${intensityLabel})</span>
        </span>`;
      }).join('');
    }

    // ── Charts ─────────────────────────────────────────────────────
    function renderCharts(articles) {
      const primaryEmotionCounts = {};
      const secondaryEmotionCounts = {};

      articles.forEach(a => {
        let primary = "Unknown";
        let secondary = null;

        if (Array.isArray(a.sentiment)) {
          primary = (a.sentiment[0] || "Unknown").trim();
          if (a.sentiment.length > 1) {
            secondary = a.sentiment[1].trim();
          }
        } else {
          primary = (a.sentiment || "Unknown").trim();
        }

        primaryEmotionCounts[primary] = (primaryEmotionCounts[primary] || 0) + 1;
        if (secondary) {
          secondaryEmotionCounts[secondary] = (secondaryEmotionCounts[secondary] || 0) + 1;
        }
      });

      const emotionColorPalette = [
        "#4f46e5", "#10b981", "#f59e0b", "#f43f5e", "#64748b",
        "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16", "#f97316"
      ];

      const primaryLabels = Object.keys(primaryEmotionCounts);
      const primaryColors = primaryLabels.map((_, i) => emotionColorPalette[i % emotionColorPalette.length]);

      if (pieChart) pieChart.destroy();
      pieChart = new Chart(document.getElementById("pie-chart"), {
        type: "doughnut",
        data: {
          labels: primaryLabels,
          datasets: [{ data: Object.values(primaryEmotionCounts), backgroundColor: primaryColors, borderWidth: 0, hoverOffset: 6 }],
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: "65%",
          plugins: {
            legend: {
              position: "bottom", align: "start",
              labels: { usePointStyle: true, pointStyle: "circle", padding: 16, font: { family: "'DM Sans'", size: 12 }, color: "#717182" },
            },
          },
        },
      });

      const secondaryLabels = Object.keys(secondaryEmotionCounts);
      const secondaryColors = secondaryLabels.map((_, i) => emotionColorPalette[(i + 3) % emotionColorPalette.length]);

      if (secondaryEmotionChart) secondaryEmotionChart.destroy();

      const secCanvas = document.getElementById("secondary-emotion-chart");
      if (secCanvas && secondaryLabels.length > 0) {
        secondaryEmotionChart = new Chart(secCanvas, {
          type: "doughnut",
          data: {
            labels: secondaryLabels,
            datasets: [{ data: Object.values(secondaryEmotionCounts), backgroundColor: secondaryColors, borderWidth: 0, hoverOffset: 6 }],
          },
          options: {
            responsive: true, maintainAspectRatio: false, cutout: "65%",
            plugins: {
              legend: {
                position: "bottom", align: "start",
                labels: { usePointStyle: true, pointStyle: "circle", padding: 16, font: { family: "'DM Sans'", size: 12 }, color: "#717182" },
              },
            },
          },
        });
      }

      const genreCounts = {};
      articles.forEach(a => {
        const g = (a.genre || "Unknown").trim();
        genreCounts[g] = (genreCounts[g] || 0) + 1;
      });

      const genreColorPalette = [
        "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16", "#f97316",
        "#4f46e5", "#10b981", "#f59e0b", "#f43f5e", "#64748b"
      ];
      const genreLabels = Object.keys(genreCounts);
      const genreColors = genreLabels.map((_, i) => genreColorPalette[i % genreColorPalette.length]);

      if (genreChart) genreChart.destroy();
      genreChart = new Chart(document.getElementById("genre-chart"), {
        type: "doughnut",
        data: {
          labels: genreLabels,
          datasets: [{ data: Object.values(genreCounts), backgroundColor: genreColors, borderWidth: 0, hoverOffset: 6 }],
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: "65%",
          plugins: {
            legend: {
              position: "bottom", align: "start",
              labels: { usePointStyle: true, pointStyle: "circle", padding: 16, font: { family: "'DM Sans'", size: 12 }, color: "#717182" },
            },
          },
        },
      });

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
          responsive: true, maintainAspectRatio: false,
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
      articles.forEach(a => a.actors.forEach(actor => { const key = actor.name || actor; counts[key] = (counts[key] || 0) + 1; }));
      const top = Object.entries(counts).sort((a,b) => b[1]-a[1]).slice(0, 5);

      document.getElementById("actors-list").innerHTML = top.length > 0
      ? top.map(([actor, count]) => `<div class="actor-chip">${esc(actor)}<span class="actor-chip-count">${count}</span></div>`).join("")
      : `<p style="font-size:.85rem;color:var(--text-400)">No actors identified yet.</p>`;
    }

    // ── Global Feedback Form ───────────────────────────────────────
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

    // ── Event Listeners ────────────────────────────────────────────

    // 1. Click main research button
    document.getElementById("main-search-btn").addEventListener("click", () => {
      const country = document.getElementById("main-country-select").value;
      const engine = document.getElementById("main-engine-select").value;
      handleSearch(mainSearchInput.value, country, engine);
    });

    mainSearchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const country = document.getElementById("main-country-select").value;
        const engine = document.getElementById("main-engine-select").value;
        handleSearch(mainSearchInput.value, country, engine);
      }
    });

    // 2. Click inline search button
    document.getElementById("inline-search-btn").addEventListener("click", () => {
      const country = document.getElementById("inline-country-select").value;
      const engine = document.getElementById("inline-engine-select").value;
      handleSearch(inlineSearchInput.value, country, engine);
    });
        inlineSearchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const country = document.getElementById("inline-country-select").value;
        const engine = document.getElementById("inline-engine-select").value;
        handleSearch(inlineSearchInput.value, country, engine);
      }
    });


    // ── Utility ────────────────────────────────────────────────────
    function esc(str) {
      return String(str || "")
      .replace(/&/g,"&amp;").replace(/</g,"&lt;")
      .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    }

    // ── Trending Topics ────────────────────────────────────────────
    async function loadTrending() {
      try {
        const res  = await fetch("/api/analytics-data");
        if (!res.ok) return;
        const data = await res.json();

        const stats  = data.topic_stats || [];
        const sorted = [...stats].sort((a, b) => (b.count || 0) - (a.count || 0)).slice(0, 6);
        const list   = document.getElementById("trending-list");
        if (!list || sorted.length === 0) return;

        sorted.forEach(t => {
          const chip = document.createElement("button");
          chip.className   = "trending-chip";
          chip.textContent = t.event_query;
          chip.addEventListener("click", () => handleSearch(t.event_query));
          list.appendChild(chip);
        });
      } catch(e) {
        // Silently fail if analytics are not available
      }
    }

    loadTrending();
