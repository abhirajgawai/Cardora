'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Download, Trash2, UserX, Database, FileX,
  CheckCircle2, XCircle, AlertTriangle, Info
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface DataStats {
  transactions: number;
  statements: number;
  cards: number;
  insights: number;
  categories: number;
}

export default function PrivacyDataSettings() {
  const router = useRouter();
  const [dataStats, setDataStats] = useState<DataStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showAccountDeleteConfirm, setShowAccountDeleteConfirm] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Fetch user data statistics
    fetchDataStats();
  }, [router]);

  const fetchDataStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      // TODO: Implement actual API calls
      // For now, using placeholder data
      setDataStats({
        transactions: 0,
        statements: 0,
        cards: 0,
        insights: 0,
        categories: 21
      });
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data stats:', error);
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/export', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cardora-data-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        alert('Data exported successfully! Check your downloads folder.');
      } else {
        const error = await response.json();
        alert(`Failed to export data: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data. Please try again.');
    }
  };

  const handleDeleteAllData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/data', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('All your data has been permanently deleted. You will be redirected to the dashboard.');
        setShowDeleteConfirm(false);
        router.push('/dashboard');
      } else {
        const error = await response.json();
        alert(`Failed to delete data: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting data:', error);
      alert('Failed to delete data. Please try again.');
    }
  };

  const handleDeleteAccount = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/users/account', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        localStorage.removeItem('access_token');
        alert('Your account has been permanently deleted. You will be redirected to the homepage.');
        router.push('/');
      } else {
        const error = await response.json();
        alert(`Failed to delete account: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-muted-foreground">Loading your data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Trust Badge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fintech-card p-6 border-emerald-500/30 bg-emerald-500/5"
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

      <div className="grid lg:grid-cols-2 gap-6">
        {/* What We Store */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
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
                <span className="text-2xl font-bold text-primary">{dataStats?.transactions || 0}</span>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <span className="text-foreground">Statements Processed</span>
                </div>
                <span className="text-2xl font-bold text-primary">{dataStats?.statements || 0}</span>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <span className="text-foreground">Credit Cards</span>
                </div>
                <span className="text-2xl font-bold text-primary">{dataStats?.cards || 0}</span>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <span className="text-foreground">AI Insights</span>
                </div>
                <span className="text-2xl font-bold text-primary">{dataStats?.insights || 0}</span>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg glass-effect">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <span className="text-foreground">Categories</span>
                </div>
                <span className="text-2xl font-bold text-primary">{dataStats?.categories || 21}</span>
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
          transition={{ delay: 0.2 }}
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

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="fintech-card p-8">
          <h2 className="text-2xl font-bold text-foreground mb-6">Your Actions</h2>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Export Data */}
            <button
              onClick={handleExportData}
              className="p-6 rounded-xl glass-effect border border-border hover:border-primary transition-all group"
            >
              <Download className="w-8 h-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Export All Data</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Download all your data as JSON or CSV format
              </p>
              <div className="text-primary font-semibold text-sm">Download Now →</div>
            </button>

            {/* Delete All Data */}
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-6 rounded-xl glass-effect border border-border hover:border-amber-500 transition-all group"
            >
              <Trash2 className="w-8 h-8 text-amber-500 mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Delete All Data</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Permanently remove all transactions, cards, and insights
              </p>
              <div className="text-amber-500 font-semibold text-sm">Delete Data →</div>
            </button>

            {/* Delete Account */}
            <button
              onClick={() => setShowAccountDeleteConfirm(true)}
              className="p-6 rounded-xl glass-effect border border-border hover:border-destructive transition-all group"
            >
              <UserX className="w-8 h-8 text-destructive mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Delete Account</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Permanently delete your account and all associated data
              </p>
              <div className="text-destructive font-semibold text-sm">Delete Account →</div>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Privacy Note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="fintech-card p-6 border-primary/30"
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

      {/* Delete Data Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fintech-card p-8 max-w-md w-full"
          >
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-amber-500" />
              <h3 className="text-2xl font-bold text-foreground">Confirm Data Deletion</h3>
            </div>
            <p className="text-muted-foreground mb-6">
              This will permanently delete all your transactions, cards, statements, and insights.
              Your account will remain active, but all data will be gone.
            </p>
            <p className="text-foreground font-semibold mb-6">
              This action cannot be undone.
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 px-6 py-3 rounded-xl glass-effect border border-border hover:border-primary transition-colors font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAllData}
                className="flex-1 px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold transition-colors"
              >
                Delete All Data
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Delete Account Confirmation Modal */}
      {showAccountDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fintech-card p-8 max-w-md w-full border-destructive"
          >
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-destructive" />
              <h3 className="text-2xl font-bold text-foreground">Confirm Account Deletion</h3>
            </div>
            <p className="text-muted-foreground mb-4">
              This will permanently delete your account and ALL associated data including:
            </p>
            <ul className="list-disc list-inside text-muted-foreground mb-6 space-y-1">
              <li>All transactions</li>
              <li>All credit cards</li>
              <li>All statements</li>
              <li>All insights</li>
              <li>Your profile</li>
            </ul>
            <p className="text-destructive font-bold mb-6">
              This action is PERMANENT and cannot be undone.
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setShowAccountDeleteConfirm(false)}
                className="flex-1 px-6 py-3 rounded-xl glass-effect border border-border hover:border-primary transition-colors font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                className="flex-1 px-6 py-3 rounded-xl bg-destructive hover:bg-destructive/90 text-white font-semibold transition-colors"
              >
                Delete Account
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
