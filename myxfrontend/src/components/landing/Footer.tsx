import { Sparkles } from "lucide-react";

const footerLinks = {
  Product: ["Features", "Predictions", "Recommendations", "Pricing"],
  "Supported Banks": ["GTBank", "OPay", "Moniepoint", "Zenith Bank", "Ecobank"],
  Company: ["About", "Blog", "Careers", "Contact"],
  Legal: ["Privacy Policy", "Terms of Service", "Security"],
};

export function Footer() {
  return (
    <footer className="bg-navy py-16 px-4">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="text-lg font-bold text-navy-foreground">
                Transac<span className="text-primary">AI</span>
              </span>
            </div>
            <p className="text-sm text-navy-foreground/50 leading-relaxed">
              Nigeria's most trusted financial intelligence platform.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-sm font-semibold text-navy-foreground mb-4">{title}</h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-navy-foreground/50 hover:text-primary transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-8 border-t border-navy-foreground/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-navy-foreground/40">
            © {new Date().getFullYear()} TransacAI. All rights reserved.
          </p>
          <p className="text-xs text-navy-foreground/40">
            Your data never leaves our secure servers. No bank connections required.
          </p>
        </div>
      </div>
    </footer>
  );
}
