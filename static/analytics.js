console.log("🚀 analytics.js: File caricato correttamente (Versione UI Pro)!");

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics-data');
        if (!response.ok) throw new Error("Errore HTTP");

        const data = await response.json();
        document.getElementById('avg-rating').innerText = (data.average_rating || 0) + "/10";
        document.getElementById('total-feedbacks').innerText = data.total || 0;

        const leaderboard = document.getElementById('leaderboard-list');
        if (leaderboard) {
            leaderboard.innerHTML = "";
            const stats = data.topic_stats || [];
            const sorted = [...stats].sort((a, b) => (b.count || 0) - (a.count || 0)).slice(0, 5);

            if (sorted.length === 0) {
                leaderboard.innerHTML = "<p style='color: var(--text-400);'>Nessun dato presente.</p>";
            } else {
                sorted.forEach((t, i) => {
                    const medals = ["🥇", "🥈", "🥉"];
                    const medalDisplay = medals[i] || `<span style="color: #9ca3af; font-size: 1.1rem; font-weight: 800;">#${i+1}</span>`;

                    const row = document.createElement('div');
                    row.style.display = "flex";
                    row.style.alignItems = "center";
                    row.style.width = "100%";
                    row.style.maxWidth = "600px";
                    row.style.padding = "14px 20px";
                    row.style.margin = "6px 0";
                    row.style.background = "#ffffff";
                    row.style.borderRadius = "12px";
                    row.style.border = "1px solid #e5e7eb";
                    row.style.boxShadow = "0 2px 4px rgba(0,0,0,0.02)";

                    row.innerHTML = `
                    <div style="width: 45px; text-align: center; font-size: 1.5rem; margin-right: 15px; flex-shrink: 0;">
                    ${medalDisplay}
                    </div>

                    <div style="flex: 1; text-align: left; font-weight: 700; font-size: 1.1rem; color: #111827; text-transform: capitalize; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    ${t.event_query}
                    </div>

                    <div style="background: #eef2ff; color: #4338ca; font-weight: 700; font-size: 0.85rem; padding: 6px 14px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; margin-left: 15px;">
                    ${t.count} searches
                    </div>
                    `;
                    leaderboard.appendChild(row);
                });
            }
        }

        const reviewList = document.getElementById('top-reviews-list');
        if (reviewList) {
            reviewList.innerHTML = "";
            const reviews = data.top_reviews || [];

            if (reviews.length === 0) {
                reviewList.innerHTML = "<p style='color: var(--text-400);'>Nessuna recensione a 5 stelle trovata.</p>";
            } else {
                reviews.forEach(r => {
                    const card = document.createElement('div');
                    card.style.display = "flex";
                    card.style.flexDirection = "column";
                    card.style.alignItems = "center";
                    card.style.width = "100%";
                    card.style.maxWidth = "650px";
                    card.style.padding = "24px";
                    card.style.margin = "10px 0";
                    card.style.background = "rgba(79, 70, 229, 0.03)";
                    card.style.border = "1px solid #e0e7ff";
                    card.style.borderRadius = "16px";

                    card.innerHTML = `
                    <div style="display: inline-flex; align-items: center; justify-content: center; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 6px 16px; border-radius: 30px; margin-bottom: 15px;">
                    <span style="color: #047857; font-weight: 800; font-size: 0.9rem; letter-spacing: 0.5px;">RATING: ${r.rating}/10 ⭐</span>
                    <span style="color: #065f46; font-size: 0.9rem; border-left: 2px solid #a7f3d0; padding-left: 12px; margin-left: 12px; font-weight: 500;">su "${r.event_query}"</span>
                    </div>
                    <p style="font-size: 1.15rem; color: #1f2937; font-style: italic; margin: 0; line-height: 1.6; text-align: center; max-width: 95%;">
                    "${r.comment}"
                    </p>
                    `;
                    reviewList.appendChild(card);
                });
            }
        }

    } catch (err) {
        console.error("🚨 Errore JS:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadAnalytics);
