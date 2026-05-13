import { useState } from "react";
import "./StarRating.css";

interface StarRatingProps {
  articleId: string;
  onRate: (articleId: string, stars: number) => void;
}

export function StarRating({ articleId, onRate }: StarRatingProps) {
  const [hovered, setHovered] = useState(0);
  const [rated, setRated]     = useState(0);

  const handleClick = (stars: number) => {
    setRated(stars);
    onRate(articleId, stars);   // ← this is where you call your backend
  };

  if (rated > 0) {
    return <p className="rating-done">Thanks! Rated {rated}/5 — saved.</p>;
  }

  return (
    <div className="star-rating">
      <span className="rating-label">Was this analysis accurate or neutral ? (1: Biased ; 5: Neutral)</span>
      <div className="stars">
        {[1,2,3,4,5].map(n => (
          <span
            key={n}
            className={`star ${n <= (hovered || rated) ? "filled" : ""}`}
            onMouseEnter={() => setHovered(n)}
            onMouseLeave={() => setHovered(0)}
            onClick={() => handleClick(n)}
          >★</span>
        ))}
      </div>
    </div>
  );
}