/* eslint-disable react/no-unescaped-entities */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { login } from "@/features/auth";
import { extractErrorMessage } from "@/shared/lib/utils/errorHandler";
import GoogleSignInButton from "@/features/auth/components/GoogleSignInButton";

// Validation schema
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionExpired, setSessionExpired] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Check if redirected due to expired session
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('expired') === 'true') {
        setSessionExpired(true);
      }
    }
  }, []);

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError("");

    try {
      await login({
        username: data.email, // FastAPI expects 'username' field
        password: data.password,
      });

      // Check if there's a saved redirect path
      const redirectPath = localStorage.getItem('redirectAfterLogin');
      if (redirectPath) {
        localStorage.removeItem('redirectAfterLogin');
        router.push(redirectPath);
      } else {
        // Redirect to dashboard on success
        router.push("/dashboard");
      }
    } catch (err) {
      const errorMessage = extractErrorMessage(
        err,
        "Invalid email or password"
      );
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* LEFT PANEL - Brand & Visual */}
      <div className="hidden lg:flex lg:w-2/5 relative overflow-hidden gradient-navy-indigo">
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-64 h-64 bg-white rounded-full blur-3xl animate-float"></div>
          <div className="absolute bottom-20 right-10 w-80 h-80 bg-purple-300 rounded-full blur-3xl animate-float" style={{ animationDelay: "2s" }}></div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 py-12 text-white">
          {/* Logo */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold tracking-tight mb-3">
              CARDORA
            </h1>
            <p className="text-lg text-white/80">
              Smart way to manage your credit cards
            </p>
          </div>

          {/* Feature Highlights */}
          <div className="space-y-6">
            <div className="flex items-start space-x-4 glass-effect rounded-2xl p-5 animate-slide-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">AI-Powered PDF Extraction</h3>
                <p className="text-white/70 text-sm leading-relaxed">
                  Upload statements and let AI extract transactions automatically
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 glass-effect rounded-2xl p-5 animate-slide-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Smart Analytics</h3>
                <p className="text-white/70 text-sm leading-relaxed">
                  Visualize spending patterns with beautiful charts and insights
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 glass-effect rounded-2xl p-5 animate-slide-in" style={{ animationDelay: "0.3s" }}>
              <div className="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Auto-Categorization</h3>
                <p className="text-white/70 text-sm leading-relaxed">
                  93% accuracy in categorizing transactions automatically
                </p>
              </div>
            </div>
          </div>

          {/* Decorative Element */}
          <div className="mt-12 opacity-30">
            <svg className="w-full h-24" viewBox="0 0 200 100" fill="none">
              <path d="M0 50 Q 50 10, 100 50 T 200 50" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.3"/>
              <path d="M0 60 Q 50 20, 100 60 T 200 60" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.2"/>
            </svg>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - Login Form */}
      <div className="flex-1 flex items-center justify-center px-6 sm:px-12 lg:px-16 bg-card">
        <div className="w-full max-w-md animate-slide-in">
          {/* Header */}
          <div className="text-center lg:text-left mb-10">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground mb-3">
              Welcome back
            </h2>
            <p className="text-muted-foreground text-base">
              Sign in to your account to continue
            </p>
          </div>

          {/* Session Expired Message */}
          {sessionExpired && !error && (
            <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 animate-slide-in">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-amber-600 dark:text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-amber-800 dark:text-amber-400 font-medium">Your session expired. Please login again.</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 animate-slide-in">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-destructive flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-destructive font-medium">{error}</p>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email Field */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-foreground mb-2"
              >
                Email address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
                <input
                  id="email"
                  type="email"
                  {...register("email")}
                  className="w-full pl-12 pr-4 py-3.5 rounded-xl border-2 border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
                  placeholder="you@example.com"
                  suppressHydrationWarning
                />
              </div>
              {errors.email && (
                <p className="mt-2 text-sm text-destructive flex items-center space-x-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>{errors.email.message}</span>
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="password"
                  className="block text-sm font-semibold text-foreground"
                >
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  type="password"
                  {...register("password")}
                  className="w-full pl-12 pr-4 py-3.5 rounded-xl border-2 border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
                  placeholder="••••••••"
                />
              </div>
              {errors.password && (
                <p className="mt-2 text-sm text-destructive flex items-center space-x-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>{errors.password.message}</span>
                </p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                className="w-4 h-4 rounded border-input text-primary focus:ring-2 focus:ring-primary focus:ring-offset-0 transition-all"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-muted-foreground">
                Remember me for 30 days
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full gradient-indigo-purple text-white px-6 py-3.5 rounded-xl font-semibold shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed btn-hover transition-all duration-200"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                "Sign in"
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-card text-muted-foreground">Or continue with</span>
            </div>
          </div>

          {/* Google Sign In */}
          <GoogleSignInButton onError={setError} />

          {/* Sign Up Link */}
          <p className="mt-8 text-center text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link
              href="/register"
              className="font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              Sign up for free →
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
