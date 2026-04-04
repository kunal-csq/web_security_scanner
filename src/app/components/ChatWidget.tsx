import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, User, Shield, Minimize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import API from '../../config/api';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Focus input when opened
  useEffect(() => {
    if (open && !minimized) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [open, minimized]);

  const sendMessage = async () => {
    const msg = input.trim();
    if (!msg || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: msg };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(API.chat, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          history: messages.map(m => ({ role: m.role, content: m.content })),
        }),
      });

      const data = await res.json();

      if (res.ok && data.reply) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: data.error || 'Something went wrong. Please try again.' }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Network error. Please check your connection.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Format message content — handle code blocks
  const formatContent = (text: string) => {
    const parts = text.split(/(```[\s\S]*?```)/g);
    return parts.map((part, i) => {
      if (part.startsWith('```')) {
        const code = part.replace(/```\w*\n?/g, '').replace(/```$/g, '');
        return (
          <pre key={i} className="my-2 p-3 rounded-lg bg-black/40 border border-white/[0.06] overflow-x-auto text-[12px] font-mono text-emerald-300 leading-relaxed">
            {code.trim()}
          </pre>
        );
      }
      // Handle inline code
      const inlineParts = part.split(/(`[^`]+`)/g);
      return (
        <span key={i}>
          {inlineParts.map((ip, j) => {
            if (ip.startsWith('`') && ip.endsWith('`')) {
              return <code key={j} className="px-1.5 py-0.5 rounded bg-white/[0.06] text-[12px] font-mono text-cyber-glow">{ip.slice(1, -1)}</code>;
            }
            return <span key={j}>{ip}</span>;
          })}
        </span>
      );
    });
  };

  return (
    <>
      {/* FAB Button */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.08, boxShadow: '0 0 30px rgba(139,92,246,0.5)' }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl bg-gradient-to-br from-cyber-purple to-cyber-neon flex items-center justify-center shadow-[0_4px_20px_rgba(139,92,246,0.4)] group"
          >
            <MessageCircle className="w-6 h-6 text-white group-hover:rotate-12 transition-transform" />
            {/* Notification dot */}
            {messages.length === 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-400 border-2 border-cyber-dark flex items-center justify-center">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping absolute" />
              </span>
            )}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              height: minimized ? 56 : 520,
              width: minimized ? 220 : 400,
            }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className="fixed bottom-6 right-6 z-50 rounded-2xl overflow-hidden flex flex-col"
            style={{
              background: 'linear-gradient(145deg, rgba(18,18,30,0.97), rgba(12,12,22,0.99))',
              backdropFilter: 'blur(16px)',
              border: '1px solid rgba(139,92,246,0.12)',
              boxShadow: '0 16px 60px rgba(0,0,0,0.5), 0 0 20px rgba(139,92,246,0.08)',
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 h-14 border-b border-white/[0.06] flex-shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-cyber-purple/15 border border-cyber-purple/30 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-cyber-purple" />
                </div>
                <div>
                  <div className="text-[13px] font-semibold text-white leading-tight">WebGuard AI</div>
                  {!minimized && (
                    <div className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-[10px] text-cyber-text-muted">Security Expert</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setMinimized(!minimized)}
                  className="w-7 h-7 rounded-lg hover:bg-white/[0.06] flex items-center justify-center transition-colors"
                >
                  <Minimize2 className="w-3.5 h-3.5 text-cyber-text-muted" />
                </button>
                <button
                  onClick={() => { setOpen(false); setMinimized(false); }}
                  className="w-7 h-7 rounded-lg hover:bg-white/[0.06] flex items-center justify-center transition-colors"
                >
                  <X className="w-3.5 h-3.5 text-cyber-text-muted" />
                </button>
              </div>
            </div>

            {/* Body — only when not minimized */}
            {!minimized && (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4" style={{ scrollbarWidth: 'thin' }}>
                  {/* Welcome message */}
                  {messages.length === 0 && (
                    <div className="text-center py-6">
                      <div className="w-14 h-14 rounded-2xl bg-cyber-purple/10 border border-cyber-purple/20 flex items-center justify-center mx-auto mb-4">
                        <Shield className="w-7 h-7 text-cyber-purple" />
                      </div>
                      <h3 className="text-[15px] font-semibold text-white mb-2">Security Assistant</h3>
                      <p className="text-[12px] text-cyber-text-muted leading-relaxed max-w-[280px] mx-auto mb-4">
                        Ask me about web security vulnerabilities, fixes, server configs, or ecommerce protection.
                      </p>
                      <div className="flex flex-wrap gap-1.5 justify-center">
                        {['Fix SQL Injection', 'Harden Nginx', 'Secure cookies', 'CSP headers'].map(q => (
                          <button
                            key={q}
                            onClick={() => { setInput(q); setTimeout(() => inputRef.current?.focus(), 50); }}
                            className="px-2.5 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.06] text-[11px] text-cyber-text-dim hover:bg-cyber-purple/10 hover:border-cyber-purple/20 hover:text-cyber-glow transition-all"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      {msg.role === 'assistant' && (
                        <div className="w-6 h-6 rounded-md bg-cyber-purple/15 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <Bot className="w-3.5 h-3.5 text-cyber-purple" />
                        </div>
                      )}
                      <div
                        className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-[13px] leading-relaxed ${
                          msg.role === 'user'
                            ? 'bg-cyber-purple/20 text-white border border-cyber-purple/15'
                            : 'bg-white/[0.04] text-cyber-text-dim border border-white/[0.04]'
                        }`}
                      >
                        {msg.role === 'assistant'
                          ? <div className="whitespace-pre-wrap">{formatContent(msg.content)}</div>
                          : msg.content
                        }
                      </div>
                      {msg.role === 'user' && (
                        <div className="w-6 h-6 rounded-md bg-white/[0.06] flex items-center justify-center flex-shrink-0 mt-0.5">
                          <User className="w-3.5 h-3.5 text-cyber-text-muted" />
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Typing indicator */}
                  {loading && (
                    <div className="flex gap-2.5">
                      <div className="w-6 h-6 rounded-md bg-cyber-purple/15 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-3.5 h-3.5 text-cyber-purple" />
                      </div>
                      <div className="bg-white/[0.04] border border-white/[0.04] rounded-xl px-4 py-3 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyber-purple animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-cyber-purple animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 rounded-full bg-cyber-purple animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="px-3 pb-3 pt-1 flex-shrink-0">
                  <div className="flex items-center gap-2 p-1.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <input
                      ref={inputRef}
                      type="text"
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask about web security..."
                      disabled={loading}
                      className="flex-1 px-3 py-2 bg-transparent text-[13px] text-white placeholder:text-cyber-text-muted focus:outline-none disabled:opacity-50"
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={sendMessage}
                      disabled={!input.trim() || loading}
                      className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
                        input.trim() && !loading
                          ? 'bg-cyber-purple text-white shadow-[0_0_12px_rgba(139,92,246,0.3)]'
                          : 'bg-white/[0.04] text-cyber-text-muted'
                      }`}
                    >
                      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </motion.button>
                  </div>
                  <p className="text-[9px] text-cyber-text-muted text-center mt-1.5 opacity-60">
                    WebGuard AI • Web & Ecommerce Security Only
                  </p>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
