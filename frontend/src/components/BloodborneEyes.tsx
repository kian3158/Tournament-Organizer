import { useEffect, useId, useRef, useState } from "react";

// A loose grid with per-eye jitter — enough structure to not feel random, still
// uneven enough to stay Bloodborne-messy. Varied size/opacity reads as depth.
const EYES = [
  // row 1
  { top: "11%", left: "8%", size: 92, opacity: 0.4, blink: "0s" },
  { top: "14%", left: "33%", size: 56, opacity: 0.2, blink: "3.3s" },
  { top: "9%", left: "59%", size: 60, opacity: 0.22, blink: "5.0s" },
  { top: "15%", left: "85%", size: 100, opacity: 0.36, blink: "4.1s" },
  // row 2
  { top: "40%", left: "5%", size: 70, opacity: 0.3, blink: "2.3s" },
  { top: "37%", left: "29%", size: 52, opacity: 0.14, blink: "4.6s" },
  { top: "43%", left: "71%", size: 64, opacity: 0.22, blink: "3.9s" },
  { top: "39%", left: "93%", size: 72, opacity: 0.26, blink: "1.8s" },
  // row 3
  { top: "66%", left: "14%", size: 64, opacity: 0.24, blink: "0.7s" },
  { top: "63%", left: "40%", size: 50, opacity: 0.13, blink: "5.4s" },
  { top: "68%", left: "67%", size: 70, opacity: 0.24, blink: "2.8s" },
  { top: "64%", left: "90%", size: 60, opacity: 0.2, blink: "2.0s" },
  // row 4
  { top: "90%", left: "26%", size: 66, opacity: 0.26, blink: "6.1s" },
  { top: "88%", left: "62%", size: 58, opacity: 0.22, blink: "1.2s" },
];

const isBloodborne = () =>
  document.documentElement.dataset.accent === "bloodborne";

function Eye({
  irisRef,
  blink,
}: {
  irisRef: (el: SVGGElement | null) => void;
  blink: string;
}) {
  const raw = useId().replace(/[:]/g, "");
  const s = `s${raw}`;
  const i = `i${raw}`;
  const c = `c${raw}`;
  return (
    <svg
      viewBox="0 0 100 100"
      className="h-full w-full"
      style={{
        filter: "drop-shadow(0 0 9px rgba(150, 22, 22, 0.55))",
        transformOrigin: "center",
        animation: `bb-blink 7s ${blink} infinite`,
      }}
      aria-hidden="true"
    >
      <defs>
        <radialGradient id={s} cx="50%" cy="42%" r="62%">
          <stop offset="0%" stopColor="#f7eedb" />
          <stop offset="68%" stopColor="#e4d2ad" />
          <stop offset="100%" stopColor="#b29469" />
        </radialGradient>
        <radialGradient id={i} cx="50%" cy="50%" r="55%">
          <stop offset="0%" stopColor="#e0973b" />
          <stop offset="42%" stopColor="#9c4a18" />
          <stop offset="100%" stopColor="#491c0a" />
        </radialGradient>
        <clipPath id={c}>
          <ellipse cx="50" cy="50" rx="48" ry="33" />
        </clipPath>
      </defs>

      <ellipse
        cx="50"
        cy="50"
        rx="48"
        ry="33"
        fill={`url(#${s})`}
        stroke="#4a2f20"
        strokeWidth="1.5"
      />

      {/* bloodshot veins on the sclera */}
      <g
        stroke="#9e2a24"
        strokeWidth="0.9"
        fill="none"
        opacity="0.55"
        strokeLinecap="round"
        clipPath={`url(#${c})`}
      >
        <path d="M4 48 q16 -7 28 -1" />
        <path d="M5 56 q15 3 24 1" />
        <path d="M96 50 q-16 9 -28 3" />
        <path d="M95 44 q-15 -4 -24 -1" />
        <path d="M50 17 q-5 12 -1 23" />
      </g>

      {/* moving iris + pupil */}
      <g ref={irisRef} clipPath={`url(#${c})`}>
        <circle
          cx="50"
          cy="50"
          r="21"
          fill={`url(#${i})`}
          stroke="#34150a"
          strokeWidth="1.5"
        />
        <g stroke="#34150a" strokeWidth="0.6" opacity="0.45">
          {Array.from({ length: 18 }).map((_, k) => {
            const a = (k * 20 * Math.PI) / 180;
            return (
              <line
                key={k}
                x1={50 + Math.cos(a) * 10}
                y1={50 + Math.sin(a) * 10}
                x2={50 + Math.cos(a) * 20}
                y2={50 + Math.sin(a) * 20}
              />
            );
          })}
        </g>
        <circle cx="50" cy="50" r="9.5" fill="#0c0605" />
        <circle cx="45" cy="45" r="3.4" fill="#fff" opacity="0.85" />
      </g>
    </svg>
  );
}

export default function BloodborneEyes() {
  const [on, setOn] = useState(isBloodborne);
  const irises = useRef<(SVGGElement | null)[]>([]);

  useEffect(() => {
    const obs = new MutationObserver(() => setOn(isBloodborne()));
    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-accent"],
    });
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!on) return;
    let raf = 0;
    function onMove(e: MouseEvent) {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        for (const g of irises.current) {
          if (!g?.ownerSVGElement) continue;
          const r = g.ownerSVGElement.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const angle = Math.atan2(e.clientY - cy, e.clientX - cx);
          const dist = Math.hypot(e.clientX - cx, e.clientY - cy);
          const d = Math.min(14, dist / 12);
          g.setAttribute(
            "transform",
            `translate(${Math.cos(angle) * d} ${Math.sin(angle) * d})`
          );
        }
      });
    }
    window.addEventListener("mousemove", onMove);
    return () => {
      window.removeEventListener("mousemove", onMove);
      cancelAnimationFrame(raf);
    };
  }, [on]);

  if (!on) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {EYES.map((eye, idx) => (
        <div
          key={idx}
          style={{
            position: "absolute",
            top: eye.top,
            left: eye.left,
            width: eye.size,
            height: eye.size,
            opacity: eye.opacity,
            transform: "translate(-50%, -50%)",
          }}
        >
          <Eye
            irisRef={(el) => {
              irises.current[idx] = el;
            }}
            blink={eye.blink}
          />
        </div>
      ))}
    </div>
  );
}
