import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import heroBg from "@/assets/hero-bg.jpg";

const rotatingWords = ["analyse", "predict", "understand", "optimise", "grow"];

export function HeroSection() {
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((i) => (i + 1) % rotatingWords.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
      <div className="absolute inset-0">
        <img src={heroBg} alt="" className="w-full h-full object-cover" width={1920} height={1080} />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-black/70" />
      </div>

      <div className="relative z-10 mx-auto max-w-4xl w-full px-4 sm:px-6 lg:px-8 text-center pt-32 pb-24">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary mb-6 animate-fade-up">
          Financial Intelligence Platform
        </p>

        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-[1.08] mb-8">
          Where Nigerians{" "}
          <br className="hidden sm:block" />
          go to{" "}
          <span className="relative inline-block min-w-[180px] sm:min-w-[260px]">
            <span
              key={wordIndex}
              className="text-primary inline-block"
              style={{ animation: "word-fade-in 2.5s ease forwards" }}
            >
              {rotatingWords[wordIndex]}
            </span>
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload your bank statement. Get a complete financial picture with
          AI-powered insights, predictions, and personalised recommendations —
          in under 60 seconds.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/signup">
            <Button
              variant="hero"
              size="lg"
              className="text-base px-8 py-6 gap-2 min-w-[200px] transition-all duration-200 hover:scale-[1.03] hover:brightness-110"
            >
              Get Started <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link to="/login">
            <Button
              size="lg"
              className="text-base px-8 py-6 border border-white/30 text-white bg-transparent hover:bg-white/10 hover:text-white min-w-[200px] font-semibold transition-all duration-200 hover:scale-[1.03]"
            >
              See How It Works
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
