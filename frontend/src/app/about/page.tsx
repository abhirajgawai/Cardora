'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Mail, Linkedin, Twitter, Github, Heart, Shield, Users, Target } from 'lucide-react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen fintech-bg">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass-effect border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 text-foreground hover:text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Home</span>
          </Link>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="text-2xl font-bold text-primary"
          >
            CARDORA
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">
              Built by someone who values
              <br />
              <span className="text-primary">privacy as much as you do</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Cardora is a passion project born from frustration with existing financial apps that demand too much access.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Founder Story Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="fintech-card p-12"
          >
            <div className="grid md:grid-cols-[300px,1fr] gap-12 items-start">
              {/* Profile Image Placeholder */}
              <div className="mx-auto md:mx-0">
                <div className="w-64 h-64 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                  <Users className="w-24 h-24 text-primary/40" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <p className="text-sm text-muted-foreground text-center px-4">
                      [Add your photo here]
                    </p>
                  </div>
                </div>
                {/* Social Links */}
                <div className="flex gap-4 justify-center mt-6">
                  <a href="mailto:your-email@example.com" className="w-10 h-10 rounded-lg glass-effect border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Mail className="w-5 h-5 text-muted-foreground" />
                  </a>
                  <a href="https://linkedin.com/in/yourprofile" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-lg glass-effect border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Linkedin className="w-5 h-5 text-muted-foreground" />
                  </a>
                  <a href="https://twitter.com/yourhandle" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-lg glass-effect border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Twitter className="w-5 h-5 text-muted-foreground" />
                  </a>
                  <a href="https://github.com/yourhandle" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-lg glass-effect border border-border flex items-center justify-center hover:border-primary transition-colors">
                    <Github className="w-5 h-5 text-muted-foreground" />
                  </a>
                </div>
              </div>

              {/* Story */}
              <div>
                <h2 className="text-3xl font-bold text-foreground mb-2">[Your Name]</h2>
                <p className="text-primary font-semibold mb-6">Founder & Developer</p>

                <div className="space-y-4 text-muted-foreground leading-relaxed">
                  <p>
                    <strong className="text-foreground">Hi, I'm [Your Name].</strong> I built Cardora because I was frustrated with apps like Mint and YNAB that required me to hand over my bank credentials to third-party services like Plaid.
                  </p>

                  <p>
                    As a <strong className="text-foreground">[your background - software engineer/privacy advocate/financial analyst/etc.]</strong>, I knew there had to be a better way to track spending without compromising privacy. Why should I give an app continuous access to all my accounts just to categorize transactions?
                  </p>

                  <p>
                    I spent <strong className="text-foreground">[X months/years]</strong> building Cardora to be the finance app I wished existed—one that respects your privacy, puts you in control, and still provides powerful insights through AI.
                  </p>

                  <p>
                    <strong className="text-foreground">The philosophy is simple:</strong> You upload statements when YOU want. We extract the data, give you insights, and you can delete everything whenever you want. No bank linking. No passwords stored. No continuous monitoring.
                  </p>

                  <p className="text-foreground font-semibold">
                    Your data belongs to you. Always.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="relative py-20 px-6 bg-muted/30">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-foreground">
              Our Mission & Values
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              What drives us and what we stand for
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: 'Privacy First',
                description: 'We will never compromise your privacy for convenience. Your financial data is yours alone, and we have no interest in selling it or sharing it.',
                color: 'emerald'
              },
              {
                icon: Heart,
                title: 'User Control',
                description: 'You decide what to share, when to share it, and when to delete it. We build features that empower you, not trap you.',
                color: 'primary'
              },
              {
                icon: Target,
                title: 'Transparency',
                description: 'No hidden agendas, no fine print tricks. We\'ll always be honest about what we do, how we do it, and why.',
                color: 'accent'
              }
            ].map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="fintech-card p-8 text-center"
              >
                <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl ${
                  value.color === 'emerald' ? 'bg-emerald-500/10' :
                  value.color === 'primary' ? 'bg-primary/10' :
                  'bg-accent/10'
                } flex items-center justify-center`}>
                  <value.icon className={`w-8 h-8 ${
                    value.color === 'emerald' ? 'text-emerald-500' :
                    value.color === 'primary' ? 'text-primary' :
                    'text-accent'
                  }`} />
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">{value.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Free Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="fintech-card p-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-foreground text-center">
              Why is Cardora free?
            </h2>

            <div className="space-y-4 text-muted-foreground leading-relaxed text-lg">
              <p>
                <strong className="text-foreground">Great question.</strong> Most people are suspicious of "free" apps (and they should be).
              </p>

              <p>
                Here's the honest answer: <strong className="text-foreground">[Choose one or customize based on your actual model]</strong>
              </p>

              {/* Option 1: Passion Project */}
              <div className="pl-6 border-l-2 border-primary/30 my-6">
                <p className="text-foreground font-semibold mb-2">Option A: This is a passion project</p>
                <p>
                  Cardora is a portfolio project and a tool I built for myself. I'm sharing it because I believe others want the same privacy-first approach. There's no business model yet—it's free because I believe in privacy-first tools being accessible.
                </p>
              </div>

              {/* Option 2: Freemium Future */}
              <div className="pl-6 border-l-2 border-accent/30 my-6">
                <p className="text-foreground font-semibold mb-2">Option B: Freemium model in the future</p>
                <p>
                  Cardora is free for personal use and always will be. In the future, I may offer premium features like multi-year trend analysis, family account sharing, or financial advisor integrations. But the core privacy-first experience will remain free forever.
                </p>
              </div>

              {/* Option 3: Other */}
              <div className="pl-6 border-l-2 border-emerald-500/30 my-6">
                <p className="text-foreground font-semibold mb-2">Option C: [Your custom explanation]</p>
                <p>
                  [Explain your actual business model or future plans here]
                </p>
              </div>

              <p className="text-foreground font-bold text-center mt-8 text-xl">
                What we will NEVER do: Sell your data or transaction history.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="relative py-20 px-6 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-foreground">
              Get in Touch
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Questions? Concerns? Feedback? I'd love to hear from you.
            </p>

            <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
              <a href="mailto:support@cardora.com" className="fintech-card p-6 hover:border-primary transition-colors group">
                <Mail className="w-8 h-8 text-primary mx-auto mb-3" />
                <p className="font-semibold text-foreground mb-1">General Inquiries</p>
                <p className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">support@cardora.com</p>
              </a>

              <a href="mailto:security@cardora.com" className="fintech-card p-6 hover:border-primary transition-colors group">
                <Shield className="w-8 h-8 text-emerald-500 mx-auto mb-3" />
                <p className="font-semibold text-foreground mb-1">Security Issues</p>
                <p className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">security@cardora.com</p>
              </a>
            </div>

            <div className="mt-12 p-6 rounded-xl glass-effect border border-border max-w-2xl mx-auto">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Location:</strong> [Your City, Country]<br />
                <strong className="text-foreground">Company:</strong> [Legal entity name, if registered]<br />
                <strong className="text-foreground">Founded:</strong> [Year]
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl font-bold mb-6 text-foreground">
              Ready to take control of your financial data?
            </h2>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl gradient-indigo-purple text-white font-semibold text-lg shadow-lg btn-hover"
            >
              Get Started Today
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
