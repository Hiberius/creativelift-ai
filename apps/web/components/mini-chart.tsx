export function MiniChart({ tone = "cyan" }: { tone?: "cyan" | "mint" | "lime" | "red" }) {
  const stroke = {
    cyan: "#20e7f6",
    mint: "#63f584",
    lime: "#a4ff5f",
    red: "#ff5c70"
  }[tone];
  return (
    <svg viewBox="0 0 120 32" className="h-8 w-full" aria-hidden="true">
      <path d="M0 24 C12 24 12 19 24 20 S36 28 48 19 60 13 72 15 84 22 96 12 108 8 120 10" fill="none" stroke={stroke} strokeWidth="2" />
    </svg>
  );
}

export function LiftChart() {
  const lines = [
    { d: "M10 152 C80 88 130 92 190 84 S310 90 390 70 520 78 620 34", color: "#20e7f6" },
    { d: "M10 132 C90 128 150 104 230 112 S380 112 470 94 560 104 620 78", color: "#4f8cff" },
    { d: "M10 126 C100 128 170 138 250 132 S380 154 460 170 550 158 620 150", color: "#a4ff5f" }
  ];
  return (
    <svg viewBox="0 0 640 190" className="h-72 w-full" role="img" aria-label="Creative lift over time chart">
      {[0, 1, 2, 3, 4].map((i) => (
        <line key={i} x1="0" x2="640" y1={30 + i * 32} y2={30 + i * 32} stroke="rgba(148,163,184,.16)" />
      ))}
      <line x1="0" x2="640" y1="126" y2="126" stroke="rgba(148,163,184,.35)" strokeDasharray="6 8" />
      {lines.map((line) => (
        <path key={line.color} d={line.d} fill="none" stroke={line.color} strokeWidth="3" />
      ))}
      {["May 4", "May 11", "May 18", "May 25", "Jun 1"].map((label, i) => (
        <text key={label} x={30 + i * 135} y="184" fill="#98a6b3" fontSize="12">
          {label}
        </text>
      ))}
    </svg>
  );
}
