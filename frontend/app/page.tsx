'use client';

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  BookOpen, 
  HelpCircle, 
  Terminal, 
  CheckCircle2, 
  ArrowRight, 
  History, 
  Brain, 
  Compass, 
  Activity, 
  ListFilter,
  Layers,
  ChevronRight,
  ShieldCheck,
  Zap,
  RotateCcw
} from 'lucide-react';

import AgentCard from './components/AgentCard';
import DiffViewer from './components/DiffViewer';

// API Server Address
const API_BASE_URL = 'http://localhost:8000';

interface HistoryItem {
  id: string;
  student_query: string;
  topic: string;
  skill_level: string;
  timestamp: string;
}

interface TokenMetrics {
  prompt: number;
  completion: number;
}

interface DoubtResolutionResponse {
  id: string;
  student_query: string;
  intent_output: {
    topic: string;
    skill_level: string;
    intent_type: string;
    key_terms: string[];
  };
  explanation_output: string;
  simplification_output: string;
  example_output: string;
  validation_output: {
    valid: boolean;
    score: number;
    feedback: string[];
  };
  diff_output: {
    words_added: number;
    words_removed: number;
    chunks: Array<{ type: 'added' | 'removed' | 'equal'; text: string }>;
  };
  token_counts: {
    intent_agent: TokenMetrics;
    explanation_agent: TokenMetrics;
    simplification_agent: TokenMetrics;
    example_agent: TokenMetrics;
    validation_agent: TokenMetrics;
    total: TokenMetrics;
  };
  execution_latency_ms: number;
  timestamp: string;
}

const LOADING_STEPS = [
  { id: 1, label: 'Profiling intent, core subject topic & skill tier...' },
  { id: 2, label: 'Authoring exhaustive, detailed academic explanation...' },
  { id: 3, label: 'Translating dense physics/formulas to friendly analogies...' },
  { id: 4, label: 'Creating code samples, calculations or step-by-step examples...' },
  { id: 5, label: 'Auditing complete structural quality and evaluating rules...' },
];

