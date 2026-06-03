import { useEffect, useRef, useState } from "react";

const banks = [
  { name: "GTBank", initials: "GT" },
  { name: "OPay", initials: "OP" },
  { name: "Moniepoint", initials: "MP" },
  { name: "Zenith Bank", initials: "ZB" },
  { name: "Ecobank", initials: "EB" },
];

// Double the list for seamless loop
const scrollBanks = [...banks, ...banks];

function AnimatedNumber({ target }: { target: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          let current = 0;
          const step = Math.ceil(target / 40);
          const timer = setInterval(() => {
            current += step;
            if (current >= target) {
              setCount(target);
              clearInterval(timer);
            } else {
              setCount(current);
            }
          }, 30);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);

  return <span ref={ref}>{count.toLocaleString()}</span>;
}

export function TrustBar() {
  return (
    <section className="bg-background py-16 border-b border-border overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 text-center mb-10">
        <h2 className="text-xl sm:text-2xl font-semibold text-foreground mb-2">
          <AnimatedNumber target={10000} />+ Nigerians trust TransacAI to understand their finances.
        </h2>
        <p className="text-sm text-muted-foreground">
          Supporting statements from Nigeria's top financial institutions
        </p>
      </div>

      {/* Scrolling marquee */}
      <div className="relative w-full">
        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />

        <div className="flex animate-marquee gap-6 w-max">
          {scrollBanks.map((bank, i) => (
            <div
              key={`${bank.name}-${i}`}
              className="group flex items-center gap-3 px-6 py-4 rounded-xl border border-border bg-card hover:border-primary/30 hover:shadow-md transition-all duration-300 shrink-0"
            >
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-xs font-bold text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                {bank.initials}
              </div>
              <span className="text-sm font-medium text-foreground">{bank.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
