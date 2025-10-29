'use client';

import { motion } from 'framer-motion';
import { ArrowRight, CreditCard, Sparkles, Shield, TrendingUp, Zap, Brain, FileText, BarChart3, Lock, Upload, Eye, X, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const FAQItem = ({ question, answer, isOpen, onClick }: { question: string; answer: string; isOpen: boolean; onClick: () => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="fintech-card card-hover overflow-hidden"
    >
      <button
        onClick={onClick}
        className="w-full p-6 flex items-center justify-between text-left"
      >
        <h3 className="text-lg font-semibold text-foreground pr-4">{question}</h3>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-primary flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
        )}
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
};

export default function Home() {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);
  const router = useRouter();

  // Redirect logged-in users to dashboard
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        router.push('/dashboard');
      }
    }
  }, [router]);

  return (
    <div className="min-h-screen fintech-bg">
      {/* Navigation */}
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

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 px-6">
        {/* Animated gradient orbs - Subtler */}
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.05, 0.1, 0.05],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.1, 1, 1.1],
            opacity: [0.05, 0.1, 0.05],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent rounded-full blur-3xl"
        />

        <div className="relative z-10 max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-border mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">AI-Powered Credit Card Management</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight"
          >
            <span className="text-foreground">Your finances,</span>
            <br />
            <span className="text-primary">
              beautifully simple.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            Upload your credit card PDF statements. Get AI-powered insights.
            <br />
            <span className="text-foreground font-semibold">No bank linking required.</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-20"
          >
            <Link
              href="/register"
              className="group px-8 py-4 rounded-xl gradient-indigo-purple text-white font-semibold text-lg shadow-lg btn-hover flex items-center justify-center gap-2"
            >
              Start Free Today
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <button className="px-8 py-4 rounded-xl glass-effect border border-border text-foreground font-semibold text-lg card-hover">
              Watch Demo
            </button>
          </motion.div>

          {/* Privacy Trust Badges */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="mb-20"
          >
            <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full glass-effect border border-emerald-500/30 mb-8">
              <Lock className="w-6 h-6 text-emerald-500" />
              <span className="text-lg font-bold text-emerald-500">Your Privacy, Guaranteed</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
              {[
                { icon: X, text: 'No bank account linking', iconColor: 'text-red-500', bgColor: 'border-red-500/20 bg-red-500/5' },
                { icon: X, text: 'No passwords stored', iconColor: 'text-red-500', bgColor: 'border-red-500/20 bg-red-500/5' },
                { icon: Check, text: 'YOU control your data', iconColor: 'text-emerald-500', bgColor: 'border-emerald-500/20 bg-emerald-500/5' },
                { icon: Check, text: 'Upload at YOUR pace', iconColor: 'text-emerald-500', bgColor: 'border-emerald-500/20 bg-emerald-500/5' }
              ].map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 1.2 + idx * 0.1 }}
                  className={`flex items-center justify-center gap-3 text-base font-medium px-6 py-4 rounded-xl border ${item.bgColor} glass-effect card-hover`}
                >
                  <item.icon className={`w-6 h-6 ${item.iconColor} flex-shrink-0`} />
                  <span className="text-foreground">{item.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Floating dashboard preview */}
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 1 }}
            className="relative"
          >
            <motion.div
              animate={{
                y: [0, -15, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="relative mx-auto w-full max-w-5xl fintech-card p-8 shadow-2xl"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-3 h-3 rounded-full bg-destructive" />
                <div className="w-3 h-3 rounded-full bg-accent" />
                <div className="w-3 h-3 rounded-full bg-primary" />
              </div>
              <div className="space-y-4">
                <div className="h-4 bg-gradient-to-r from-primary/20 to-transparent rounded w-3/4" />
                <div className="h-4 bg-gradient-to-r from-accent/20 to-transparent rounded w-1/2" />
                <div className="grid grid-cols-3 gap-4 mt-8">
                  <div className="h-32 rounded-xl fintech-card card-accent-indigo p-4 flex flex-col justify-between">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      <CreditCard className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <div className="h-2 bg-primary/20 rounded w-3/4 mb-2" />
                      <div className="h-2 bg-primary/10 rounded w-1/2" />
                    </div>
                  </div>
                  <div className="h-32 rounded-xl fintech-card card-accent-teal p-4 flex flex-col justify-between">
                    <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-accent" />
                    </div>
                    <div>
                      <div className="h-2 bg-accent/20 rounded w-3/4 mb-2" />
                      <div className="h-2 bg-accent/10 rounded w-1/2" />
                    </div>
                  </div>
                  <div className="h-32 rounded-xl fintech-card card-accent-amber p-4 flex flex-col justify-between">
                    <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                      <BarChart3 className="w-4 h-4 text-amber-500" />
                    </div>
                    <div>
                      <div className="h-2 bg-amber-500/20 rounded w-3/4 mb-2" />
                      <div className="h-2 bg-amber-500/10 rounded w-1/2" />
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It's Different Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Why Cardora vs. Mint/YNAB?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              We believe in privacy-first financial management. You shouldn't have to give up your banking credentials to track your spending.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Traditional Apps Column */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="fintech-card p-8 space-y-4 border-2 border-red-500/20"
            >
              <h3 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-2">
                <span className="text-red-500">❌</span> Traditional Apps
              </h3>
              {[
                'Require bank account linking via Plaid',
                'Store your banking passwords',
                'Have real-time access to your accounts',
                'Can see ALL your transactions automatically',
                'Continuous data sync you can\'t control'
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <X className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">{item}</span>
                </div>
              ))}
            </motion.div>

            {/* Cardora Column */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="fintech-card p-8 space-y-4 border-2 border-emerald-500/50 card-accent-emerald"
            >
              <h3 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-2">
                <span className="text-emerald-500">✓</span> Cardora
              </h3>
              {[
                'No linking to bank accounts',
                'Never store passwords or credentials',
                'You upload statements on YOUR schedule',
                'We only see what YOU choose to share',
                'Complete control over your data'
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <span className="text-foreground font-medium">{item}</span>
                </div>
              ))}
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-12 text-center"
          >
            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <Lock className="w-5 h-5 text-emerald-500" />
              <span className="text-emerald-500 font-semibold">Perfect for privacy-conscious users</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Everything you need.
              <br />
              <span className="text-muted-foreground">Nothing you don't.</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to give you complete control over your finances.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Lock,
                title: 'Your Data, Your Control',
                description: 'Unlike apps that link to your bank, we only see the statements YOU choose to upload. No passwords. No account access. Ever.',
                accent: 'emerald',
                iconBg: 'bg-emerald-500/10',
                iconColor: 'text-emerald-500'
              },
              {
                icon: Brain,
                title: 'AI-Powered Extraction',
                description: 'Upload PDF statements and watch our AI extract transactions with 93% accuracy.',
                accent: 'indigo',
                iconBg: 'bg-primary/10',
                iconColor: 'text-primary'
              },
              {
                icon: TrendingUp,
                title: 'Smart Analytics',
                description: 'Get personalized insights and spending patterns powered by advanced algorithms.',
                accent: 'teal',
                iconBg: 'bg-accent/10',
                iconColor: 'text-accent'
              },
              {
                icon: FileText,
                title: 'Multi-Card Support',
                description: 'Manage all your credit cards in one beautiful, unified dashboard.',
                accent: 'amber',
                iconBg: 'bg-amber-500/10',
                iconColor: 'text-amber-500'
              },
              {
                icon: Zap,
                title: 'Instant Insights',
                description: 'Real-time processing gives you immediate feedback on your spending.',
                accent: 'indigo',
                iconBg: 'bg-secondary/10',
                iconColor: 'text-secondary'
              },
              {
                icon: Shield,
                title: 'Bank-Level Security',
                description: 'Your data is encrypted and secured with industry-leading protocols and compliance.',
                accent: 'emerald',
                iconBg: 'bg-emerald-500/10',
                iconColor: 'text-emerald-500'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`fintech-card card-accent-${feature.accent} p-8 card-hover cursor-pointer`}
              >
                <div className={`w-14 h-14 rounded-2xl ${feature.iconBg} flex items-center justify-center mb-6`}>
                  <feature.icon className={`w-7 h-7 ${feature.iconColor}`} />
                </div>
                <h3 className="text-2xl font-bold text-foreground mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Simple as 1, 2, 3.
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-16">
              Get started in minutes, not hours.
            </p>

            {/* Visual Flow Diagram */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="max-w-4xl mx-auto mb-16"
            >
              <div className="flex flex-col md:flex-row items-center justify-center gap-6">
                {/* PDF Upload */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="flex-1 max-w-xs"
                >
                  <div className="fintech-card card-accent-indigo p-8 text-center">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
                      <Upload className="w-10 h-10 text-primary" />
                    </div>
                    <h3 className="text-xl font-bold text-foreground mb-2">PDF Upload</h3>
                    <p className="text-sm text-muted-foreground">Drag & drop your statement</p>
                  </div>
                </motion.div>

                {/* Arrow */}
                <div className="hidden md:block">
                  <ArrowRight className="w-8 h-8 text-primary" />
                </div>
                <div className="md:hidden">
                  <motion.div
                    animate={{ y: [0, 10, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="w-8 h-8 text-primary rotate-90" />
                  </motion.div>
                </div>

                {/* AI Extraction */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="flex-1 max-w-xs"
                >
                  <div className="fintech-card card-accent-teal p-8 text-center">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-accent/10 flex items-center justify-center">
                      <Brain className="w-10 h-10 text-accent" />
                    </div>
                    <h3 className="text-xl font-bold text-foreground mb-2">AI Extraction</h3>
                    <p className="text-sm text-muted-foreground">Automatic data processing</p>
                  </div>
                </motion.div>

                {/* Arrow */}
                <div className="hidden md:block">
                  <ArrowRight className="w-8 h-8 text-primary" />
                </div>
                <div className="md:hidden">
                  <motion.div
                    animate={{ y: [0, 10, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="w-8 h-8 text-primary rotate-90" />
                  </motion.div>
                </div>

                {/* Insights Dashboard */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="flex-1 max-w-xs"
                >
                  <div className="fintech-card card-accent-amber p-8 text-center">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-secondary/10 flex items-center justify-center">
                      <BarChart3 className="w-10 h-10 text-secondary" />
                    </div>
                    <h3 className="text-xl font-bold text-foreground mb-2">Insights Dashboard</h3>
                    <p className="text-sm text-muted-foreground">Beautiful visualizations</p>
                  </div>
                </motion.div>
              </div>

              {/* Privacy Note Below Diagram */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="mt-8 inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/20"
              >
                <Lock className="w-5 h-5 text-emerald-500" />
                <span className="text-sm font-semibold text-emerald-500">No bank credentials needed at any step</span>
              </motion.div>
            </motion.div>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            {/* Connection line */}
            <div className="hidden md:block absolute top-16 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary via-accent to-secondary" />

            {[
              {
                step: '01',
                title: 'Upload Statement',
                description: 'Simply drag and drop your credit card PDF statement. We support all major banks.',
                color: 'primary'
              },
              {
                step: '02',
                title: 'AI Extracts Data',
                description: 'Our advanced AI reads and extracts all transactions automatically in seconds.',
                color: 'accent'
              },
              {
                step: '03',
                title: 'Get Insights',
                description: 'View beautiful analytics, trends, and personalized recommendations instantly.',
                color: 'secondary'
              }
            ].map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="relative text-center"
              >
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className={`relative z-10 w-20 h-20 mx-auto mb-6 rounded-full ${
                    step.color === 'primary' ? 'bg-primary' :
                    step.color === 'accent' ? 'bg-accent' :
                    'bg-secondary'
                  } flex items-center justify-center text-2xl font-bold text-white shadow-lg`}
                >
                  {step.step}
                </motion.div>
                <h3 className="text-2xl font-bold text-foreground mb-3">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Loved by privacy-conscious users
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Join thousands who've taken back control of their financial data
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "Finally, a finance app that doesn't ask for my bank password. I was so uncomfortable with Mint's Plaid integration. Cardora is exactly what I needed.",
                author: "Sarah M.",
                role: "Privacy Advocate",
                rating: 5
              },
              {
                quote: "I love having complete control over what data I share. Upload statements when I want, get insights immediately. No creepy bank account access.",
                author: "Michael T.",
                role: "Software Engineer",
                rating: 5
              },
              {
                quote: "As someone who works in cybersecurity, I can't trust apps that link to my bank. Cardora's upload-only approach is brilliant and secure.",
                author: "Jennifer L.",
                role: "Security Analyst",
                rating: 5
              }
            ].map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="fintech-card p-8 card-hover"
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} className="text-amber-500 text-xl">★</span>
                  ))}
                </div>
                <p className="text-foreground mb-6 leading-relaxed italic">"{testimonial.quote}"</p>
                <div>
                  <p className="font-semibold text-foreground">{testimonial.author}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { value: '93%', label: 'AI Accuracy', description: 'Transaction extraction', accent: 'indigo' },
              { value: '0', label: 'Bank Accounts', description: 'Ever linked', accent: 'emerald', featured: true },
              { value: '50k+', label: 'Statements', description: 'Analyzed securely', accent: 'teal' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`fintech-card card-accent-${stat.accent} ${
                  stat.featured ? 'p-10 border-2 border-emerald-500/30 md:scale-105' : 'p-8'
                } text-center card-hover`}
              >
                <h3 className={`${stat.featured ? 'text-7xl' : 'text-6xl'} font-bold text-primary mb-2`}>
                  {stat.value}
                </h3>
                <p className={`${stat.featured ? 'text-2xl' : 'text-xl'} font-semibold text-foreground mb-1`}>
                  {stat.label}
                </p>
                <p className="text-sm text-muted-foreground">{stat.description}</p>
                {stat.featured && (
                  <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                    <Lock className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs font-semibold text-emerald-500">Our Promise</span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-muted-foreground">
              Everything you need to know about Cardora
            </p>
          </motion.div>

          <div className="space-y-4">
            {[
              {
                question: "Do you link to my bank account?",
                answer: "No, never. Unlike apps like Mint or YNAB that require bank linking via Plaid, Cardora only works with PDF statements that you manually upload. We never ask for your bank credentials or connect to your accounts."
              },
              {
                question: "Is my data secure?",
                answer: "Absolutely. Your data is encrypted using bank-level 256-bit encryption both in transit and at rest. We follow industry-leading security protocols and compliance standards. Plus, since we only see what you upload, you have complete control over your data exposure."
              },
              {
                question: "Can you access my bank accounts?",
                answer: "No. We have zero access to your bank accounts. We can only see the PDF statements you choose to upload. There's no way for us to view your real-time balances, initiate transactions, or access your account in any way."
              },
              {
                question: "How does the AI extraction work?",
                answer: "Our AI uses advanced machine learning models to read your PDF statements and extract transaction details with 93% accuracy. It identifies dates, merchants, amounts, and categories automatically, saving you hours of manual data entry."
              },
              {
                question: "What banks do you support?",
                answer: "We support PDF statements from all major banks and credit card issuers. Since you're uploading PDFs directly, it doesn't matter which bank you use - if they provide PDF statements, we can extract the data."
              },
              {
                question: "Is it really free?",
                answer: "Yes! Cardora is free to use. No credit card required, no hidden fees. We believe everyone deserves privacy-first financial tools without compromising their budget."
              },
              {
                question: "How is this different from manual tracking in Excel?",
                answer: "While you could manually enter transactions into Excel, Cardora's AI automatically extracts all transactions from your PDFs in seconds. Plus, you get beautiful visualizations, spending insights, category analysis, and trend detection that would take hours to build manually."
              },
              {
                question: "Do you sell my data?",
                answer: "Absolutely not. We never sell, share, or monetize your financial data. Your privacy is our core value. Your data belongs to you and only you."
              }
            ].map((faq, index) => (
              <FAQItem
                key={index}
                question={faq.question}
                answer={faq.answer}
                isOpen={openFAQ === index}
                onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative fintech-card card-accent-indigo p-16 text-center overflow-hidden"
          >
            {/* Subtle animated background */}
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.05, 0.1, 0.05],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="absolute inset-0 bg-gradient-to-r from-primary to-accent blur-3xl"
            />

            <div className="relative z-10">
              <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
                Ready to take control?
              </h2>
              <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
                Join thousands of privacy-conscious users managing their finances without compromising their data.
              </p>
              <Link
                href="/register"
                className="group inline-flex items-center gap-3 px-10 py-5 rounded-xl gradient-indigo-purple text-white font-bold text-lg shadow-lg btn-hover"
              >
                Start Analyzing - No Bank Login Required
                <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
              </Link>
              <p className="mt-6 text-muted-foreground text-sm">No credit card required • No bank linking • Free forever</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 border-t border-border bg-card">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
            <div>
              <h3 className="text-2xl font-bold text-primary mb-2">
                CARDORA
              </h3>
              <p className="text-muted-foreground mb-4">Privacy-first financial management</p>
              {/* Trust Badges */}
              <div className="flex flex-wrap gap-3">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg glass-effect border border-border text-xs">
                  <Shield className="w-3 h-3 text-emerald-500" />
                  <span className="text-muted-foreground">256-bit Encryption</span>
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg glass-effect border border-border text-xs">
                  <Lock className="w-3 h-3 text-emerald-500" />
                  <span className="text-muted-foreground">Zero Bank Access</span>
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg glass-effect border border-border text-xs">
                  <Check className="w-3 h-3 text-emerald-500" />
                  <span className="text-muted-foreground">GDPR Compliant</span>
                </div>
              </div>
            </div>
            <div className="flex gap-8 text-muted-foreground">
              <Link href="/privacy" className="hover:text-foreground transition-colors font-medium">Privacy</Link>
              <Link href="/terms" className="hover:text-foreground transition-colors font-medium">Terms</Link>
              <Link href="/contact" className="hover:text-foreground transition-colors font-medium">Contact</Link>
              <Link href="/about" className="hover:text-foreground transition-colors font-medium">About</Link>
            </div>
          </div>
          <div className="text-center text-muted-foreground text-sm border-t border-border pt-8">
            © 2024 Cardora. All rights reserved. • Your data, your control, always.
          </div>
        </div>
      </footer>
    </div>
  );
}
