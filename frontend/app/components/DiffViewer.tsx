'use client';

import React from 'react';
import { PlusCircle, MinusCircle, HelpCircle } from 'lucide-react';

interface DiffChunk {
  type: 'added' | 'removed' | 'equal';
  text: string;
}

interface DiffViewerProps {
  diffOutput?: {
    words_added: number;
    words_removed: number;
    chunks: DiffChunk[];
  };
}

export default function DiffViewer({ diffOutput }: DiffViewerProps) {
  if (!diffOutput || !diffOutput.chunks || diffOutput.chunks.length === 0) {
    return (
      <div className="glass rounded-2xl p-6 text-center text-slate-400">
        <HelpCircle className="h-8 w-8 mx-auto mb-2 text-slate-600" />
        <p className="text-sm">No comparison data is available yet.</p>
      </div>
    );
  }

  const { words_added, words_removed, chunks } = diffOutput;

  return (
    <div className="glass rounded-2xl p-6 animate-slide-up relative overflow-hidden">
      {/* Visual background gradient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2/3 h-20 bg-gradient-to-b from-purple-500/5 to-transparent blur-3xl pointer-events-none" />

      {/* Header & Diff Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-900/60">
        <div>
          <h3 className="font-semibold text-lg text-slate-100">
            Simplification Transformation Diff
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Comparing Rigorous Academic Explanation to Analogy Simplification (Word-Level Tracker)
          </p>
        </div>

        {/* Word Diff Statistics */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 text-xs font-semibold font-mono">
            <PlusCircle className="h-3.5 w-3.5" />
            <span>+{words_added} words</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-950/40 border border-rose-500/20 text-rose-400 text-xs font-semibold font-mono">
            <MinusCircle className="h-3.5 w-3.5" />
            <span>-{words_removed} words</span>
          </div>
        </div>
      </div>

      {/* Guide Banner */}
      <div className="flex items-center gap-3 text-xs bg-slate-950/60 border border-slate-900 rounded-xl p-3 mb-5 text-slate-400">
        <span className="font-semibold text-slate-300">Legend:</span>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded bg-rose-500/30 border border-rose-500/40" />
          <span>Academic original (Removed)</span>
        </div>
        <div className="flex items-center gap-1.5 ml-2">
          <span className="inline-block w-2.5 h-2.5 rounded bg-emerald-500/30 border border-emerald-500/40" />
          <span>Simplified analog (Added)</span>
        </div>
      </div>

      {/* Interactive Render Area */}
      <div className="glass-interactive bg-slate-950/50 border border-slate-900 rounded-xl p-5 md:p-6 text-sm leading-relaxed whitespace-pre-wrap font-sans max-h-[450px] overflow-y-auto">
        <div className="flex flex-wrap items-baseline gap-y-1">
          {chunks.map((chunk, index) => {
            if (chunk.type === 'removed') {
              return (
                <span
                  key={index}
                  className="bg-rose-500/15 text-rose-300 border border-rose-500/20 px-1 py-0.5 rounded mx-0.5 break-words line-through selection:bg-rose-500/30 selection:text-white"
                >
                  {chunk.text}
                </span>
              );
            } else if (chunk.type === 'added') {
              return (
                <span
                  key={index}
                  className="bg-emerald-500/15 text-emerald-300 border border-emerald-500/20 px-1 py-0.5 rounded mx-0.5 break-words selection:bg-emerald-500/30 selection:text-white"
                >
                  {chunk.text}
                </span>
              );
            } else {
              return (
                <span key={index} className="text-slate-300 mx-0.5 break-words">
                  {chunk.text}
                </span>
              );
            }
          })}
        </div>
      </div>
    </div>
  );
}
