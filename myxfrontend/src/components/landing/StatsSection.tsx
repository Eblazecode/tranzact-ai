import { useEffect, useRef, useState } from "react";

const stats = [
  { value: 5, suffix: "", label: "Banks Supported", description: "GTBank, OPay, Moniepoint, Zenith, Ecobank" },
  { value: 11, suffix: "+", label: "Insight Modules", description: "From category breakdowns to anomaly detection" },
  { value: 6, suffix: "", label: "AI Recommendations", description: "Personalised actions ranked by impact" },
  { value: 60, suffix: "s", label: "Processing Time", description: "Upload to full dashboard in under a minute" },
];

function Counter({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          let current = 0;
          const step = Math.ceil(target / 30);
          const timer = setInterval(() => {
            current += step;
            if (current >= target) {
              setCount(target);
              clearInterval(timer);
            } else {
              setCount(current);
            }
          }, 40);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);

  return (
    <div ref={ref} className="text-5xl sm:text-6xl font-bold text-primary">
      {count}
      {suffix}
    </div>
  );
}

export function StatsSection() {
  return (
    <section className="py-24 bg-background border-y border-border">
      <div className="mx-auto max-w-7xl px-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-10">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <Counter target={s.value} suffix={s.suffix} />
              <p className="text-lg font-semibold text-foreground mt-2">{s.label}</p>
              <p className="text-sm text-muted-foreground mt-1">{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
