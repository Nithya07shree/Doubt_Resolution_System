'use client';

import React, { useState } from 'react';
import { Copy, Check, Clock, Cpu } from 'lucide-react';

interface AgentCardProps {
  title: string;
  agentName: string;
  icon: React.ReactNode;
  content: string;
  latencyMs?: number;
  tokens?: { prompt: number; completion: number };
  badge?: string;
  badgeColor?: string;
}

export default function AgentCard({
  title,
  agentName,
  icon,
  content,
  latencyMs,
  tokens,
  badge,
  badgeColor = "bg-brand-500/20 text-brand-300 border-brand-500/30"
}: AgentCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="glass-interactive rounded-2xl p-6 relative overflow-hidden group animate-slide-up">
      {/* Decorative gradient overlay */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-brand-500/10 to-transparent rounded-full blur-2xl pointer-events-none transition-all duration-300 group-hover:scale-125" />

      {/* Card Header */}
      <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-brand-400 group-hover:text-brand-300 transition-colors">
            {icon}
          </div>
          <div>
            <h3 className="font-semibold text-lg text-slate-100 group-hover:text-white transition-colors">
              {title}
            </h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              {agentName}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {badge && (
            <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${badgeColor}`}>
              {badge}
            </span>
          )}

          <button
            onClick={handleCopy}
            className="p-2 bg-slate-900/60 hover:bg-slate-800 rounded-lg border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 transition-all active:scale-95"
            title="Copy output to clipboard"
          >
            {copied ? (
              <Check className="h-4 w-4 text-emerald-400 animate-pulse" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans bg-slate-950/40 border border-slate-900 rounded-xl p-4 md:p-5 max-h-[380px] overflow-y-auto">
        {content}
      </div>

      {/* Footer Metrics */}
      {(latencyMs !== undefined || tokens) && (
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-slate-900/60 text-xs text-slate-400 font-mono">
          {latencyMs !== undefined && (
            <div className="flex items-center gap-1.5" title="Execution duration">
              <Clock className="h-3.5 w-3.5 text-slate-500" />
              <span>{(latencyMs / 1000.0).toFixed(2)}s</span>
            </div>
          )}
          {tokens && (
            <div className="flex items-center gap-1.5" title="Token consumption">
              <Cpu className="h-3.5 w-3.5 text-slate-500" />
              <span>
                {tokens.prompt + tokens.completion} tokens (In: {tokens.prompt} | Out: {tokens.completion})
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
