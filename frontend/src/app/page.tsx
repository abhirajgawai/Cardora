'use client';

import { motion } from 'framer-motion';
import {
  ArrowRight, Upload, Brain, BarChart3, Lock, Shield,
  Check, X, Sparkles, Bell, ChevronDown, ChevronUp, FileX,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const FAQItem = ({
  question,
  answer,
  isOpen,
  onClick,
}: {
  question: string;
  answer: string;
  isOpen: boolean;
  onClick: () => void;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    className="fintech-card overflow-hidden"
  >
    <button
      onClick={onClick}
      className="w-full p-6 flex items-center justify-between text-left"
    >
      <h3 className="text-lg font-semibold text-foreground pr-4">{question}</h3>
      {isOpen
        ? <ChevronUp className="w-5 h-5 text-primary flex-shrink-0" />
        : <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />}
    </button>
    <motion.div
      initial={false}
      animate={{ height: isOpen ? 'auto' : 0 }}
      transition={{ duration: 0.3 }}
      className="overflow-hidden"
    >
      <p className="px-6 pb-6 text-muted-foreground leading-relaxed">{answer}</p>
    </motion.div>
  </motion.div>
);

const DashboardIllustration = () => (
  <div className="rounded-2xl overflow-hidden border border-border shadow-2xl bg-card">
    {/* Browser chrome */}
    <div className="bg-muted/50 px-4 py-3 flex items-center gap-2 border-b border-border">
      <div className="w-3 h-3 rounded-full bg-red-400/80" />
      <div className="w-3 h-3 rounded-full bg-amber-400/80" />
      <div className="w-3 h-3 rounded-full bg-emerald-400/80" />
      <div className="flex-1 mx-4 h-5 bg-background rounded-md flex items-center px-3 gap-1.5">
        <Lock className="w-3 h-3 text-emerald-500 flex-shrink-0" />
        <span className="text-xs text-muted-foreground">cardora.app/dashboard</span>
      </div>
    </div>

    {/* App shell */}
    <div className="flex" style={{ height: '320px' }}>
      {/* Mini sidebar */}
      <div className="w-14 bg-muted/20 border-r border-border flex flex-col items-center pt-4 gap-3 flex-shrink-0">
        <div className="w-8 h-8 rounded-xl gradient-indigo-purple flex items-center justify-center">
          <div className="w-3 h-3 bg-white rounded-sm opacity-80" />
        </div>
        {(['bg-primary/20', 'bg-muted', 'bg-muted', 'bg-muted'] as const).map((bg, i) => (
          <div key={i} className={`w-8 h-8 rounded-xl ${bg}`} />
        ))}
      </div>

      {/* Main panel */}
      <div className="flex-1 p-4 overflow-hidden bg-background">
        {/* Page header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="h-3 w-36 bg-foreground/10 rounded mb-1.5" />
            <div className="h-2 w-48 bg-muted-foreground/20 rounded" />
          </div>
          <div className="px-3 py-1.5 rounded-lg gradient-teal-accent text-white text-xs font-semibold">
            Upload PDF
          </div>
        </div>

        {/* KPI cards */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          {[
            { label: 'This Month', value: 'SGD 2,480', sub: '▼ 8% vs last', subColor: 'text-emerald-500' },
            { label: 'Transactions', value: '47', sub: 'this month', subColor: 'text-muted-foreground' },
            { label: 'Top Category', value: 'Dining', sub: 'SGD 680', subColor: 'text-muted-foreground' },
          ].map((kpi, i) => (
            <div key={i} className="rounded-xl border border-border p-2.5 bg-card">
              <div className="text-[10px] text-muted-foreground mb-1">{kpi.label}</div>
              <div className="text-sm font-bold text-foreground leading-tight">{kpi.value}</div>
              <div className={`text-[10px] mt-0.5 ${kpi.subColor}`}>{kpi.sub}</div>
            </div>
          ))}
        </div>

        {/* Transaction list */}
        <div className="rounded-xl border border-border overflow-hidden">
          <div className="px-3 py-2 bg-muted/30 border-b border-border">
            <div className="text-xs font-semibold text-foreground">Recent Transactions</div>
          </div>
          {[
            { icon: '🍽️', name: 'Paradise Dynasty', cat: 'Dining', amount: '-SGD 68.50' },
            { icon: '🛒', name: 'Cold Storage', cat: 'Groceries', amount: '-SGD 124.30' },
            { icon: '🚗', name: 'Grab', cat: 'Transport', amount: '-SGD 18.90' },
            { icon: '💡', name: 'SP Group', cat: 'Utilities', amount: '-SGD 87.20' },
          ].map((t, i) => (
            <div
              key={i}
              className="flex items-center justify-between px-3 py-2 border-b border-border/50 last:border-0"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm">{t.icon}</span>
                <div>
                  <div className="text-xs font-medium text-foreground leading-tight">{t.name}</div>
                  <div className="text-[10px] text-muted-foreground">{t.cat}</div>
                </div>
              </div>
              <div className="text-xs font-semibold text-foreground">{t.amount}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

const COMPARISON_ROWS = [
  { feature: 'No bank account linking required', cardora: true, traditional: false },
  { feature: 'Works with any bank PDF statement', cardora: true, traditional: false },
  { feature: 'AI transaction categorization', cardora: true, traditional: true },
  { feature: 'Privacy-first — no credential storage', cardora: true, traditional: false },
  { feature: 'You choose what data to share', cardora: true, traditional: false },
  { feature: 'Export & delete your data anytime', cardora: true, traditional: 'partial' },
  { feature: 'Free to use', cardora: true, traditional: 'partial' },
] as const;

const FEATURES = [
  {
    icon: Upload,
    title: 'Upload any bank PDF',
    description:
      'Drag and drop your credit card statement. Our AI reads it and extracts every transaction in under 60 seconds.',
    accent: 'card-accent-indigo',
    iconBg: 'bg-primary/10',
    iconColor: 'text-primary',
  },
  {
    icon: BarChart3,
    title: 'Instant spending clarity',
    description:
      'See your spending by category, month, and card. Spot trends, compare periods, and understand your habits at a glance.',
    accent: 'card-accent-teal',
    iconBg: 'bg-accent/10',
    iconColor: 'text-accent',
  },
  {
    icon: Bell,
    title: 'Never miss a payment',
    description:
      "Smart payment alerts and a payoff calculator show you exactly what's due and how to clear balances faster.",
    accent: 'card-accent-amber',
    iconBg: 'bg-amber-500/10',
    iconColor: 'text-amber-500',
  },
] as const;

const HOW_IT_WORKS_STEPS = [
  {
    step: '01',
    color: 'bg-primary',
    title: 'Upload your PDF',
    description: 'Drag and drop your credit card statement. We support all major banks.',
  },
  {
    step: '02',
    color: 'bg-accent',
    title: 'AI extracts data',
    description: 'Every transaction, date, merchant, and amount — extracted automatically in seconds.',
  },
  {
    step: '03',
    color: 'bg-secondary',
    title: 'Explore your insights',
    description: 'Beautiful analytics, spending trends, and payment alerts — ready instantly.',
  },
] as const;

const DATA_LIFECYCLE_STEPS = [
  {
    icon: Upload,
    step: '1',
    title: 'You upload your PDF',
    description: 'Sent over an encrypted connection. Held in memory only — never written to disk.',
    iconBg: 'bg-primary',
    cardBorder: 'border-primary/30',
  },
  {
    icon: Brain,
    step: '2',
    title: 'AI extracts transactions',
    description: 'Processed in under 60 seconds. Dates, merchants, and amounts are saved to your account.',
    iconBg: 'bg-accent',
    cardBorder: 'border-accent/30',
  },
  {
    icon: FileX,
    step: '3',
    title: 'PDF is permanently deleted',
    description: 'Your file is gone within a minute. No copies, no backups. Only the extracted numbers remain.',
    iconBg: 'bg-emerald-500',
    cardBorder: 'border-emerald-500/30',
  },
] as const;

const FAQS = [
  {
    question: 'Do you link to my bank account?',
    answer:
      'No, never. Cardora only works with PDF statements you manually upload. We never ask for banking credentials or connect to your accounts in any way.',
  },
  {
    question: 'How does the AI extraction work?',
    answer:
      'Our AI reads your PDF and identifies every transaction — date, merchant, amount, and category — with 93% accuracy. It works with statement formats from all major banks.',
  },
  {
    question: 'What happens to my PDF after upload?',
    answer:
      'Your PDF is processed in memory and permanently deleted within a minute of upload. We only store the extracted transaction data — no full statements, no document backups.',
  },
  {
    question: 'Can I delete my data?',
    answer:
      'Yes, completely. You can export all your data or delete your entire account in one click from the Settings page. No questions asked.',
  },
  {
    question: 'Is it really free?',
    answer:
      "Yes. Core features are free with no credit card required. We're focused on building the best privacy-first financial tool — premium features for power users will come later, but the core will always be free.",
  },
];

export default function Home() {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen fintech-bg">

      {/* ── Navbar ── */}
      <nav className="fixed top-0 w-full z-50 glass-effect border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="text-2xl font-bold text-primary"
          >
            CARDORA
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex gap-4"
          >
            <Link
              href="/login"
              className="px-6 py-2 text-foreground/80 hover:text-foreground transition-colors font-medium"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-6 py-2 rounded-xl gradient-indigo-purple text-white font-semibold shadow-lg btn-hover"
            >
              Get Started
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative min-h-screen flex items-center overflow-hidden pt-24 pb-20 px-6">
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.05, 0.1, 0.05] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-1/4 -left-32 w-96 h-96 bg-primary rounded-full blur-3xl pointer-events-none"
        />
        <motion.div
          animate={{ scale: [1.1, 1, 1.1], opacity: [0.05, 0.1, 0.05] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          className="absolute bottom-1/4 -right-32 w-96 h-96 bg-accent rounded-full blur-3xl pointer-events-none"
        />

        <div className="relative z-10 max-w-7xl mx-auto w-full grid lg:grid-cols-2 gap-16 items-center">
          {/* Left — copy */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-border mb-6"
            >
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-foreground">AI-Powered · Privacy-First</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6"
            >
              <span className="text-foreground">Know exactly</span>
              <br />
              <span className="text-foreground">where your</span>
              <br />
              <span className="text-primary">money goes.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed"
            >
              Upload your credit card PDF statement. Our AI extracts every transaction
              automatically — categorized, visualized, and ready to explore.{' '}
              <span className="font-semibold text-foreground">
                No bank linking. No passwords. Ever.
              </span>
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 mb-8"
            >
              <Link
                href="/register"
                className="group px-8 py-4 rounded-xl gradient-indigo-purple text-white font-semibold text-lg shadow-lg btn-hover flex items-center justify-center gap-2"
              >
                Start Free Today
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="#how-it-works"
                className="px-8 py-4 rounded-xl glass-effect border border-border text-foreground font-semibold text-lg card-hover text-center"
              >
                See how it works
              </a>
            </motion.div>

            {/* Inline trust row */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="flex flex-wrap gap-5 text-sm text-muted-foreground"
            >
              {([
                { Icon: Lock, text: 'No bank credentials' },
                { Icon: Check, text: 'You control your data' },
                { Icon: Shield, text: 'Delete anytime' },
              ] as const).map(({ Icon, text }) => (
                <div key={text} className="flex items-center gap-1.5">
                  <Icon className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                  <span>{text}</span>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right — illustration */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            >
              <DashboardIllustration />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Stats strip ── */}
      <section className="py-10 px-6 border-y border-border bg-card/50">
        <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-8 text-center divide-y sm:divide-y-0 sm:divide-x divide-border">
          {[
            { value: '93%', label: 'AI extraction accuracy', note: 'across all statement formats' },
            { value: '0', label: 'Bank accounts ever linked', note: 'by design, not by accident' },
            { value: '< 60s', label: 'To process any statement', note: 'from upload to insights' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="py-4 sm:py-0 sm:px-8"
            >
              <div className="text-4xl font-bold text-primary mb-1">{stat.value}</div>
              <div className="text-base font-semibold text-foreground mb-0.5">{stat.label}</div>
              <div className="text-sm text-muted-foreground">{stat.note}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Comparison table ── */}
      <section className="py-24 px-6 bg-muted/30">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-14"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Why choose Cardora?
            </h2>
            <p className="text-xl text-muted-foreground max-w-xl mx-auto">
              Traditional finance apps require you to hand over the keys to your bank. We don't.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="fintech-card overflow-hidden"
          >
            {/* Header row */}
            <div className="grid grid-cols-3 bg-muted/40 border-b border-border">
              <div className="p-5 text-sm font-semibold text-muted-foreground">Feature</div>
              <div className="p-5 text-center border-l border-border">
                <span className="text-base font-bold text-primary">Cardora</span>
              </div>
              <div className="p-5 text-center border-l border-border">
                <span className="text-base font-semibold text-muted-foreground">Traditional Apps</span>
              </div>
            </div>

            {COMPARISON_ROWS.map(({ feature, cardora, traditional }, i) => (
              <div
                key={i}
                className="grid grid-cols-3 border-b border-border/60 last:border-0 hover:bg-muted/10 transition-colors"
              >
                <div className="p-5 text-sm text-foreground font-medium">{feature}</div>
                <div className="p-5 flex justify-center items-center border-l border-border/60">
                  {cardora && <Check className="w-5 h-5 text-emerald-500" />}
                </div>
                <div className="p-5 flex justify-center items-center border-l border-border/60">
                  {traditional === true ? (
                    <Check className="w-5 h-5 text-emerald-500" />
                  ) : traditional === 'partial' ? (
                    <span className="text-xs font-medium text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded-full">
                      Varies
                    </span>
                  ) : (
                    <X className="w-5 h-5 text-red-400" />
                  )}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-14"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Everything you need.
              <br />
              <span className="text-muted-foreground">Nothing you don't.</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map(({ icon: Icon, title, description, accent, iconBg, iconColor }, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className={`fintech-card ${accent} p-8 card-hover`}
              >
                <div className={`w-14 h-14 rounded-2xl ${iconBg} flex items-center justify-center mb-6`}>
                  <Icon className={`w-7 h-7 ${iconColor}`} />
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
                <p className="text-muted-foreground leading-relaxed">{description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" className="py-24 px-6 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Simple as 1, 2, 3.
            </h2>
            <p className="text-xl text-muted-foreground">Get started in minutes, not hours.</p>
          </motion.div>

          <div className="relative grid md:grid-cols-3 gap-12">
            <div className="hidden md:block absolute top-10 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary via-accent to-secondary" />

            {HOW_IT_WORKS_STEPS.map(({ step, color, title, description }, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.2 }}
                className="relative text-center"
              >
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className={`relative z-10 w-20 h-20 mx-auto mb-6 rounded-full ${color} flex items-center justify-center text-2xl font-bold text-white shadow-lg`}
                >
                  {step}
                </motion.div>
                <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
                <p className="text-muted-foreground leading-relaxed">{description}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="mt-12 flex justify-center"
          >
            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <Lock className="w-5 h-5 text-emerald-500" />
              <span className="text-sm font-semibold text-emerald-500">
                No bank credentials needed at any step
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Data lifecycle ── */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-14"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-emerald-500/30 mb-6">
              <Shield className="w-5 h-5 text-emerald-500" />
              <span className="text-sm font-medium text-emerald-500">100% Transparent</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              What happens to your PDF?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Your document is never stored. Here's exactly what we do with it.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {DATA_LIFECYCLE_STEPS.map(({ icon: Icon, step, title, description, iconBg, cardBorder }, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                className={`fintech-card border ${cardBorder} p-6`}
              >
                <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">
                  Step {step}
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="mt-8 text-center"
          >
            <Link
              href="/data-transparency"
              className="text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              View full data controls →
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="py-24 px-6 bg-muted/30">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Common questions
            </h2>
            <p className="text-xl text-muted-foreground">Everything you need to know</p>
          </motion.div>

          <div className="space-y-4">
            {FAQS.map((faq, i) => (
              <FAQItem
                key={i}
                question={faq.question}
                answer={faq.answer}
                isOpen={openFAQ === i}
                onClick={() => setOpenFAQ(openFAQ === i ? null : i)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative fintech-card card-accent-indigo p-14 text-center overflow-hidden"
          >
            <motion.div
              animate={{ scale: [1, 1.15, 1], opacity: [0.04, 0.08, 0.04] }}
              transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute inset-0 bg-gradient-to-r from-primary to-accent blur-3xl pointer-events-none"
            />
            <div className="relative z-10">
              <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                Ready to see your spending clearly?
              </h2>
              <p className="text-xl text-muted-foreground mb-8 max-w-xl mx-auto">
                No bank login. No passwords. Just upload your statement and let the AI do the rest.
              </p>
              <Link
                href="/register"
                className="group inline-flex items-center gap-3 px-10 py-4 rounded-xl gradient-indigo-purple text-white font-bold text-lg shadow-lg btn-hover"
              >
                Start Analyzing — It's Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <p className="mt-5 text-muted-foreground text-sm">
                No credit card required · No bank linking · Free forever
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative py-12 px-6 border-t border-border bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
            <div>
              <h3 className="text-2xl font-bold text-primary mb-2">CARDORA</h3>
              <p className="text-muted-foreground mb-4">Privacy-first financial management</p>
              <div className="flex flex-wrap gap-3">
                {([
                  { Icon: Shield, text: '256-bit Encryption' },
                  { Icon: Lock, text: 'Zero Bank Access' },
                  { Icon: Check, text: 'GDPR Compliant' },
                ] as const).map(({ Icon, text }) => (
                  <div
                    key={text}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg glass-effect border border-border text-xs"
                  >
                    <Icon className="w-3 h-3 text-emerald-500" />
                    <span className="text-muted-foreground">{text}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex gap-8 text-muted-foreground">
              <Link href="/data-transparency" className="hover:text-foreground transition-colors font-medium">
                Data Controls
              </Link>
              <Link href="/about" className="hover:text-foreground transition-colors font-medium">
                About
              </Link>
            </div>
          </div>
          <div className="text-center text-muted-foreground text-sm border-t border-border pt-8">
            © 2024 Cardora. All rights reserved. · Your data, your control, always.
          </div>
        </div>
      </footer>
    </div>
  );
}
