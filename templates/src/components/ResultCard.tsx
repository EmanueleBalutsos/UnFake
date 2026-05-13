import { Tags, Brain, Meh, ThumbsDown, ThumbsUp } from "lucide-react";
import { type Article } from "../types";
import "./ResultCard.css";
import { StarRating } from "./StarRating";

const sentimentClass = {
  positive: "badge-positive",
  negative: "badge-negative",
  neutral:  "badge-neutral",
} as const;

const SentimentIcon = ({ sentiment }: { sentiment: Article["sentiment"] }) => {
  if (sentiment === "positive") return <ThumbsUp  size={12} />;
  if (sentiment === "negative") return <ThumbsDown size={12} />;
  return <Meh size={12} />;
};

export function ResultCard({ article }: { article: Article }) {
  const handleRate = async (_articleId: string, stars: number) => {
  await fetch("http://localhost:5000/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event:   article.headline,
      rating:  stars,
      comment: "",
    }),
  });
};
  // Highlight the key phrase inside the headline
  const idx = article.headline.indexOf(article.firstWord);
  const headline =
    idx !== -1 ? (
      <>
        {article.headline.slice(0, idx)}
        <mark className="headline-highlight">{article.firstWord}</mark>
        {article.headline.slice(idx + article.firstWord.length)}
      </>
    ) : (
      article.headline
    );

  return (
    <article className="result-card">
      {/* Source + sentiment badge */}
      <div className="card-top">
        <div className="source-info">
          <div className="source-avatar">{article.source.charAt(0)}</div>
          <span className="source-name">{article.source}</span>
        </div>
        <div className={`sentiment-badge ${sentimentClass[article.sentiment]}`}>
          <SentimentIcon sentiment={article.sentiment} />
          {article.sentiment}
        </div>
      </div>

      {/* Headline */}
      <h3 className="card-headline">{headline}</h3>

      {/* Actors + tone */}
      <div className="card-meta">
        {article.actors.length > 0 && (
          <div className="meta-actors">
            <Tags size={13} className="meta-icon" />
            <div className="actor-tags">
              {article.actors.map((actor) => (
                <span key={actor} className="actor-tag">{actor}</span>
              ))}
            </div>
          </div>
        )}
        <div className="meta-tone">
          <Brain size={13} className="meta-icon" />
          <span>Tone: {article.tone}</span>
        </div>
      </div>
      <div className="card-footer">
        <StarRating articleId={article.id} onRate={handleRate} />
      </div>
    </article>
  );
}
