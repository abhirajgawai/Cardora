'use client';

import { motion } from 'framer-motion';
import {
  Download, Trash2, UserX, Shield, Database, FileX,
  CheckCircle2, XCircle, AlertTriangle, ArrowLeft, Info, ArrowRight, Lock
} from 'lucide-react';
import Link from 'next/link';

export default function DataTransparencyPage() {
  return (
    <div className="min-h-screen fintech-bg pb-20">
      {/* Header */}
      <div className="fintech-card rounded-none border-x-0 border-t-0">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <Link href="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-8 h-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Data Transparency</h1>
          </div>
          <p className="text-muted-foreground">
            See exactly what data we collect and what controls you'll have as a user.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-8">
        {/* Preview Notice */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fintech-card p-6 mb-8 border-primary/30 bg-primary/5"
        >
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">This is a Preview</h3>
              <p className="text-muted-foreground mb-4">
                This page shows you exactly what data controls you'll have as a Cardora user.
                These features are fully functional for registered users.
              </p>
              <Link
                href="/register"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl gradient-indigo-purple text-white font-semibold shadow-lg btn-hover"
              >
                Sign Up to Access Your Controls
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Trust Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="fintech-card p-6 mb-8 border-emerald-500/30 bg-emerald-500/5"
        >
          <div className="flex items-start gap-4">
            <CheckCircle2 className="w-6 h-6 text-emerald-500 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Your Data, Your Control</h3>
              <p className="text-muted-foreground">
                Unlike apps that link to your bank, we only store what you explicitly upload.
                You can export all your data or delete it permanently at any time. No questions asked.
              </p>
            </div>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* What We Store */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="fintech-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <Database className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-bold text-foreground">What We Store</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">Transactions</span>
                  </div>
                  <span className="text-sm text-muted-foreground italic">Your actual count</span>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">Statements Processed</span>
                  </div>
                  <span className="text-sm text-muted-foreground italic">Your actual count</span>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">Credit Cards</span>
                  </div>
                  <span className="text-sm text-muted-foreground italic">Your actual count</span>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">AI Insights</span>
                  </div>
                  <span className="text-sm text-muted-foreground italic">Your actual count</span>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">Categories</span>
                  </div>
                  <span className="text-2xl font-bold text-primary">21</span>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-foreground">Profile Data</span>
                  </div>
                  <span className="text-sm text-muted-foreground">Email, name, timezone</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* What We DON'T Store */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="fintech-card p-6 border-emerald-500/30">
              <div className="flex items-center gap-3 mb-6">
                <FileX className="w-6 h-6 text-emerald-500" />
                <h2 className="text-xl font-bold text-foreground">What We DON'T Store</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3 p-4 rounded-lg glass-effect bg-emerald-500/5">
                  <XCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground font-medium">Full Credit Card Numbers</p>
                    <p className="text-sm text-muted-foreground">We only store the last 4 digits for display</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg glass-effect bg-emerald-500/5">
                  <XCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground font-medium">Bank Passwords or Credentials</p>
                    <p className="text-sm text-muted-foreground">We never ask for or store banking credentials</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg glass-effect bg-emerald-500/5">
                  <XCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground font-medium">CVV or PIN Codes</p>
                    <p className="text-sm text-muted-foreground">Security codes are never extracted or stored</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg glass-effect bg-emerald-500/5">
                  <XCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground font-medium">PDF Files</p>
                    <p className="text-sm text-muted-foreground">Deleted within 1 minute after AI processing</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg glass-effect bg-emerald-500/5">
                  <XCircle className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-foreground font-medium">Your Real-Time Bank Balance</p>
                    <p className="text-sm text-muted-foreground">We have zero access to your live accounts</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Action Buttons Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <div className="fintech-card p-8">
            <h2 className="text-2xl font-bold text-foreground mb-2">Your Controls</h2>
            <p className="text-muted-foreground mb-6">Once you sign up, you'll have full access to these features:</p>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Export Data */}
              <div className="p-6 rounded-xl glass-effect border border-border opacity-75 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
                <div className="relative">
                  <Download className="w-8 h-8 text-primary mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">Export All Data</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Download all your data as JSON or CSV format
                  </p>
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm font-semibold">
                    <Lock className="w-4 h-4" />
                    Sign up to enable
                  </div>
                </div>
              </div>

              {/* Delete All Data */}
              <div className="p-6 rounded-xl glass-effect border border-border opacity-75 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent" />
                <div className="relative">
                  <Trash2 className="w-8 h-8 text-amber-500 mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">Delete All Data</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Permanently remove all transactions, cards, and insights
                  </p>
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/10 text-amber-500 text-sm font-semibold">
                    <Lock className="w-4 h-4" />
                    Sign up to enable
                  </div>
                </div>
              </div>

              {/* Delete Account */}
              <div className="p-6 rounded-xl glass-effect border border-border opacity-75 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-destructive/5 to-transparent" />
                <div className="relative">
                  <UserX className="w-8 h-8 text-destructive mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">Delete Account</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Permanently delete your account and all associated data
                  </p>
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-destructive/10 text-destructive text-sm font-semibold">
                    <Lock className="w-4 h-4" />
                    Sign up to enable
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Privacy Guarantees */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 grid md:grid-cols-3 gap-6"
        >
          <div className="fintech-card p-6 text-center border-emerald-500/30">
            <Shield className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
            <h3 className="font-bold text-foreground mb-2">Instant Access</h3>
            <p className="text-sm text-muted-foreground">
              Access your data controls immediately after signing up
            </p>
          </div>

          <div className="fintech-card p-6 text-center border-emerald-500/30">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
            <h3 className="font-bold text-foreground mb-2">No Questions Asked</h3>
            <p className="text-sm text-muted-foreground">
              Export or delete your data anytime without approval
            </p>
          </div>

          <div className="fintech-card p-6 text-center border-emerald-500/30">
            <Database className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
            <h3 className="font-bold text-foreground mb-2">Complete Export</h3>
            <p className="text-sm text-muted-foreground">
              Get all your data in machine-readable JSON format
            </p>
          </div>
        </motion.div>

        {/* Email Confirmation Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 fintech-card p-6 border-primary/30"
        >
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-primary mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Email Confirmations</h3>
              <p className="text-muted-foreground">
                You'll receive email confirmations for all data actions (export, delete, account deletion).
                This ensures you have a paper trail and proof of all data operations.
              </p>
            </div>
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-12 text-center"
        >
          <div className="fintech-card p-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Ready to take control of your data?
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Sign up now and get instant access to all these data controls.
            </p>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl gradient-indigo-purple text-white font-semibold text-lg shadow-lg btn-hover"
            >
              Create Your Account
              <ArrowRight className="w-5 h-5" />
            </Link>
            <p className="mt-4 text-muted-foreground text-sm">
              No credit card required • No bank linking • Free to use
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
