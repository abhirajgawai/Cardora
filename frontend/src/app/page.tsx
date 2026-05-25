'use client';

import { motion } from 'framer-motion';
import { ArrowRight, CreditCard, Sparkles, Shield, TrendingUp, Zap, Brain, FileText, BarChart3, Lock, Upload, Eye, X, Check, ChevronDown, ChevronUp, CheckCircle2, XCircle, FileX, Database, Info } from 'lucide-react';
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

      {/* Data Lifecycle Transparency Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-emerald-500/30 mb-6">
              <Shield className="w-5 h-5 text-emerald-500" />
              <span className="text-sm font-medium text-emerald-500">100% Transparent</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              What happens to your PDF?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Complete transparency about how we handle your sensitive documents
            </p>
          </motion.div>

          {/* Timeline Visualization */}
          <div className="max-w-5xl mx-auto">
            <div className="relative">
              {/* Vertical timeline line */}
              <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary via-accent to-emerald-500" />

              {/* Timeline Steps */}
              <div className="space-y-12">
                {/* Step 1: Upload */}
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                  className="relative flex items-center gap-8"
                >
                  <div className="hidden md:flex flex-1 justify-end">
                    <div className="fintech-card p-6 max-w-md border-primary/30">
                      <h3 className="text-xl font-bold text-foreground mb-2">1. You Upload PDF</h3>
                      <p className="text-muted-foreground">Your credit card statement is uploaded securely via encrypted connection (TLS 1.3)</p>
                    </div>
                  </div>
                  <div className="absolute left-8 md:left-1/2 transform md:-translate-x-1/2 w-16 h-16 rounded-full bg-primary flex items-center justify-center z-10 shadow-lg">
                    <Upload className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1 ml-24 md:ml-0">
                    <div className="fintech-card p-6 md:hidden border-primary/30">
                      <h3 className="text-xl font-bold text-foreground mb-2">1. You Upload PDF</h3>
                      <p className="text-muted-foreground">Your credit card statement is uploaded securely via encrypted connection (TLS 1.3)</p>
                    </div>
                  </div>
                </motion.div>

                {/* Step 2: Processing */}
                <motion.div
                  initial={{ opacity: 0, x: 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                  className="relative flex items-center gap-8"
                >
                  <div className="flex-1 mr-24 md:mr-0">
                    <div className="md:hidden" />
                  </div>
                  <div className="absolute left-8 md:left-1/2 transform md:-translate-x-1/2 w-16 h-16 rounded-full bg-accent flex items-center justify-center z-10 shadow-lg">
                    <Brain className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1 ml-24 md:ml-0">
                    <div className="fintech-card p-6 max-w-md border-accent/30">
                      <h3 className="text-xl font-bold text-foreground mb-2">2. AI Extracts Data (30-60 seconds)</h3>
                      <p className="text-muted-foreground">Processed in-memory only. We extract transactions, dates, amounts, and categories. Never saved to disk.</p>
                    </div>
                  </div>
                </motion.div>

                {/* Step 3: PDF Deleted */}
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="relative flex items-center gap-8"
                >
                  <div className="hidden md:flex flex-1 justify-end">
                    <div className="fintech-card p-6 max-w-md border-destructive/30 bg-destructive/5">
                      <h3 className="text-xl font-bold text-foreground mb-2">3. PDF DELETED (&lt; 1 minute)</h3>
                      <p className="text-muted-foreground">Your PDF is permanently deleted from our servers. No copies. No backups. Gone forever.</p>
                      <div className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-emerald-500">
                        <CheckCircle2 className="w-4 h-4" />
                        Automatically deleted
                      </div>
                    </div>
                  </div>
                  <div className="absolute left-8 md:left-1/2 transform md:-translate-x-1/2 w-16 h-16 rounded-full bg-destructive flex items-center justify-center z-10 shadow-lg">
                    <FileX className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1 ml-24 md:ml-0">
                    <div className="fintech-card p-6 md:hidden border-destructive/30 bg-destructive/5">
                      <h3 className="text-xl font-bold text-foreground mb-2">3. PDF DELETED (&lt; 1 minute)</h3>
                      <p className="text-muted-foreground">Your PDF is permanently deleted from our servers. No copies. No backups. Gone forever.</p>
                      <div className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-emerald-500">
                        <CheckCircle2 className="w-4 h-4" />
                        Automatically deleted
                      </div>
                    </div>
                  </div>
                </motion.div>

                {/* Step 4: Data Stored */}
                <motion.div
                  initial={{ opacity: 0, x: 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                  className="relative flex items-center gap-8"
                >
                  <div className="flex-1 mr-24 md:mr-0">
                    <div className="md:hidden" />
                  </div>
                  <div className="absolute left-8 md:left-1/2 transform md:-translate-x-1/2 w-16 h-16 rounded-full bg-secondary flex items-center justify-center z-10 shadow-lg">
                    <Database className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1 ml-24 md:ml-0">
                    <div className="fintech-card p-6 max-w-md border-secondary/30">
                      <h3 className="text-xl font-bold text-foreground mb-2">4. Only Transaction Data Stored</h3>
                      <p className="text-muted-foreground">We keep: dates, merchants, amounts, categories. We don't keep: full card numbers, CVV, passwords.</p>
                    </div>
                  </div>
                </motion.div>

                {/* Step 5: Your Control */}
                <motion.div
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="relative flex items-center gap-8"
                >
                  <div className="hidden md:flex flex-1 justify-end">
                    <div className="fintech-card p-6 max-w-md border-emerald-500/30 bg-emerald-500/5">
                      <h3 className="text-xl font-bold text-foreground mb-2">5. You Control Everything</h3>
                      <p className="text-muted-foreground">Export your data anytime. Delete it with one click. Close your account whenever you want.</p>
                      <div className="mt-4 flex gap-2">
                        <Link href="/data-transparency" className="text-sm font-semibold text-primary hover:underline">
                          View Data Controls →
                        </Link>
                      </div>
                    </div>
                  </div>
                  <div className="absolute left-8 md:left-1/2 transform md:-translate-x-1/2 w-16 h-16 rounded-full bg-emerald-500 flex items-center justify-center z-10 shadow-lg">
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1 ml-24 md:ml-0">
                    <div className="fintech-card p-6 md:hidden border-emerald-500/30 bg-emerald-500/5">
                      <h3 className="text-xl font-bold text-foreground mb-2">5. You Control Everything</h3>
                      <p className="text-muted-foreground">Export your data anytime. Delete it with one click. Close your account whenever you want.</p>
                      <div className="mt-4 flex gap-2">
                        <Link href="/data-transparency" className="text-sm font-semibold text-primary hover:underline">
                          View Data Controls →
                        </Link>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>

          {/* Key Guarantees */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 1 }}
            className="mt-20 grid md:grid-cols-3 gap-6 max-w-5xl mx-auto"
          >
            <div className="fintech-card p-6 text-center border-emerald-500/30">
              <XCircle className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
              <h3 className="font-bold text-foreground mb-2">No Long-Term Storage</h3>
              <p className="text-sm text-muted-foreground">Your PDF exists on our servers for less than 1 minute</p>
            </div>
            <div className="fintech-card p-6 text-center border-emerald-500/30">
              <Eye className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
              <h3 className="font-bold text-foreground mb-2">Full Transparency</h3>
              <p className="text-sm text-muted-foreground">See exactly what data we have about you</p>
            </div>
            <div className="fintech-card p-6 text-center border-emerald-500/30">
              <Shield className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
              <h3 className="font-bold text-foreground mb-2">Your Control</h3>
              <p className="text-sm text-muted-foreground">Export or delete all data with one click</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Join Beta Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-primary/30 mb-6">
              <Sparkles className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-primary">Early Access</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Join the privacy revolution
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
              Be among the first to experience truly private financial management. No testimonials yet—because we're putting real users first, not fake reviews.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="group px-8 py-4 rounded-xl gradient-indigo-purple text-white font-semibold text-lg shadow-lg btn-hover flex items-center justify-center gap-2"
              >
                Get Early Access
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </motion.div>
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

      {/* Why Free Section */}
      <section className="relative py-32 px-6 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-primary/30 mb-6">
              <Info className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-primary">Honest Answer</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-foreground">
              "Why is Cardora free?"
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              The question everyone asks. Here's the honest truth.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="fintech-card p-10 border-primary/30"
          >
            <div className="space-y-6 text-lg leading-relaxed">
              <p className="text-foreground">
                <strong>Great question.</strong> Most people are rightfully suspicious of "free" apps in the finance space.
              </p>

              <div className="p-6 rounded-xl glass-effect border border-primary/20 bg-primary/5">
                <p className="text-foreground mb-3">
                  <strong className="text-primary text-xl">The Honest Answer:</strong>
                </p>
                <p className="text-muted-foreground">
                  Cardora is a passion project built to solve a real problem: tracking spending without handing over bank credentials. Right now, it's free because we're in early access and focused on building the best privacy-first financial tool possible.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mt-8">
                <div className="p-6 rounded-xl glass-effect border border-emerald-500/20">
                  <h3 className="text-xl font-bold text-foreground mb-3 flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                    Future Plans
                  </h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Core features stay free forever</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Premium features for power users (multi-year trends, family accounts)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Business accounts for financial advisors</span>
                    </li>
                  </ul>
                </div>

                <div className="p-6 rounded-xl glass-effect border border-destructive/20">
                  <h3 className="text-xl font-bold text-foreground mb-3 flex items-center gap-2">
                    <XCircle className="w-6 h-6 text-destructive" />
                    What We'll NEVER Do
                  </h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <span className="text-destructive">✗</span>
                      <span>Sell your transaction data</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-destructive">✗</span>
                      <span>Show targeted ads based on spending</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-destructive">✗</span>
                      <span>Share data with third parties</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="mt-8 p-6 rounded-xl bg-primary/5 border border-primary/20">
                <p className="text-center text-foreground text-xl font-bold">
                  No VC funding = No pressure to monetize your privacy
                </p>
                <p className="text-center text-muted-foreground mt-2">
                  We're building this the right way, not the fast way.
                </p>
              </div>
            </div>
          </motion.div>
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
              <Link href="/data-transparency" className="hover:text-foreground transition-colors font-medium">Data Controls</Link>
              <Link href="/about" className="hover:text-foreground transition-colors font-medium">About</Link>
              <Link href="/privacy" className="hover:text-foreground transition-colors font-medium">Privacy</Link>
              <Link href="/terms" className="hover:text-foreground transition-colors font-medium">Terms</Link>
              <Link href="/contact" className="hover:text-foreground transition-colors font-medium">Contact</Link>
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
