import { Search } from "lucide-react";
import "./Header.css";

export function Header() {
  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="logo">
          <div className="logo-icon">
            <Search size={20} />
          </div>
          <span className="logo-name">UnFake</span>
        </div>
        <nav className="header-nav">
          <a href="#" className="nav-link active">Home</a>
          <a href="#" className="nav-link">Analysis</a>
          <a href="#" className="nav-link">About</a>
        </nav>
      </div>
    </header>
  );
}
