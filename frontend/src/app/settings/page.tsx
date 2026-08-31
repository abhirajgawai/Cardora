'use client';

import { useState } from 'react';
import { User, Shield, Bell, Tags, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import {
  AccountSettings,
  PrivacyDataSettings,
  NotificationSettings,
  CategorySettings,
} from '@/features/settings';

type TabId = 'account' | 'categories' | 'privacy' | 'notifications';

interface Tab {
  id: TabId;
  name: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabId>('account');

  const tabs: Tab[] = [
    {
      id: 'account',
      name: 'Account',
      icon: <User className="w-5 h-5" />,
      component: <AccountSettings />,
    },
    {
      id: 'categories',
      name: 'Categories',
      icon: <Tags className="w-5 h-5" />,
      component: <CategorySettings />,
    },
    {
      id: 'privacy',
      name: 'Privacy & Data',
      icon: <Shield className="w-5 h-5" />,
      component: <PrivacyDataSettings />,
    },
    {
      id: 'notifications',
      name: 'Notifications',
      icon: <Bell className="w-5 h-5" />,
      component: <NotificationSettings />,
    },
  ];

  const currentTab = tabs.find(tab => tab.id === activeTab);

  return (
    <div className="min-h-screen fintech-bg pb-20">
      {/* Header */}
      <div className="fintech-card rounded-none border-x-0 border-t-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
          <Link href="/dashboard" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-foreground mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account, privacy, and preferences
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 mt-6 sm:mt-8">
        <div className="grid lg:grid-cols-12 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-3">
            <nav className="fintech-card rounded-xl p-2 space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  {tab.icon}
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="lg:col-span-9">
            {currentTab?.component}
          </div>
        </div>
      </div>
    </div>
  );
}
