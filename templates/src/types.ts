export type Sentiment = "positive" | "negative" | "neutral";

export type Article = {
  id: string;
  headline: string;
  source: string;
  sentiment: Sentiment;
  actors: string[];
  tone: string;
  /** The phrase to highlight inside the headline */
  firstWord: string;
};
