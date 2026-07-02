import {
  Activity,
  BarChart3,
  Beaker,
  CheckCircle2,
  Database,
  FileText,
  GitBranch,
  KeyRound,
  LineChart,
  Plug,
  ShieldCheck,
  Sparkles,
  Users
} from "lucide-react";

export const navItems = [
  { label: "Product", href: "/product" },
  { label: "Use Cases", href: "/use-cases/ai-creative-testing" },
  { label: "Open Source", href: "/open-source" },
  { label: "Security", href: "/security" },
  { label: "Docs", href: "/docs" },
  { label: "Pricing", href: "/pricing" }
];

export const appNavItems = [
  { label: "Dashboard", href: "/app/dashboard", icon: BarChart3 },
  { label: "Briefs", href: "/app/briefs", icon: FileText },
  { label: "Creatives", href: "/app/creatives", icon: Sparkles },
  { label: "Experiments", href: "/app/experiments", icon: Beaker },
  { label: "Approvals", href: "/app/approvals", icon: CheckCircle2 },
  { label: "Events", href: "/app/events", icon: Activity },
  { label: "Connectors", href: "/app/connectors", icon: Plug },
  { label: "API Keys", href: "/app/api-keys", icon: KeyRound },
  { label: "Settings", href: "/app/settings", icon: ShieldCheck }
];

export const heroBullets = [
  "Prompt-to-profit creative lineage",
  "Experiment registry for AI-generated variants",
  "Incrementality-first measurement",
  "Self-hostable and warehouse-ready",
  "Built for marketers, data teams, and agencies"
];

export const metrics = [
  { label: "Prompt-to-profit lift", value: "+18.7%", hint: "vs. baseline", tone: "mint" },
  { label: "Incremental Revenue", value: "$2.43M", hint: "95% CI: $1.85M - $3.02M", tone: "white" },
  { label: "Spend", value: "$1.29M", hint: "Efficiency: $1.88 ROI", tone: "white" },
  { label: "Conversions", value: "24,183", hint: "Lift: +15.2%", tone: "mint" },
  { label: "SRM", value: "0.98", hint: "Healthy", tone: "mint" },
  { label: "Active Experiments", value: "12", hint: "2 ending soon", tone: "warning" }
];

export const treatments = [
  {
    id: "00000000-0000-0000-0000-000000000101",
    name: "AI Video - Sunset v3",
    type: "Video",
    experiment: "EXP-2024-0521",
    channel: "Meta",
    spend: "$312,402",
    lift: "+23.4%",
    revenue: "$734,210",
    status: "Winning"
  },
  {
    id: "00000000-0000-0000-0000-000000000102",
    name: "AI UGC - Founder v2",
    type: "Video",
    experiment: "EXP-2024-0523",
    channel: "TikTok",
    spend: "$198,721",
    lift: "+11.2%",
    revenue: "$245,680",
    status: "Running"
  },
  {
    id: "00000000-0000-0000-0000-000000000103",
    name: "AI Image - Product v5",
    type: "Image",
    experiment: "EXP-2024-0526",
    channel: "Google",
    spend: "$143,221",
    lift: "-1.8%",
    revenue: "-$8,112",
    status: "Inconclusive"
  },
  {
    id: "00000000-0000-0000-0000-000000000104",
    name: "Control - Static",
    type: "Image",
    experiment: "Baseline",
    channel: "Meta",
    spend: "$201,334",
    lift: "-",
    revenue: "-",
    status: "Control"
  },
  {
    id: "00000000-0000-0000-0000-000000000105",
    name: "AI Email - Proof angle",
    type: "Email",
    experiment: "EXP-2024-0528",
    channel: "Lifecycle",
    spend: "$18,972",
    lift: "+19.1%",
    revenue: "$187,920",
    status: "Running"
  }
];

export const experiments = [
  {
    id: "00000000-0000-0000-0000-000000000201",
    name: "AI Video vs Static",
    channel: "Meta Paid Social",
    lift: "+23.4%",
    confidence: 98,
    status: "Winning"
  },
  {
    id: "00000000-0000-0000-0000-000000000202",
    name: "AI UGC vs Brand Video",
    channel: "TikTok",
    lift: "+11.2%",
    confidence: 76,
    status: "Running"
  },
  {
    id: "00000000-0000-0000-0000-000000000203",
    name: "AI Image Variants",
    channel: "Google Ads",
    lift: "-1.8%",
    confidence: 22,
    status: "Inconclusive"
  }
];

export const approvalQueue = [
  { name: "AI Video - Testimonial v2", requestor: "Maya Patel", age: "2h ago" },
  { name: "AI Image - Offer v3", requestor: "Jason Lee", age: "5h ago" },
  { name: "Prompt Update - Brand Voice", requestor: "Alex Kim", age: "1d ago" }
];

export const connectors = [
  { name: "PostHog", status: "Scaffolded", events: "1.2M", lag: "2m 18s" },
  { name: "Rudder", status: "Scaffolded", events: "8.7M", lag: "1m 05s" },
  { name: "Snowplow", status: "Scaffolded", events: "3.1M", lag: "5m 47s" },
  { name: "Google Ads", status: "Stub", events: "metadata", lag: "manual" },
  { name: "Meta Ads", status: "Stub", events: "metadata", lag: "manual" },
  { name: "HubSpot", status: "Stub", events: "leads", lag: "manual" }
];

export const useCases = {
  "ai-creative-testing": {
    title: "AI Creative Testing",
    description: "Turn generated ads, emails, and landing page variants into measurable treatments with lineage, approvals, and lift results.",
    icon: Sparkles
  },
  "marketing-attribution": {
    title: "Marketing Attribution",
    description: "Feed attribution systems with experiment-calibrated creative events instead of trusting platform ROAS blindly.",
    icon: GitBranch
  },
  agencies: {
    title: "Agencies",
    description: "Standardize prompt-to-profit reporting across clients while keeping data self-hosted and auditable.",
    icon: Users
  },
  "b2b-saas": {
    title: "B2B SaaS",
    description: "Measure messaging, landing page, lifecycle, and paid social variants against pipeline-aware conversion events.",
    icon: LineChart
  },
  ecommerce: {
    title: "E-commerce",
    description: "Connect product creative tests to purchases, revenue per visitor, guardrails, and MMM-ready calibration data.",
    icon: Database
  }
};

export const comparisons = {
  jasper: {
    name: "Jasper",
    positioning: "Jasper is strong for AI content generation. CreativeLift AI focuses on measurement, lineage, and incrementality after content is created."
  },
  anyword: {
    name: "Anyword",
    positioning: "Anyword is useful for predictive scoring. CreativeLift AI focuses on real experiment outcomes and revenue lift."
  },
  optimizely: {
    name: "Optimizely",
    positioning: "Optimizely is a mature experimentation platform. CreativeLift AI is creative-treatment native, open source, and prompt-lineage aware."
  },
  "triple-whale": {
    name: "Triple Whale",
    positioning: "Triple Whale is known for e-commerce attribution. CreativeLift AI focuses on prompt-to-profit creative lineage and causal testing."
  },
  hockeystack: {
    name: "HockeyStack",
    positioning: "HockeyStack is useful for B2B attribution. CreativeLift AI focuses on open-source AI creative measurement and experiment calibration."
  }
};
