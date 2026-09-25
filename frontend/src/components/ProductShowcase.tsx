import React, { useState } from 'react'
import {
  Sparkles,
  Terminal,
  Unlock,
  CheckCircle,
  Copy,
  Check,
  Download,
  ExternalLink,
  ShieldCheck,
  Zap,
  Server,
  Play,
  ArrowRight,
  Boxes,
} from 'lucide-react'

export const ProductShowcase: React.FC = () => {
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null)
  const [activeAgentTab, setActiveAgentTab] = useState<'hermes' | 'pi' | 'claude' | 'ollama'>('hermes')

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCmd(id)
    setTimeout(() => setCopiedCmd(null), 2500)
  }

  const installCommand = 'curl -fsSL https://raw.githubusercontent.com/unrealandychan/open-factory-agent/main/install.sh | bash'

  return (
    <div className="space-y-24 py-6 font-sans">
      {/* Hero Section */}
      <section className="text-center relative max-w-4xl mx-auto px-4 pt-4">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-800/60 text-xs font-bold text-cyan-300 mb-6 shadow-inner">
          <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
          <span>100% Free &amp; Open Source • Zero Paywalls • MIT Licensed</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-[1.15]">
          The Flow Factory Idea,{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
            Liberated &amp; Open Sourced.
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          The 1:1 open-source alternative to proprietary workflow platforms. Run unlimited factories, execute Python scripts,
          and orchestrate local AI agents (<span className="text-cyan-300 font-semibold">Hermes, Pi, Claude Code, Ollama</span>)
          with live streaming logs on your own machine.
        </p>

        {/* 1-Line Install Box */}
        <div className="mt-8 max-w-2xl mx-auto bg-slate-900/90 border border-cyan-500/30 rounded-2xl p-2 sm:p-2.5 shadow-2xl shadow-cyan-950/50 flex flex-col sm:flex-row items-center gap-2">
          <div className="flex items-center space-x-2 px-3 text-cyan-400 font-mono text-xs select-none">
            <span className="text-slate-500 font-bold">$</span>
            <span className="text-slate-200 overflow-x-auto whitespace-nowrap text-[13px] font-medium py-1">
              {installCommand}
            </span>
          </div>
          <button
            onClick={() => copyToClipboard(installCommand, 'hero-install')}
            className="w-full sm:w-auto ml-auto flex items-center justify-center space-x-1.5 px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-md transition-all active:scale-95 whitespace-nowrap"
          >
            {copiedCmd === 'hero-install' ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-950" />
                <span>Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Command</span>
              </>
            )}
          </button>
        </div>

        {/* CTAs */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <a
            href="./app.html"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-sm shadow-xl shadow-cyan-500/25 transition-all hover:scale-105 active:scale-95"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Try Live 1:1 Web Demo</span>
            <ArrowRight className="w-4 h-4" />
          </a>

          <a
            href="#install-section"
            className="flex items-center space-x-2 px-6 py-3.5 rounded-2xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-bold text-sm transition-all"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            <span>Download for Local</span>
          </a>

          <a
            href="https://github.com/unrealandychan/open-factory-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-6 py-3.5 rounded-2xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-300 font-semibold text-sm transition-all"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            <span>GitHub Stars</span>
          </a>
        </div>
      </section>

      {/* 1:1 Live Workspace Interactive Demo Window */}
      <section id="demo-section" className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-6">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800 text-xs font-semibold text-cyan-400 mb-2">
            <Boxes className="w-3.5 h-3.5" />
            <span>Interactive 1:1 Desktop UI</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Three-Pane Workspace In Action</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl mx-auto">
            Experience the identical information architecture: Factory Sidebar, Flow Step Cards, and the Parameter &amp; Output Workspace.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-700/80 rounded-2xl overflow-hidden shadow-2xl">
          {/* Mock Browser Header */}
          <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              <span className="ml-3 text-[11px] font-mono text-slate-400">http://127.0.0.1:8765/ (Open Factory Agent)</span>
            </div>
            <a
              href="./app.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] font-bold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
            >
              <span>Open Fullscreen</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          {/* Embedded 1:1 App Frame */}
          <div className="w-full h-[620px] bg-[#17191d]">
            <iframe
              src="./app.html"
              title="Open Factory Agent 1:1 Web Demo"
              className="w-full h-full border-0"
              loading="lazy"
            />
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-cyan-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 mb-4">
            <Unlock className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-white mb-2">Zero Paywalls &amp; 100% Free</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            No $16/month Patreon subscriptions, no 2-factory artificial caps, and no remote license validation. Create unlimited automated workflows freely.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center text-indigo-400 mb-4">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-white mb-2">100% On-Device Privacy</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All scripts, prompts, and output files reside entirely on your local machine. No external Cloudflare license servers tracking your usage.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 mb-4">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-white mb-2">Local Agent Ecosystem</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Out-of-the-box integration with Hermes, Pi, Claude Code CLI, and local Ollama models. Trigger tasks and stream outputs with zero extra config.
          </p>
        </div>
      </section>

      {/* Local Agent Architecture & Setup */}
      <section id="agents-section" className="max-w-5xl mx-auto px-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800 text-xs font-semibold text-cyan-400 mb-2">
            <Terminal className="w-3.5 h-3.5" />
            <span>Zero-Friction Local Agents</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Plug In Any Coding Agent</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl mx-auto">
            Open Factory Agent communicates over standard local HTTP webhooks. Connect your favorite agent in seconds:
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          {/* Agent Tabs */}
          <div className="flex space-x-2 border-b border-slate-800 pb-4 mb-6 overflow-x-auto text-xs font-bold">
            <button
              onClick={() => setActiveAgentTab('hermes')}
              className={`px-4 py-2 rounded-xl transition-all ${
                activeAgentTab === 'hermes'
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Hermes Agent
            </button>
            <button
              onClick={() => setActiveAgentTab('pi')}
              className={`px-4 py-2 rounded-xl transition-all ${
                activeAgentTab === 'pi'
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Pi Agent Harness
            </button>
            <button
              onClick={() => setActiveAgentTab('claude')}
              className={`px-4 py-2 rounded-xl transition-all ${
                activeAgentTab === 'claude'
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Claude Code CLI
            </button>
            <button
              onClick={() => setActiveAgentTab('ollama')}
              className={`px-4 py-2 rounded-xl transition-all ${
                activeAgentTab === 'ollama'
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Ollama / Local LLM
            </button>
          </div>

          {/* Agent Content */}
          {activeAgentTab === 'hermes' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-300">
                Launch Hermes in daemon mode with its native webhook listener enabled:
              </p>
              <div className="bg-slate-950 p-4 rounded-xl font-mono text-xs text-slate-200 border border-slate-800 flex justify-between items-center">
                <code>hermes agent start --webhook-port 8644</code>
                <button
                  onClick={() => copyToClipboard('hermes agent start --webhook-port 8644', 'hermes')}
                  className="text-slate-400 hover:text-cyan-400 p-1"
                >
                  {copiedCmd === 'hermes' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-[11px] text-slate-400">
                In Open Factory Agent Web UI → Settings → Agent, verify target is <span className="text-cyan-400 font-mono">http://127.0.0.1:8644/webhooks/agent-task</span>.
              </p>
            </div>
          )}

          {activeAgentTab === 'pi' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-300">
                Use Pi's webhook bridge to dispatch prompt steps directly into Pi sessions:
              </p>
              <div className="bg-slate-950 p-4 rounded-xl font-mono text-xs text-slate-200 border border-slate-800 flex justify-between items-center">
                <code>pi --listen-webhook 8644</code>
                <button
                  onClick={() => copyToClipboard('pi --listen-webhook 8644', 'pi')}
                  className="text-slate-400 hover:text-cyan-400 p-1"
                >
                  {copiedCmd === 'pi' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}

          {activeAgentTab === 'claude' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-300">
                Connect Claude Code CLI through standard local HTTP dispatch:
              </p>
              <div className="bg-slate-950 p-4 rounded-xl font-mono text-xs text-slate-200 border border-slate-800 flex justify-between items-center">
                <code>claude --server --port 8644</code>
                <button
                  onClick={() => copyToClipboard('claude --server --port 8644', 'claude')}
                  className="text-slate-400 hover:text-cyan-400 p-1"
                >
                  {copiedCmd === 'claude' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}

          {activeAgentTab === 'ollama' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-300">
                Run fully offline models (Qwen 2.5, Llama 3.3, DeepSeek) through Ollama:
              </p>
              <div className="bg-slate-950 p-4 rounded-xl font-mono text-xs text-slate-200 border border-slate-800 flex justify-between items-center">
                <code>ollama run qwen2.5-coder:14b</code>
                <button
                  onClick={() => copyToClipboard('ollama run qwen2.5-coder:14b', 'ollama')}
                  className="text-slate-400 hover:text-cyan-400 p-1"
                >
                  {copiedCmd === 'ollama' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Comparison Table */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Why Open Factory Agent?</h2>
          <p className="text-xs text-slate-400 mt-1">Direct comparison with closed-source / paywalled alternatives</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950 text-slate-400">
                <th className="py-3 px-4 font-semibold">Capability</th>
                <th className="py-3 px-4 font-semibold text-cyan-400">Open Factory Agent</th>
                <th className="py-3 px-4 font-semibold text-slate-500">Proprietary Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr>
                <td className="py-3 px-4 font-medium text-slate-200">Pricing &amp; License</td>
                <td className="py-3 px-4 text-emerald-400 font-semibold flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>100% Free Forever (MIT)</span>
                </td>
                <td className="py-3 px-4 text-slate-400">US$12 - $16 / month Patreon</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-slate-200">Factory Creation Cap</td>
                <td className="py-3 px-4 text-emerald-400 font-semibold">Unlimited Free Factories</td>
                <td className="py-3 px-4 text-rose-400">Capped at 2 in Free Trial</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-slate-200">License Verification</td>
                <td className="py-3 px-4 text-emerald-400 font-semibold">None (No DRM / No Keys)</td>
                <td className="py-3 px-4 text-rose-400">Cloudflare D1 &amp; Worker DRM</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-slate-200">On-Device Privacy</td>
                <td className="py-3 px-4 text-emerald-400 font-semibold">100% Offline / Local Execution</td>
                <td className="py-3 px-4 text-slate-400">Remote Auth Callbacks</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-slate-200">Developer Tooling</td>
                <td className="py-3 px-4 text-emerald-400 font-semibold">Makefile, Docker, Shell CLI</td>
                <td className="py-3 px-4 text-slate-400">Restricted Launchers</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Download & Installation Section */}
      <section id="install-section" className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800 text-xs font-semibold text-cyan-400 mb-2">
            <Download className="w-3.5 h-3.5" />
            <span>Ready in Seconds</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Download &amp; Install on Your Machine</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl mx-auto">
            Choose your preferred way to run Open Factory Agent locally:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Option 1: 1-Line Installer */}
          <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <div className="w-10 h-10 rounded-xl bg-cyan-950 flex items-center justify-center text-cyan-400 mb-3">
                <Terminal className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-white text-sm mb-1">Option 1: One-Line Curl</h3>
              <p className="text-slate-400 text-xs leading-relaxed mb-4">
                Recommended for macOS &amp; Linux. Automatically installs CLI and dependencies into ~/.open-factory-agent.
              </p>
            </div>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-cyan-300 break-all mb-3">
              <code>{installCommand}</code>
            </div>
            <button
              onClick={() => copyToClipboard(installCommand, 'card-curl')}
              className="w-full py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all flex items-center justify-center space-x-1"
            >
              {copiedCmd === 'card-curl' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedCmd === 'card-curl' ? 'Copied!' : 'Copy Script'}</span>
            </button>
          </div>

          {/* Option 2: Docker Compose */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-950 flex items-center justify-center text-indigo-400 mb-3">
                <Server className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-white text-sm mb-1">Option 2: Docker Compose</h3>
              <p className="text-slate-400 text-xs leading-relaxed mb-4">
                Containerized deployment with zero host dependencies. Perfect for headless servers or local Docker desktops.
              </p>
            </div>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-indigo-300 mb-3">
              <code>docker compose up -d</code>
            </div>
            <button
              onClick={() => copyToClipboard('docker compose up -d', 'card-docker')}
              className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-all flex items-center justify-center space-x-1"
            >
              {copiedCmd === 'card-docker' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedCmd === 'card-docker' ? 'Copied!' : 'Copy Docker Cmd'}</span>
            </button>
          </div>

          {/* Option 3: Git & Make */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-950 flex items-center justify-center text-emerald-400 mb-3">
                <Zap className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-white text-sm mb-1">Option 3: Make Script</h3>
              <p className="text-slate-400 text-xs leading-relaxed mb-4">
                Full developer control with the included Makefile. Clone the repo and start with a single make target.
              </p>
            </div>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-emerald-300 mb-3">
              <code>git clone ... &amp;&amp; make run</code>
            </div>
            <button
              onClick={() => copyToClipboard('git clone https://github.com/unrealandychan/open-factory-agent.git && cd open-factory-agent && make run', 'card-make')}
              className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-all flex items-center justify-center space-x-1"
            >
              {copiedCmd === 'card-make' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedCmd === 'card-make' ? 'Copied!' : 'Copy Make Cmd'}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 pt-10 pb-8 text-center text-xs text-slate-500">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <img src="./open-factory-logo.png" alt="Logo" className="w-6 h-6 rounded-lg object-contain" />
          <span className="font-bold text-slate-300">Open Factory Agent</span>
          <span>•</span>
          <span>Released under MIT License</span>
          <span>•</span>
          <span>Author: Eddie Chan (@unrealandychan)</span>
        </div>
        <p>100% Free and Open Source software. No subscriptions, no telemetry, no paywalls.</p>
      </footer>
    </div>
  )
}
