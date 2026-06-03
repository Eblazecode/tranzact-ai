import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Sparkles, Menu, X } from "lucide-react";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "nav-frosted bg-background/90 shadow-sm border-b border-border"
          : "bg-transparent"
      }`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <span className={`text-xl font-bold ${scrolled ? "text-foreground" : "text-white"}`}>
              Transac<span className="text-primary">AI</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {["Home", "Features", "How It Works"].map((label) => (
              <a
                key={label}
                href={`#${label.toLowerCase().replace(/ /g, "-")}`}
                className={`text-sm font-medium transition-colors px-2 py-1 ${
                  scrolled
                    ? "text-muted-foreground hover:text-foreground"
                    : "text-white/70 hover:text-white"
                }`}
              >
                {label}
              </a>
            ))}
            <Link
              to="/login"
              className={`text-sm font-medium transition-colors ${
                scrolled
                  ? "text-muted-foreground hover:text-foreground"
                  : "text-white/70 hover:text-white"
              }`}
            >
              Log in
            </Link>
            <Link to="/signup">
              <Button variant="hero" size="sm" className="px-5">
                Get Started Free
              </Button>
            </Link>
          </div>

          <button
            className={`md:hidden ${scrolled ? "text-foreground" : "text-white"}`}
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-4 flex flex-col gap-3 bg-background/95 nav-frosted rounded-b-xl px-2 mt-2">
            {["Home", "Features", "How It Works"].map((label) => (
              <a
                key={label}
                href={`#${label.toLowerCase().replace(/ /g, "-")}`}
                className="text-sm font-medium text-muted-foreground hover:text-foreground px-2 py-2"
                onClick={() => setMobileOpen(false)}
              >
                {label}
              </a>
            ))}
            <Link
              to="/login"
              className="text-sm font-medium text-muted-foreground hover:text-foreground px-2 py-2"
              onClick={() => setMobileOpen(false)}
            >
              Log in
            </Link>
            <Link to="/signup" onClick={() => setMobileOpen(false)}>
              <Button variant="hero" size="lg" className="w-full">
                Get Started Free
              </Button>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
