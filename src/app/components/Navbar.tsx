import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Menu, X, Clock, LogOut, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { isLoggedIn, getUser, logout } from '../../config/auth';

const navLinks = [
  { label: 'Platform', href: '#features' },
  { label: 'Solutions', href: '#how-it-works' },
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Docs', href: '#' },
];

export function Navbar() {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const loggedIn = isLoggedIn();
  const user = getUser();

  const handleLogout = () => {
    logout();
    navigate('/');
    // Force re-render by reloading
    window.location.reload();
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-cyber-dark/60 backdrop-blur-2xl border-b border-white/[0.04] shadow-[0_4px_30px_rgba(0,0,0,0.3)]">
      <div className="max-w-[1320px] mx-auto px-6 h-[72px] flex items-center justify-between">

        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5 group" onClick={() => navigate('/')}>
          <div className="w-9 h-9 rounded-lg bg-cyber-purple/15 border border-cyber-purple/30 flex items-center justify-center group-hover:shadow-[0_0_20px_rgba(139,92,246,0.3)] transition-all duration-300">
            <Shield className="w-5 h-5 text-cyber-purple" />
          </div>
          <span className="text-[18px] font-bold text-white tracking-tight">
            Web<span className="text-cyber-purple">Sec</span> AI
          </span>
        </a>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map(link => (
            <a
              key={link.label}
              href={link.href}
              className="px-4 py-2 text-[14px] text-cyber-text-dim hover:text-white rounded-lg hover:bg-white/[0.04] transition-all duration-200"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Desktop CTA */}
        <div className="hidden lg:flex items-center gap-3">
          {loggedIn ? (
            <>
              {/* User info */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyber-surface/50 border border-cyber-border">
                <User className="w-3.5 h-3.5 text-cyber-purple" />
                <span className="text-[13px] text-cyber-text-dim">{user?.name}</span>
              </div>

              <button
                onClick={() => navigate('/history')}
                className="flex items-center gap-1.5 px-4 py-2 text-[14px] text-cyber-text-dim hover:text-white transition-colors"
              >
                <Clock className="w-3.5 h-3.5" />
                History
              </button>

              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-2 text-[13px] text-cyber-text-muted hover:text-red-400 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>

              <motion.button
                whileHover={{ boxShadow: '0 0 30px rgba(139,92,246,0.5)' }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/scan')}
                className="px-5 py-2.5 text-[14px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_40px_rgba(139,92,246,0.5)] transition-all duration-300"
              >
                Start Scan
              </motion.button>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 text-[14px] text-cyber-text-dim hover:text-white transition-colors"
              >
                Login
              </button>
              <motion.button
                whileHover={{ boxShadow: '0 0 30px rgba(139,92,246,0.5)' }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/scan')}
                className="px-5 py-2.5 text-[14px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_40px_rgba(139,92,246,0.5)] transition-all duration-300"
              >
                Start Scan
              </motion.button>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="lg:hidden text-white p-2" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-cyber-surface border-b border-cyber-border overflow-hidden"
          >
            <div className="px-6 py-4 space-y-1">
              {navLinks.map(link => (
                <a key={link.label} href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="block px-4 py-3 text-[15px] text-cyber-text-dim hover:text-white hover:bg-white/[0.04] rounded-lg transition-colors"
                >
                  {link.label}
                </a>
              ))}
              {loggedIn && (
                <a onClick={() => { setMobileOpen(false); navigate('/history'); }}
                  className="block px-4 py-3 text-[15px] text-cyber-text-dim hover:text-white hover:bg-white/[0.04] rounded-lg transition-colors cursor-pointer"
                >
                  📋 Scan History
                </a>
              )}
              <div className="pt-3 border-t border-cyber-border mt-2 space-y-2">
                {loggedIn ? (
                  <>
                    <button onClick={() => { setMobileOpen(false); navigate('/scan'); }}
                      className="w-full py-3 text-[15px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl">
                      Start Scan
                    </button>
                    <button onClick={() => { setMobileOpen(false); handleLogout(); }}
                      className="w-full py-3 text-[15px] text-red-400 hover:text-red-300">
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <button onClick={() => { setMobileOpen(false); navigate('/login'); }}
                      className="w-full py-3 text-[15px] text-cyber-text-dim hover:text-white">
                      Login
                    </button>
                    <button onClick={() => { setMobileOpen(false); navigate('/scan'); }}
                      className="w-full py-3 text-[15px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl">
                      Start Scan
                    </button>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