export default function Home() {
  const [studentQuery, setStudentQuery] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedResolution, setSelectedResolution] = useState<DoubtResolutionResponse | null>(null);
  
  // Pipeline Load State
  const [isLoading, setIsLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch initial history
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/resolutions`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Error reading resolution history: ", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Simulate loader progression while backend does the work
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadStep((prev) => {
          if (prev < LOADING_STEPS.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 2500);
    } else {
      setLoadStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  // Load a historic query
  const handleLoadHistory = async (id: string) => {
    setErrorMsg('');
    try {
      const res = await fetch(`${API_BASE_URL}/api/resolutions/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedResolution(data);
        // Pre-fill query input for fast editing if wanted
        setStudentQuery(data.student_query);
      } else {
        setErrorMsg("Failed to load resolution details.");
      }
    } catch (err) {
      setErrorMsg("Failed to reach server database.");
    }
  };

  // Submit Doubt Pipeline
  const handleResolveDoubt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentQuery || studentQuery.trim().length < 10) {
      setErrorMsg("Please enter a structured doubt with at least 10 characters.");
      return;
    }

    setIsLoading(true);
    setLoadStep(0);
    setErrorMsg('');
    setSelectedResolution(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_query: studentQuery })
      });

      if (res.ok) {
        const data = await res.json();
        setSelectedResolution(data);
        fetchHistory(); // Refresh history panel
      } else {
        const errData = await res.json().catch(() => ({}));
        setErrorMsg(errData.detail || "Agent pipeline encountered a structural validation error.");
      }
    } catch (err) {
      setErrorMsg("Server is currently offline. Please double-check backend status.");
    } finally {
      setIsLoading(false);
    }
  };

  // Custom styling utility for validation scores
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400 border-emerald-500/20 bg-emerald-950/30';
    if (score >= 80) return 'text-purple-400 border-purple-500/20 bg-purple-950/30';
    return 'text-amber-400 border-amber-500/20 bg-amber-950/30';
  };

  return (
    <div className="flex flex-col lg:flex-row min-h-screen text-slate-200">
      
      {/* Sidebar: Historical Resolutions List */}
      <aside className="w-full lg:w-80 bg-[#0b0e14] border-b lg:border-b-0 lg:border-r border-slate-900/60 p-6 flex flex-col shrink-0">
        <div className="flex items-center gap-2.5 mb-6">
          <History className="h-5 w-5 text-brand-400" />
          <h2 className="font-semibold text-lg text-slate-100">Doubt Log History</h2>
        </div>

        {/* List of past inquiries */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[300px] lg:max-h-none">
          {history.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm border border-dashed border-slate-900 rounded-xl">
              <Brain className="h-6 w-6 mx-auto mb-2 opacity-30" />
              <p>No queries logged yet</p>
            </div>
          ) : (
            history.map((item) => (
              <button
                key={item.id}
                onClick={() => handleLoadHistory(item.id)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all text-xs flex flex-col gap-2 ${
                  selectedResolution?.id === item.id
                    ? 'bg-brand-950/40 border-brand-500/40 shadow-[0_4px_20px_-10px_rgba(139,92,246,0.2)]'
                    : 'bg-slate-950/40 border-slate-900 hover:border-slate-800 hover:bg-slate-900/40'
                }`}
              >
                <div className="flex items-center justify-between gap-2 w-full text-[10px]">
                  <span className="font-mono text-brand-400 bg-brand-950/60 px-2 py-0.5 rounded border border-brand-500/10">
                    {item.topic}
                  </span>
                  <span className="text-slate-500 font-mono">
                    {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-slate-300 font-medium line-clamp-2 leading-relaxed">
                  {item.student_query}
                </p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                  <span>Level: {item.skill_level}</span>
                  <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
                </div>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main Panel */}
      <main className="flex-1 p-6 md:p-8 lg:p-10 max-w-6xl mx-auto w-full overflow-y-auto">
        
        {/* Hub Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-3.5">
            <div className="p-3 bg-brand-500/10 rounded-2xl border border-brand-500/20 text-brand-400">
              <Brain className="h-7 w-7 animate-pulse-slow" />
            </div>
            <div>
              <h1 className="font-bold text-2xl md:text-3xl text-slate-500 tracking-tight bg-gradient-to-r from-slate-100 to-indigo-200 bg-clip-text text-transparent">
                Multi-Agent Doubt Resolver
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Sequential Pipeline Translation & Quality Verification Core
              </p>
            </div>
          </div>
        </header>

        {/* Input doubt field form */}
        <section className="glass rounded-3xl p-6 md:p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/5 rounded-full blur-3xl pointer-events-none" />
          
          <form onSubmit={handleResolveDoubt}>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4.5 w-4.5 text-brand-400" />
              <label className="text-sm font-semibold text-slate-300">
                Submit Your Complex Academic Doubt
              </label>
            </div>

            <textarea
              value={studentQuery}
              onChange={(e) => setStudentQuery(e.target.value)}
              placeholder="e.g. Explain how index lookup works in B-Trees versus Hash Maps, why Hash Maps cannot serve range queries, and provide a concrete example."
              className="w-full h-32 bg-slate-950/60 border border-slate-900 focus:border-brand-500/50 rounded-2xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none transition-all resize-none shadow-inner"
              maxLength={4000}
            />

            <div className="flex items-center justify-between mt-4 flex-wrap gap-4">
              <div className="text-xs text-slate-500 font-mono">
                Min 10 characters • Sanitized Secure Prompts
              </div>

              <div className="flex items-center gap-3">
                {studentQuery.trim().length > 0 && (
                  <button
                    type="button"
                    onClick={() => setStudentQuery('')}
                    className="p-3 bg-slate-900/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-400 hover:text-slate-200 transition-all active:scale-95 flex items-center gap-2 text-xs"
                    title="Clear input fields"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    <span>Reset</span>
                  </button>
                )}

                <button
                  type="submit"
                  disabled={isLoading || studentQuery.trim().length < 10}
                  className="px-6 py-3 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:from-slate-900 disabled:to-slate-900 disabled:text-slate-600 text-white rounded-xl font-semibold text-sm transition-all active:scale-95 shadow-[0_4px_20px_-5px_rgba(139,92,246,0.3)] disabled:shadow-none flex items-center gap-2 border border-brand-500/20 disabled:border-slate-800"
                >
                  {isLoading ? 'Processing Pipeline...' : 'Deconstruct Doubt'}
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </form>

          {/* Validation/Connection Error Block */}
          {errorMsg && (
            <div className="mt-4 p-4 bg-rose-950/40 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex items-center gap-3 animate-fade-in">
              <span className="p-1.5 bg-rose-500/20 rounded-lg text-rose-400 font-bold font-mono">!</span>
              <div>
                <p className="font-semibold">Pipeline Alert</p>
                <p className="text-rose-400/90 mt-0.5">{errorMsg}</p>
              </div>
            </div>
          )}
        </section>

        {/* Dynamic Loading State Indicator */}
        {isLoading && (
          <section className="glass rounded-3xl p-6 md:p-8 mb-8 text-center animate-fade-in">
            <div className="flex flex-col items-center justify-center max-w-md mx-auto">
              <Brain className="h-10 w-10 text-brand-500 animate-pulse mb-4" />
              <h3 className="font-semibold text-slate-100 text-lg">Running Intelligent Agent Pipeline</h3>
              <p className="text-xs text-slate-400 mt-1">Executing a sequence of specialized AI LLMs with tenacity retries...</p>

              {/* Progress step bar list */}
              <div className="w-full space-y-3.5 mt-8 text-left">
                {LOADING_STEPS.map((step, idx) => {
                  const isFinished = idx < loadStep;
                  const isActive = idx === loadStep;
                  return (
                    <div
                      key={step.id}
                      className={`flex items-center gap-3.5 p-3 rounded-xl border transition-all duration-300 ${
                        isFinished 
                          ? 'bg-emerald-950/15 border-emerald-500/10 text-slate-400' 
                          : isActive 
                            ? 'bg-brand-950/30 border-brand-500/20 text-slate-100 shadow-md scale-[1.01]' 
                            : 'bg-slate-950/20 border-slate-900/60 text-slate-600'
                      }`}
                    >
                      <div className="shrink-0">
                        {isFinished ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                        ) : isActive ? (
                          <div className="h-5 w-5 rounded-full border-2 border-brand-400 border-t-transparent animate-spin" />
                        ) : (
                          <div className="h-5 w-5 rounded-full border border-slate-800 text-xs flex items-center justify-center font-mono font-bold">
                            {step.id}
                          </div>
                        )}
                      </div>
                      <span className="text-xs font-medium leading-normal">{step.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* Resolution Payload Presentation */}
        {selectedResolution && (
          <div className="space-y-8 animate-fade-in">
            
            {/* Header: Profiling & Metadata Metadata */}
            <section className="glass rounded-3xl p-6 relative overflow-hidden">
              {/* Intent profiling labels */}
              <div className="flex items-center gap-2 mb-4 flex-wrap text-xs font-mono">
                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
                  <Compass className="h-3.5 w-3.5 text-slate-500" />
                  <span>Topic: <b className="text-brand-300">{selectedResolution.intent_output?.topic}</b></span>
                </span>
                
                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
                  <Brain className="h-3.5 w-3.5 text-slate-500" />
                  <span>Skill Level: <b className="text-brand-300">{selectedResolution.intent_output?.skill_level}</b></span>
                </span>

                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
                  <Activity className="h-3.5 w-3.5 text-slate-500" />
                  <span>Style: <b className="text-brand-300">{selectedResolution.intent_output?.intent_type}</b></span>
                </span>

                <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
                  <Zap className="h-3.5 w-3.5 text-slate-500" />
                  <span>Latency: <b className="text-brand-300">{(selectedResolution.execution_latency_ms / 1000.0).toFixed(2)}s</b></span>
                </span>
              </div>

              {/* Display query */}
              <div className="p-4 bg-slate-950/60 border border-slate-900 rounded-2xl">
                <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-1.5">Submitted Doubt</h4>
                <p className="text-sm text-slate-200 leading-relaxed font-medium">
                  {selectedResolution.student_query}
                </p>
              </div>

              {/* Extraction Keywords */}
              {selectedResolution.intent_output?.key_terms && (
                <div className="flex items-center gap-2 mt-4 flex-wrap text-[11px] text-slate-400">
                  <span className="font-semibold text-slate-500 font-mono">Profiled Keywords:</span>
                  {selectedResolution.intent_output.key_terms.map((term, i) => (
                    <span key={i} className="px-2 py-0.5 bg-slate-900 border border-slate-800/80 rounded font-medium text-slate-300">
                      {term}
                    </span>
                  ))}
                </div>
              )}
            </section>

            {/* Validation Auditor Quality Report */}
            {selectedResolution.validation_output && (
              <section className="glass rounded-3xl p-6 relative overflow-hidden">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-900/60 mb-4">
                  <div className="flex items-center gap-3">
                    <ShieldCheck className="h-6 w-6 text-brand-400" />
                    <div>
                      <h3 className="font-semibold text-slate-100">Quality Validation Report</h3>
                      <p className="text-xs text-slate-400 mt-0.5">Automated assessment against completeness & pedagogical criteria</p>
                    </div>
                  </div>

                  <div className={`px-4 py-2 border rounded-xl flex items-center gap-2.5 font-mono text-sm font-bold ${getScoreColor(selectedResolution.validation_output.score)}`}>
                    <span>Structural Score:</span>
                    <span>{selectedResolution.validation_output.score}/100</span>
                  </div>
                </div>

                <div className="space-y-2.5">
                  {selectedResolution.validation_output.feedback.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-400">
                      <span className="inline-block w-1.5 h-1.5 bg-brand-500 rounded-full mt-1.5 shrink-0" />
                      <p className="leading-relaxed">{item}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Comparison Visual Diff Viewer */}
            <section>
              <DiffViewer diffOutput={selectedResolution.diff_output} />
            </section>

            {/* Stacked Agent Cards */}
            <section className="space-y-6">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-5 w-5 text-brand-400" />
                <h3 className="font-semibold text-lg text-slate-100">Agent Processing Pipeline Output</h3>
              </div>

              {/* 1. Academic Explanation Card */}
              <AgentCard
                title="Deep Technical Academic Explanation"
                agentName="ExplanationAgent"
                icon={<BookOpen className="h-5 w-5" />}
                content={selectedResolution.explanation_output}
                latencyMs={selectedResolution.execution_latency_ms * 0.4} // Split representational metrics
                tokens={selectedResolution.token_counts?.explanation_agent}
                badge="Academic Rigor"
              />

              {/* 2. Simplified Explanation & Analogy Card */}
              <AgentCard
                title="Simplified Concept & Physical Analogy"
                agentName="SimplificationAgent"
                icon={<Brain className="h-5 w-5" />}
                content={selectedResolution.simplification_output}
                latencyMs={selectedResolution.execution_latency_ms * 0.3}
                tokens={selectedResolution.token_counts?.simplification_agent}
                badge="Analogy Centric"
                badgeColor="bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
              />

              {/* 3. Actionable Example Card */}
              <AgentCard
                title="Step-by-Step Contextual Scenario Example"
                agentName="ExampleAgent"
                icon={<Terminal className="h-5 w-5" />}
                content={selectedResolution.example_output}
                latencyMs={selectedResolution.execution_latency_ms * 0.2}
                tokens={selectedResolution.token_counts?.example_agent}
                badge="Actionable Practical"
                badgeColor="bg-purple-500/20 text-purple-300 border-purple-500/30"
              />
            </section>
          </div>
        )}

      </main>
    </div>
  );
}
