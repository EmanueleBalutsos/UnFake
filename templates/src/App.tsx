import { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { SearchSection } from "./components/SearchSection";
import { ResultCard } from "./components/ResultCard";
import { AnalysisSection } from "./components/AnalysisSection";
import { Filters } from "./components/Filters";
import { type Article } from "./types";
import "./styles/App.css";

const API_URL = "http://localhost:5000";

const ALL_SENTIMENTS = ["positive", "neutral", "negative"];

export default function App() {
  const [query, setQuery] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derive sources dynamically from the actual fetched articles
  const availableSources = Array.from(new Set(articles.map((a) => a.source)));

  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedSentiments, setSelectedSentiments] = useState<string[]>(ALL_SENTIMENTS);

  // Automatically select all new sources when articles are loaded
  useEffect(() => {
    setSelectedSources(availableSources);
  }, [articles]);

  // --- GLOBAL FEEDBACK STATES ---
  const [feedbackRating, setFeedbackRating] = useState<number | null>(null);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setQuery(searchQuery);
    setIsSearching(true);
    setError(null);
    setFeedbackSent(false);
    setFeedbackRating(null);
    setFeedbackComment("");

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: searchQuery }),
      });

      if (!response.ok) throw new Error("Search failed");

      const data = await response.json();

      // ── NORMALIZZAZIONE DATI ──
      // Adattiamo i dati del backend (title) a quelli che React si aspetta (headline, etc.)
      // fornendo dei valori di default (fallback) per evitare crash.
      const safeArticles = (data.articles || []).map((a: any, index: number) => ({
        ...a,
        id: a.url || String(index),                     // Assicura che ci sia un ID univoco
                                                                                 headline: a.title || a.headline || "No Title",  // Mappa 'title' del backend in 'headline'
                                                                                 source: a.source || "Unknown Source",
                                                                                 sentiment: a.sentiment || "neutral",            // Fallback per il sentiment
                                                                                 actors: a.actors || [],                         // Evita crash se actors è undefined
                                                                                 tone: a.tone || "Neutral",
      }));

      setArticles(safeArticles);

    } catch (err) {
      console.error("Search error:", err);
      setError("An error occurred during the search. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleGlobalFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query || feedbackRating === null) return;

    // Detect browser language
    const browserLang = navigator.language.split('-')[0] || "en";

    try {
      const response = await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: query,
          rating: feedbackRating,
          comment: feedbackComment,
          language: browserLang,
        }),
      });

      if (response.ok) {
        setFeedbackSent(true);
      }
    } catch (err) {
      console.error("Feedback error:", err);
    }
  };

  const handleToggleSource = (src: string) => {
    setSelectedSources((prev) =>
    prev.includes(src) ? prev.filter((s) => s !== src) : [...prev, src]
    );
  };

  const handleToggleSentiment = (sent: string) => {
    setSelectedSentiments((prev) =>
    prev.includes(sent) ? prev.filter((s) => s !== sent) : [...prev, sent]
    );
  };

  // Filter the data based on UI selections
  const filteredData = articles.filter(
    (a) =>
    selectedSources.includes(a.source) &&
    (a.sentiment ? selectedSentiments.includes(a.sentiment) : true)
  );

  return (
    <div className="app-root">
    <Header />
    <main className="main-container">
    {!query && !isSearching ? (
      <SearchSection onSearch={handleSearch} isSearching={isSearching} />
    ) : (
      <div className="results-wrapper">
      <div className="results-topbar">
      <div>
      <h1 className="results-title">Analysis Results</h1>
      <p className="results-subtitle">
      Showing results for: <strong>{query}</strong>
      </p>
      </div>
      <form
      className="inline-search"
      onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        handleSearch(formData.get("query") as string);
      }}
      >
      <button type="submit" disabled={isSearching}>
      {isSearching ? "Searching..." : "Search"}
      </button>
      </form>
      </div>

      {error && <p className="error-message">{error}</p>}

      <div className="results-grid">
      <Filters
      sources={availableSources}
      sentiments={ALL_SENTIMENTS}
      selectedSources={selectedSources}
      selectedSentiments={selectedSentiments}
      onToggleSource={handleToggleSource}
      onToggleSentiment={handleToggleSentiment}
      />

      <div className="headlines-col">
      <h2 className="headlines-count">
      Headlines ({filteredData.length})
      </h2>
      {filteredData.length > 0 ? (
        filteredData.map((article, idx) => (
          <ResultCard key={article.id || idx} article={article} />
        ))
      ) : (
        !isSearching && (
          <p className="no-results">
          No articles match your selected filters.
          </p>
        )
      )}
      </div>

      {filteredData.length > 0 && (
        <AnalysisSection articles={filteredData} />
      )}
      </div>

      {/* ── GLOBAL FEEDBACK SECTION ── */}
      {!isSearching && query && (
        <div className="global-feedback-card">
        <h3>What do you think about these results?</h3>
        {feedbackSent ? (
          <div className="feedback-success">
          <p>Thank you! Your feedback has been saved successfully. ✅</p>
          </div>
        ) : (
          <form onSubmit={handleGlobalFeedback} className="feedback-form">
          <div className="rating-group">
          <label>Rate your experience (1-10):</label>
          <div className="rating-buttons">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
            <button
            key={num}
            type="button"
            className={feedbackRating === num ? "active" : ""}
            onClick={() => setFeedbackRating(num)}
            >
            {num}
            </button>
          ))}
          </div>
          </div>

          <div className="comment-group">
          <label>Leave a comment (optional):</label>
          <textarea
          rows={3}
          placeholder="Tell us what you think..."
          value={feedbackComment}
          onChange={(e) => setFeedbackComment(e.target.value)}
          />
          </div>

          <button
          type="submit"
          className="submit-feedback-btn"
          disabled={feedbackRating === null}
          >
          Submit Feedback
          </button>
          </form>
        )}
        </div>
      )}
      </div>
    )}
    </main>
    </div>
  );
}
