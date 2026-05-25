'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Clock, Save } from 'lucide-react';
import { getCurrentUser } from '@/features/auth';
import { User as UserType } from '@/features/auth/types';

export default function AccountSettings() {
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch user:', error);
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleSave = () => {
    setSaving(true);
    // TODO: Implement API call to update user profile
    setTimeout(() => {
      setSaving(false);
      alert('Profile updated successfully!');
    }, 1000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-muted-foreground">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fintech-card p-8"
      >
        <h2 className="text-2xl font-bold text-foreground mb-6">Profile Information</h2>

        <div className="space-y-6">
          {/* Full Name */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <User className="w-4 h-4" />
              Full Name
            </label>
            <input
              type="text"
              defaultValue={user?.full_name || ''}
              className="w-full px-4 py-3 rounded-xl glass-effect border border-border focus:border-primary focus:outline-none transition-colors"
              placeholder="Enter your full name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <Mail className="w-4 h-4" />
              Email Address
            </label>
            <input
              type="email"
              defaultValue={user?.email || ''}
              className="w-full px-4 py-3 rounded-xl glass-effect border border-border bg-muted/50 cursor-not-allowed"
              placeholder="your@email.com"
              disabled
            />
            <p className="text-xs text-muted-foreground mt-2">
              Email cannot be changed. Contact support if you need to update it.
            </p>
          </div>

          {/* Timezone */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <Clock className="w-4 h-4" />
              Timezone
            </label>
            <select
              defaultValue={user?.timezone || 'UTC'}
              className="w-full px-4 py-3 rounded-xl glass-effect border border-border focus:border-primary focus:outline-none transition-colors"
            >
              <option value="UTC">UTC (GMT+0)</option>
              <option value="America/New_York">Eastern Time (GMT-5)</option>
              <option value="America/Chicago">Central Time (GMT-6)</option>
              <option value="America/Denver">Mountain Time (GMT-7)</option>
              <option value="America/Los_Angeles">Pacific Time (GMT-8)</option>
              <option value="Europe/London">London (GMT+0)</option>
              <option value="Europe/Paris">Paris (GMT+1)</option>
              <option value="Asia/Tokyo">Tokyo (GMT+9)</option>
              <option value="Australia/Sydney">Sydney (GMT+10)</option>
            </select>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Account Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fintech-card p-8"
      >
        <h2 className="text-2xl font-bold text-foreground mb-6">Account Information</h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl glass-effect">
            <div>
              <p className="text-sm text-muted-foreground">Account Created</p>
              <p className="text-foreground font-semibold">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'N/A'}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl glass-effect">
            <div>
              <p className="text-sm text-muted-foreground">Account Status</p>
              <p className="text-foreground font-semibold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                Active
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
