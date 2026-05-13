import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { type Article } from "../types";
import "./AnalysisSection.css";

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "#10b981",
  neutral:  "#64748b",
  negative: "#f43f5e",
};

interface AnalysisSectionProps {
  articles: Article[];
}

export function AnalysisSection({ articles }: AnalysisSectionProps) {
  // Sentiment pie data
  const sentimentCounts = articles.reduce<Record<string, number>>((acc, a) => {
    acc[a.sentiment] = (acc[a.sentiment] ?? 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(sentimentCounts).map(([name, value]) => ({
    name,
    value,
    color: SENTIMENT_COLORS[name] ?? "#a0a0b0",
  }));

  // Source bar data
  const sourceCounts = articles.reduce<Record<string, number>>((acc, a) => {
    acc[a.source] = (acc[a.source] ?? 0) + 1;
    return acc;
  }, {});

  const barData = Object.entries(sourceCounts).map(([name, count]) => ({ name, count }));

  // Top actors
  const actorCounts = articles.reduce<Record<string, number>>((acc, a) => {
    a.actors.forEach((actor) => { acc[actor] = (acc[actor] ?? 0) + 1; });
    return acc;
  }, {});

  const topActors = Object.entries(actorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="analysis-col">
      {/* Sentiment pie */}
      <div className="analysis-card">
        <h4 className="analysis-card-title">Sentiment Distribution</h4>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%" cy="50%"
                innerRadius={60} outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: 8, border: "1px solid #e5e5e5", boxShadow: "0 4px 6px -1px rgb(0 0 0/.1)" }}
                itemStyle={{ color: "#333", fontSize: 13 }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Source bar */}
      <div className="analysis-card">
        <h4 className="analysis-card-title">Coverage by Source</h4>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e9e9ed" />
              <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#717182" }} />
              <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#717182" }} allowDecimals={false} />
              <Tooltip
                cursor={{ fill: "#f4f4f6" }}
                contentStyle={{ borderRadius: 8, border: "1px solid #e5e5e5", boxShadow: "0 4px 6px -1px rgb(0 0 0/.1)" }}
              />
              <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top actors */}
      <div className="analysis-card">
        <h4 className="analysis-card-title">Top Actors Identified</h4>
        <div className="actors-list">
          {topActors.map(([actor, count]) => (
            <div key={actor} className="actor-chip">
              {actor}
              <span className="actor-chip-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
