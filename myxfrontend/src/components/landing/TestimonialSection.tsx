import { Star } from "lucide-react";
import userTestimonial from "@/assets/user-testimonial.jpg";

const testimonials = [
  {
    quote:
      "I used to spend hours trying to make sense of my bank statements. TransacAI showed me exactly where my money was going — and where I was losing it.",
    name: "Adaeze O.",
    role: "Business Owner, Lagos",
    rating: 5,
  },
  {
    quote:
      "The predictions are scary accurate. It told me I'd overspend this month and showed me why. I actually adjusted my budget because of it.",
    name: "Chinedu K.",
    role: "Software Engineer, Abuja",
    rating: 5,
  },
  {
    quote:
      "Best part? I didn't have to connect my bank or share any login details. Just uploaded my statement and boom — full dashboard.",
    name: "Funke A.",
    role: "Freelancer, Port Harcourt",
    rating: 5,
  },
];

export function TestimonialSection() {
  return (
    <section className="py-24 bg-muted/30">
      <div className="mx-auto max-w-7xl px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left: Image */}
          <div className="relative">
            <div className="rounded-2xl overflow-hidden shadow-2xl">
              <img
                src={userTestimonial}
                alt="Nigerian professional using TransacAI on their phone"
                className="w-full h-auto object-cover"
                loading="lazy"
                width={800}
                height={800}
              />
            </div>
            {/* Floating badge */}
            <div className="absolute bottom-6 left-6 bg-card/95 backdrop-blur-sm rounded-xl shadow-lg border border-border p-4">
              <div className="flex items-center gap-1 mb-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                ))}
              </div>
              <p className="text-sm font-semibold text-foreground">4.9/5 average rating</p>
              <p className="text-xs text-muted-foreground">from 2,000+ users</p>
            </div>
          </div>

          {/* Right: Testimonials */}
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-3">
              What Users Say
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-10">
              Real results from real Nigerians
            </h2>

            <div className="space-y-8">
              {testimonials.map((t) => (
                <div
                  key={t.name}
                  className="p-6 rounded-2xl border border-border bg-card hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-1 mb-3">
                    {[...Array(t.rating)].map((_, i) => (
                      <Star key={i} className="h-3.5 w-3.5 fill-primary text-primary" />
                    ))}
                  </div>
                  <p className="text-foreground leading-relaxed mb-4">"{t.quote}"</p>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
