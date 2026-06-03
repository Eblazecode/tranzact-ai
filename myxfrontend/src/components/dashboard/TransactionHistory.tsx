import { useEffect, useMemo, useRef } from "react";

import type { DashboardOverviewTransaction } from "@/lib/api";

const fmt = (v: number) => `\u20A6${v.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;

const AUTO_SCROLL_SPEED = 0.9;

export function TransactionHistory({ rows }: { rows: DashboardOverviewTransaction[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isManualControlRef = useRef(false);
  const initializedRef = useRef(false);

  const loopedRows = useMemo(() => {
    if (rows.length === 0) return [];
    return [...rows, ...rows, ...rows];
  }, [rows]);

  const normalizeScrollPosition = () => {
    const container = containerRef.current;
    if (!container) return;

    const oneSetHeight = container.scrollHeight / 3;
    if (oneSetHeight <= 0) return;

    if (!initializedRef.current) {
      container.scrollTop = oneSetHeight;
      initializedRef.current = true;
      return;
    }

    if (container.scrollTop >= oneSetHeight * 2) {
      container.scrollTop -= oneSetHeight;
    } else if (container.scrollTop <= 0) {
      container.scrollTop += oneSetHeight;
    }
  };

  useEffect(() => {
    const tick = () => {
      const container = containerRef.current;
      if (container) {
        normalizeScrollPosition();

        if (!isManualControlRef.current) {
          container.scrollTop += AUTO_SCROLL_SPEED;
          normalizeScrollPosition();
        }
      }

      animationFrameRef.current = window.requestAnimationFrame(tick);
    };

    animationFrameRef.current = window.requestAnimationFrame(tick);

    return () => {
      if (animationFrameRef.current !== null) {
        window.cancelAnimationFrame(animationFrameRef.current);
      }
      initializedRef.current = false;
      isManualControlRef.current = false;
    };
  }, [rows]);

  return (
    <div className="bg-card border border-border rounded-xl p-5 h-[420px] overflow-hidden relative">
      <p className="text-[13px] text-muted-foreground mb-4">Transaction History</p>
      <div className="grid grid-cols-[2fr_1fr_1fr_1fr] gap-2 px-2 py-2 text-xs font-semibold text-muted-foreground border-b border-border">
        <div>Description</div>
        <div>Category</div>
        <div>Date</div>
        <div className="text-right">Balance</div>
      </div>
      <div
        ref={containerRef}
        className="no-scrollbar relative h-[320px] overflow-y-auto overscroll-contain"
        onMouseLeave={() => {
          isManualControlRef.current = false;
        }}
        onWheel={(event) => {
          const container = containerRef.current;
          if (!container) return;

          event.preventDefault();
          isManualControlRef.current = true;
          container.scrollTop += event.deltaY;
          normalizeScrollPosition();
        }}
        onTouchStart={() => {
          isManualControlRef.current = true;
        }}
        onTouchEnd={() => {
          isManualControlRef.current = false;
        }}
      >
        <div>
          {loopedRows.map((row, i) => (
            <div key={`${row.date}-${row.description}-${i}`} className="grid grid-cols-[2fr_1fr_1fr_1fr] gap-2 px-2 py-3 text-sm border-b border-border/50">
              <div className="text-card-foreground truncate">{row.description}</div>
              <div className="text-muted-foreground truncate">{row.category}</div>
              <div className="text-muted-foreground">{row.date}</div>
              <div className="text-right font-semibold">{fmt(row.amount)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
