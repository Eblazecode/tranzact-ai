import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles, Check, Loader2, Eye, EyeOff } from "lucide-react";
import { canUseBrowserSession, createSession } from "@/lib/auth";
import { api } from "@/lib/api";

export const Route = createFileRoute("/signup")({
  beforeLoad: () => {
    // Always show signup page, don't auto-redirect
    if (!canUseBrowserSession()) {
      return;
    }
  },
  head: () => ({
    meta: [
      { title: "Sign Up - TransacAI" },
      { name: "description", content: "Create your TransacAI account and get AI-powered financial insights." },
      { property: "og:title", content: "Sign Up - TransacAI" },
      { property: "og:description", content: "Create your TransacAI account." },
    ],
  }),
  component: SignupPage,
});

function getPasswordStrength(password: string): { label: string; level: number } {
  if (password.length === 0) return { label: "", level: 0 };
  if (password.length < 6) return { label: "Weak", level: 1 };
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  const score = [hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
  if (password.length >= 8 && score >= 3) return { label: "Strong", level: 3 };
  if (password.length >= 6 && score >= 2) return { label: "Medium", level: 2 };
  return { label: "Weak", level: 1 };
}

function DecorativeBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden opacity-20">
      <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" opacity="0.3" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        <polyline points="0,300 80,280 160,310 240,250 320,270 400,220 480,240 560,180 640,200" fill="none" stroke="white" strokeWidth="2" opacity="0.4" />
        <polyline points="0,350 80,340 160,360 240,320 320,330 400,290 480,310 560,260 640,280" fill="none" stroke="white" strokeWidth="1.5" opacity="0.2" />
        {[100, 200, 300, 400, 500].map((x, i) => (
          <rect key={i} x={x} y={400 - (i + 1) * 30} width="20" height={(i + 1) * 30} fill="white" opacity="0.15" rx="2" />
        ))}
      </svg>
      <div className="absolute inset-0 backdrop-blur-[2px]" />
    </div>
  );
}

function SignupPage() {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const strength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreed || password !== confirmPassword) {
      setError(password !== confirmPassword ? "Passwords do not match." : "You need to accept the terms first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.register({
        first_name: firstName.trim(),
        email: email.trim(),
        password,
      });

      createSession(response.user.first_name, response.user.email, response.access_token);
      navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hero-gradient relative hidden w-[45%] flex-col justify-between p-12 lg:flex">
        <DecorativeBackground />
        <div className="relative z-10 flex flex-1 flex-col justify-center">
          <h1 className="mb-8 text-4xl font-bold leading-tight text-primary-foreground xl:text-5xl">
            Turn your statement
            <br />
            into strategy
          </h1>
          <div className="space-y-4">
            {[
              "10+ financial insights per upload",
              "AI-powered spending predictions",
              "Supports OPay, GTBank, Moniepoint & more",
            ].map((text) => (
              <div key={text} className="flex items-center gap-3">
                <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary-foreground/20">
                  <Check className="h-4 w-4 text-primary-foreground" />
                </div>
                <span className="text-lg text-primary-foreground/90">{text}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="relative z-10 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary-foreground" />
          <span className="text-lg font-bold text-primary-foreground">TransacAI</span>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center bg-background p-6 sm:p-12 lg:w-[55%]">
        <div className="w-full max-w-md">
          <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
            <h2 className="mb-1 text-2xl font-bold text-card-foreground">Create your account</h2>
            <p className="mb-6 text-sm text-muted-foreground">Understand your money in under 60 seconds</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input id="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="Oluwapelumi" required className="mt-1" />
              </div>
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required className="mt-1" />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative mt-1">
                  <Input id="password" type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="--------" required />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground">
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {password.length > 0 && (
                  <div className="mt-2">
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full transition-all duration-300"
                        style={{
                          width: `${(strength.level / 3) * 100}%`,
                          backgroundColor:
                            strength.level === 1 ? "var(--destructive)" :
                            strength.level === 2 ? "#f59e0b" :
                            "var(--primary)",
                        }}
                      />
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{strength.label}</p>
                  </div>
                )}
              </div>
              <div>
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <div className="relative mt-1">
                  <Input id="confirmPassword" type={showConfirmPassword ? "text" : "password"} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="--------" required />
                  <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground">
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox id="terms" checked={agreed} onCheckedChange={(v) => setAgreed(v === true)} className="data-[state=checked]:border-primary data-[state=checked]:bg-primary" />
                <Label htmlFor="terms" className="cursor-pointer text-sm font-normal text-muted-foreground">
                  I agree to the Terms of Service
                </Label>
              </div>
              <Button type="submit" disabled={loading || !agreed} className="w-full rounded-lg bg-primary text-primary-foreground hover:brightness-110">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create Account"}
              </Button>
            </form>

            {error ? (
              <p className="mt-4 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            ) : null}

            <p className="mt-4 text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link to="/login" className="font-medium text-primary hover:underline">Log in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
