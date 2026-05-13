import { Search, Loader2 } from "lucide-react";
import "./SearchSection.css";

interface SearchSectionProps {
  onSearch: (query: string) => void;
  isSearching: boolean;
}

export function SearchSection({ onSearch, isSearching }: SearchSectionProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const query = (formData.get("query") as string).trim();
    if (query) onSearch(query);
  };

  return (
    <section className="search-section">
      <h1 className="search-title">Analyze the Narrative</h1>
      <p className="search-subtitle">
        See how different media outlets frame the same news event. Uncover bias,
        emotional tone, and hidden agendas.
      </p>

      <form className="search-bar" onSubmit={handleSubmit}>
        <span className="search-icon" aria-hidden>
          <Search size={20} />
        </span>
        <input
          type="text"
          name="query"
          placeholder="Search an event or paste a news URL…"
          //defaultValue="Global Climate Summit 2026"
          autoComplete="off"
        />
        <button type="submit" disabled={isSearching}>
          {isSearching ? <Loader2 size={18} className="spin" /> : "Analyze"}
        </button>
      </form>
    </section>
  );
}
