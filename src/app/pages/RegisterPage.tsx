import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Mail, Lock, User, Loader2, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import API from '../../config/api';
import { setToken, setUser } from '../../config/auth';

export function RegisterPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(API.register, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Registration failed');
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
      <div className="absolute top-[20%] right-[30%] w-[500px] h-[500px] bg-cyber-neon/[0.04] rounded-full blur-[150px] pointer-events-none" />

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
          <h1 className="text-[24px] font-bold text-white text-center mb-1">Create Account</h1>
          <p className="text-[14px] text-cyber-text-muted text-center mb-7">Unlock full scanning capabilities</p>

          {error && (
            <div className="mb-4 px-4 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-[13px] text-red-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] text-cyber-text-muted mb-1.5 uppercase tracking-wider">Name</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-cyber-text-muted" />
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                  placeholder="Your name"
                  className="w-full pl-11 pr-4 py-3 bg-cyber-surface border border-cyber-border rounded-xl text-[14px] text-white placeholder:text-cyber-text-muted focus:border-cyber-purple/50 focus:outline-none transition-colors"
                />
              </div>
            </div>

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
                  placeholder="Min 6 characters"
                  className="w-full pl-11 pr-4 py-3 bg-cyber-surface border border-cyber-border rounded-xl text-[14px] text-white placeholder:text-cyber-text-muted focus:border-cyber-purple/50 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] text-cyber-text-muted mb-1.5 uppercase tracking-wider">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-cyber-text-muted" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  required
                  placeholder="Repeat password"
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
              {loading ? 'Creating account...' : 'Create Account'}
            </motion.button>
          </form>

          <p className="text-[13px] text-cyber-text-muted text-center mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-cyber-purple hover:text-cyber-glow transition-colors font-medium">
              Sign In
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
