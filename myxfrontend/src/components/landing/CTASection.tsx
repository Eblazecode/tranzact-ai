import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-24 px-4 bg-primary">
      <div className="mx-auto max-w-4xl text-center">
        <div className="flex items-center justify-center gap-2 mb-6">
          <Sparkles className="h-5 w-5 text-primary-foreground/80" />
          <span className="text-sm font-semibold uppercase tracking-widest text-primary-foreground/80">
            Get Started Today
          </span>
        </div>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-primary-foreground mb-6">
          Ready to understand your finances?
        </h2>
        <p className="text-lg text-primary-foreground/80 mb-10 max-w-xl mx-auto">
          Join thousands of Nigerians who are taking control of their money with
          AI-powered insights. It's free to get started.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/signup">
            <Button
              size="lg"
              className="text-base px-8 py-6 gap-2 bg-white text-primary hover:bg-white/90 font-semibold min-w-[200px] transition-all duration-200 hover:scale-[1.03]"
            >
              Get Started Free <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link to="/login">
            <Button
              size="lg"
              className="text-base px-8 py-6 border border-primary-foreground/30 text-primary-foreground bg-transparent hover:bg-primary-foreground/10 hover:text-primary-foreground min-w-[200px] transition-all duration-200 hover:scale-[1.03]"
            >
              See a Demo
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
