'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Mail, MessageSquare, CreditCard, TrendingUp, AlertCircle } from 'lucide-react';

interface NotificationPreference {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  enabled: boolean;
}

export default function NotificationSettings() {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([
    {
      id: 'transaction_alerts',
      title: 'Transaction Alerts',
      description: 'Get notified when new transactions are added to your account',
      icon: <CreditCard className="w-5 h-5" />,
      enabled: true,
    },
    {
      id: 'payment_reminders',
      title: 'Payment Reminders',
      description: 'Receive reminders for upcoming credit card payments',
      icon: <AlertCircle className="w-5 h-5" />,
      enabled: true,
    },
    {
      id: 'insights',
      title: 'AI Insights',
      description: 'Get personalized insights about your spending patterns',
      icon: <TrendingUp className="w-5 h-5" />,
      enabled: true,
    },
    {
      id: 'weekly_summary',
      title: 'Weekly Summary',
      description: 'Receive a weekly summary of your financial activity',
      icon: <Mail className="w-5 h-5" />,
      enabled: false,
    },
    {
      id: 'product_updates',
      title: 'Product Updates',
      description: 'Stay informed about new features and improvements',
      icon: <MessageSquare className="w-5 h-5" />,
      enabled: false,
    },
  ]);

  const togglePreference = (id: string) => {
    setPreferences(preferences.map(pref =>
      pref.id === id ? { ...pref, enabled: !pref.enabled } : pref
    ));
    // TODO: Implement API call to save preferences
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fintech-card p-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <Bell className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold text-foreground">Notification Preferences</h2>
        </div>

        <p className="text-muted-foreground mb-6">
          Manage how and when you receive notifications from Cardora
        </p>

        <div className="space-y-4">
          {preferences.map((pref) => (
            <motion.div
              key={pref.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-start justify-between p-4 rounded-xl glass-effect border border-border hover:border-primary/50 transition-colors"
            >
              <div className="flex items-start gap-4 flex-1">
                <div className="p-2 rounded-lg bg-primary/10 text-primary mt-1">
                  {pref.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-foreground font-semibold mb-1">{pref.title}</h3>
                  <p className="text-sm text-muted-foreground">{pref.description}</p>
                </div>
              </div>
              <button
                onClick={() => togglePreference(pref.id)}
                className={`
                  relative w-12 h-6 rounded-full transition-colors duration-200 flex-shrink-0 ml-4
                  ${pref.enabled ? 'bg-primary' : 'bg-muted'}
                `}
              >
                <span
                  className={`
                    absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform duration-200
                    ${pref.enabled ? 'translate-x-6' : 'translate-x-0'}
                  `}
                />
              </button>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Email Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fintech-card p-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <Mail className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold text-foreground">Email Preferences</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl glass-effect">
            <div>
              <h3 className="text-foreground font-semibold mb-1">Marketing Emails</h3>
              <p className="text-sm text-muted-foreground">Receive promotional content and special offers</p>
            </div>
            <button
              className="relative w-12 h-6 rounded-full bg-muted transition-colors duration-200 flex-shrink-0"
            >
              <span className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform duration-200" />
            </button>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl glass-effect">
            <div>
              <h3 className="text-foreground font-semibold mb-1">Security Alerts</h3>
              <p className="text-sm text-muted-foreground">Critical account security notifications (always enabled)</p>
            </div>
            <button
              disabled
              className="relative w-12 h-6 rounded-full bg-primary transition-colors duration-200 flex-shrink-0 opacity-50 cursor-not-allowed"
            >
              <span className="absolute top-0.5 right-0.5 w-5 h-5 bg-white rounded-full" />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
