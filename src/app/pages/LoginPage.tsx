import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Mail, Lock, Loader2, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import API from '../../config/api';
import { setToken, setUser } from '../../config/auth';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  // Google OAuth callback
  const handleGoogleResponse = useCallback(async (response: any) => {
    setError('');
    setGoogleLoading(true);
    try {
      const res = await fetch(API.googleAuth, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || 'Google sign-in failed');
        setGoogleLoading(false);
        return;
      }
      setToken(data.token);
      setUser(data.user);
      setGoogleLoading(false);
      navigate('/scan');
    } catch {
      setError('Network error. Please try again.');
      setGoogleLoading(false);
    }
  }, [navigate]);

  // Load Google Identity Services SDK
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = () => {
      (window as any).google?.accounts?.id?.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
      });
      const btnContainer = document.getElementById('google-signin-btn');
      if (btnContainer) {
        (window as any).google?.accounts?.id?.renderButton(btnContainer, {
          theme: 'filled_black',
          size: 'large',
          width: '100%',
          text: 'continue_with',
          shape: 'pill',
        });
      }
    };
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, [handleGoogleResponse]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch(API.login, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Login failed');
        setLoading(false);
        return;
      }

      setToken(data.token);
      setUser(data.user);
      setLoading(false);
      navigate('/scan');
    } catch {
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg flex items-center justify-center p-6">
      <div className="absolute top-[20%] left-[30%] w-[500px] h-[500px] bg-cyber-purple/[0.04] rounded-full blur-[150px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-[420px]"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <div className="w-10 h-10 rounded-xl bg-cyber-purple/15 border border-cyber-purple/30 flex items-center justify-center">
            <Shield className="w-5 h-5 text-cyber-purple" />
          </div>
          <span className="text-[20px] font-bold text-white">
            Web<span className="text-cyber-purple">Sec</span> AI
          </span>
        </div>

        {/* Card */}
        <div className="glass-card-strong rounded-2xl p-8 border border-white/[0.06]">
          <h1 className="text-[24px] font-bold text-white text-center mb-1">Welcome Back</h1>
          <p className="text-[14px] text-cyber-text-muted text-center mb-7">Sign in to your account</p>

          {error && (
            <div className="mb-4 px-4 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-[13px] text-red-400">
              {error}
            </div>
          )}

          {/* Google Sign-In */}
          {GOOGLE_CLIENT_ID && (
            <>
              <div className="mb-4 flex justify-center">
                {googleLoading ? (
                  <div className="w-full py-3.5 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center gap-2 text-white/70 text-[14px]">
                    <Loader2 className="w-4 h-4 animate-spin" /> Signing in with Google...
                  </div>
                ) : (
                  <div id="google-signin-btn" className="w-full flex justify-center" />
                )}
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1 h-px bg-white/10" />
                <span className="text-[12px] text-cyber-text-muted uppercase tracking-wider">or</span>
                <div className="flex-1 h-px bg-white/10" />
              </div>
            </>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] text-cyber-text-muted mb-1.5 uppercase tracking-wider">Email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-cyber-text-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  placeholder="you@example.com"
                  className="w-full pl-11 pr-4 py-3 bg-cyber-surface border border-cyber-border rounded-xl text-[14px] text-white placeholder:text-cyber-text-muted focus:border-cyber-purple/50 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] text-cyber-text-muted mb-1.5 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-cyber-text-muted" />
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-cyber-surface border border-cyber-border rounded-xl text-[14px] text-white placeholder:text-cyber-text-muted focus:border-cyber-purple/50 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ boxShadow: '0 0 30px rgba(139,92,246,0.4)' }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3.5 bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl text-[15px] font-semibold text-white shadow-[0_0_20px_rgba(139,92,246,0.25)] disabled:opacity-50 flex items-center justify-center gap-2 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              {loading ? 'Signing in...' : 'Sign In'}
            </motion.button>
          </form>

          <p className="text-[13px] text-cyber-text-muted text-center mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-cyber-purple hover:text-cyber-glow transition-colors font-medium">
              Register
            </Link>
          </p>
        </div>

        {/* Guest option */}
        <p className="text-[12px] text-cyber-text-muted text-center mt-5">
          Or{' '}
          <Link to="/scan" className="text-cyber-text-dim hover:text-white transition-colors">
            continue as guest
          </Link>
          {' '}(Quick scan only)
        </p>
      </motion.div>
    </div>
  );
}
