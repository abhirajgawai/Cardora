'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/api/auth';
import { uploadStatement } from '@/lib/api/statements';
import { User, StatementUploadResponse } from '@/models';
import { extractErrorMessage, isAuthError } from '@/lib/utils/errorHandler';
import Sidebar from '@/components/layout/Sidebar';
import Footer from '@/components/layout/Footer';
import UploadZone from '@/components/upload/UploadZone';
import UploadProgress from '@/components/upload/UploadProgress';
import UploadResults from '@/components/upload/UploadResults';

type UploadStage = 'idle' | 'uploading' | 'extracting' | 'processing' | 'complete' | 'error';

export default function UploadPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadStage, setUploadStage] = useState<UploadStage>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<StatementUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Failed to load user:', extractErrorMessage(error));
        if (isAuthError(error)) {
          localStorage.removeItem('access_token');
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setUploadStage('uploading');
    setUploadProgress(0);

    try {
      // Start upload
      setUploadProgress(10);

      // Simulate progress stages
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev < 30) return prev + 5;
          return prev;
        });
      }, 200);

      // Upload file
      const result = await uploadStatement(file, (progress) => {
        setUploadProgress(Math.min(30, progress)); // Upload is 0-30%
      });

      clearInterval(progressInterval);

      // Simulate extraction stage (30-60%)
      setUploadStage('extracting');
      for (let i = 30; i <= 60; i += 5) {
        setUploadProgress(i);
        await new Promise((resolve) => setTimeout(resolve, 150));
      }

      // Simulate processing stage (60-100%)
      setUploadStage('processing');
      for (let i = 60; i <= 100; i += 5) {
        setUploadProgress(i);
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      // Complete
      setUploadStage('complete');
      setUploadProgress(100);
      setUploadResult(result);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStage('error');
      setError(extractErrorMessage(error));
    }
  };

  const handleUploadAnother = () => {
    setUploadStage('idle');
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadResult(null);
    setError(null);
  };

  const handleCancelUpload = () => {
    // In a real implementation, you would abort the upload request here
    handleUploadAnother();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen fintech-bg">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content - offset by sidebar width (256px = w-64) */}
      <div className="flex-1 ml-64">
        {/* Header */}
        <header className="bg-card border-b border-border px-8 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-1">Upload Statement</h1>
              <p className="text-muted-foreground">
                Upload your PDF credit card statement and let AI extract all transactions
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-semibold text-foreground">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
                {user?.full_name?.charAt(0).toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        {/* Upload Content */}
        <main className="px-8 py-5">
          <div className="max-w-4xl mx-auto">
            {/* Hero Section */}
            <div className="text-center mb-10 animate-fade-in">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
                <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-3">
                AI-Powered Statement Extraction
              </h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                Upload your PDF credit card statement and our AI will automatically extract all
                transactions with 93% accuracy.
              </p>
            </div>

            {/* Upload Area */}
            {uploadStage === 'idle' && (
              <UploadZone onFileSelect={handleFileSelect} disabled={false} />
            )}

            {/* Upload Progress */}
            {selectedFile && ['uploading', 'extracting', 'processing', 'complete'].includes(uploadStage) && (
              <UploadProgress
                fileName={selectedFile.name}
                fileSize={selectedFile.size}
                progress={uploadProgress}
                stage={uploadStage as 'uploading' | 'extracting' | 'processing' | 'complete'}
                onCancel={uploadStage !== 'complete' ? handleCancelUpload : undefined}
              />
            )}

            {/* Error Message */}
            {uploadStage === 'error' && error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 animate-fade-in">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-red-800 mb-1">Upload Failed</h3>
                    <p className="text-sm text-red-700 mb-4">{error}</p>
                    <button
                      onClick={handleUploadAnother}
                      className="px-4 py-2 bg-red-100 text-red-700 font-medium rounded-lg hover:bg-red-200 transition-colors"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Upload Results */}
            {uploadStage === 'complete' && uploadResult && (
              <UploadResults result={uploadResult} onUploadAnother={handleUploadAnother} />
            )}

            {/* Features Info */}
            <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                </div>
                <h4 className="font-semibold text-foreground mb-1">AI-Powered</h4>
                <p className="text-sm text-muted-foreground">
                  Claude AI extracts all transaction details automatically
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h4 className="font-semibold text-foreground mb-1">Lightning Fast</h4>
                <p className="text-sm text-muted-foreground">
                  Process statements in under 2 minutes
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                  </svg>
                </div>
                <h4 className="font-semibold text-foreground mb-1">Secure & Private</h4>
                <p className="text-sm text-muted-foreground">
                  Your data is encrypted and never shared
                </p>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
