import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sparkles, Eye, EyeOff, Loader2 } from "lucide-react";
import { canUseBrowserSession, createSession } from "@/lib/auth";
import { api } from "@/lib/api";

export const Route = createFileRoute("/login")({
  beforeLoad: () => {
    // Always show login page, don't auto-redirect
    if (!canUseBrowserSession()) {
      return;
    }
  },
  head: () => ({
    meta: [
      { title: "Log In - TransacAI" },
      { name: "description", content: "Log in to your TransacAI dashboard." },
      { property: "og:title", content: "Log In - TransacAI" },
      { property: "og:description", content: "Access your financial intelligence dashboard." },
    ],
  }),
  component: LoginPage,
});

function DecorativeBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden opacity-20">
      <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid-login" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" opacity="0.3" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid-login)" />
        <polyline points="0,250 100,230 200,260 300,200 400,220 500,170 600,190" fill="none" stroke="white" strokeWidth="2" opacity="0.4" />
        {[80, 180, 280, 380, 480].map((x, i) => (
          <rect key={i} x={x} y={380 - (i + 1) * 25} width="20" height={(i + 1) * 25} fill="white" opacity="0.15" rx="2" />
        ))}
      </svg>
      <div className="absolute inset-0 backdrop-blur-[2px]" />
    </div>
  );
}

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await api.login({
        email: email.trim(),
        password,
      });

      createSession(response.user.first_name, response.user.email, response.access_token);
      navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hero-gradient relative hidden w-[45%] flex-col justify-between p-12 lg:flex">
        <DecorativeBackground />
        <div className="relative z-10 flex flex-1 flex-col justify-center">
          <h1 className="mb-4 text-4xl font-bold leading-tight text-primary-foreground xl:text-5xl">
            Welcome back
          </h1>
          <p className="text-xl text-primary-foreground/80">
            Your financial intelligence is waiting
          </p>
        </div>
        <div className="relative z-10 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary-foreground" />
          <span className="text-lg font-bold text-primary-foreground">TransacAI</span>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center bg-background p-6 sm:p-12 lg:w-[55%]">
        <div className="w-full max-w-md">
          <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
            <h2 className="mb-1 text-2xl font-bold text-card-foreground">Welcome back</h2>
            <p className="mb-6 text-sm text-muted-foreground">Log in to your TransacAI dashboard</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required className="mt-1" />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative mt-1">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="--------"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <div className="mt-1 text-right">
                  <button type="button" className="text-xs text-primary hover:underline">Forgot password?</button>
                </div>
              </div>
              <Button type="submit" disabled={loading} className="w-full rounded-lg bg-primary text-primary-foreground hover:brightness-110">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Log In"}
              </Button>
            </form>

            {error ? (
              <p className="mt-4 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            ) : null}

            <p className="mt-4 text-center text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link to="/signup" className="font-medium text-primary hover:underline">Sign up</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
