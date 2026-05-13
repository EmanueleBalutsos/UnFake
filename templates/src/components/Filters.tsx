import { Filter } from "lucide-react";
import "./Filters.css";

interface FiltersProps {
  sources: string[];
  sentiments: string[];
  selectedSources: string[];
  selectedSentiments: string[];
  onToggleSource: (source: string) => void;
  onToggleSentiment: (sentiment: string) => void;
}

export function Filters({
  sources,
  sentiments,
  selectedSources,
  selectedSentiments,
  onToggleSource,
  onToggleSentiment,
}: FiltersProps) {
  return (
    <aside className="filters-panel">
      <div className="filters-title">
        <Filter size={16} />
        Filters
      </div>

      <div className="filter-group">
        <p className="filter-group-label">Source</p>
        {sources.map((source) => (
          <label key={source} className="filter-item">
            <input
              type="checkbox"
              checked={selectedSources.includes(source)}
              onChange={() => onToggleSource(source)}
            />
            <span title={source}>{source}</span>
          </label>
        ))}
      </div>

      <div className="filter-group">
        <p className="filter-group-label">Sentiment</p>
        {sentiments.map((sentiment) => (
          <label key={sentiment} className="filter-item capitalize">
            <input
              type="checkbox"
              checked={selectedSentiments.includes(sentiment)}
              onChange={() => onToggleSentiment(sentiment)}
            />
            <span>{sentiment}</span>
          </label>
        ))}
      </div>
    </aside>
  );
}
