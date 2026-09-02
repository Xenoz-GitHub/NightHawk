import { useState, useEffect } from 'react';
import { Shield, Server, Globe, Key, AlertTriangle, BarChart3, Activity } from 'lucide-react';

interface Finding { title: string; severity: string; category: string; confidence: number }
interface Asset { id: string; hostname: string; platform: string; services: string[] }

export default function App() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [status, setStatus] = useState('Loading...');

  useEffect(() => {
    // Mock data for demonstration
    setFindings([
      { title: 'Potential exposed API key', severity: 'high', category: 'secret_exposure', confidence: 0.92 },
      { title: 'Weak TLS version supported', severity: 'medium', category: 'tls_config', confidence: 0.75 },
      { title: 'Information disclosure via headers', severity: 'low', category: 'configuration', confidence: 0.63 },
    ]);
    setAssets([
      { id: '1', hostname: 'lab.example', platform: 'linux', services: ['https', 'ssh'] },
      { id: '2', hostname: 'api.lab.example', platform: 'linux', services: ['https', 'http'] },
    ]);
    setStatus('Operational');
  }, []);

  const criticalCount = findings.filter(f => f.severity === 'high' || f.severity === 'critical').length;
  const highCount = findings.filter(f => f.severity === 'high').length;
  const mediumCount = findings.filter(f => f.severity === 'medium').length;

  return (
    <div className="min-h-screen bg-ink text-ink-fg font-sans">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-border/30">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan/20 to-emerald/20 border border-cyan/30 flex items-center justify-center shadow-[0_0_15px_rgba(46,196,214,0.25)]">
              <Shield className="w-5 h-5 text-cyan" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold tracking-tight leading-none">NIGHTHAWK</h1>
              <p className="text-[10px] text-muted uppercase tracking-[0.2em] font-mono">Attack Surface Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs font-mono">
            <div className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse" /> <span className="text-muted">{status}</span></div>
            <span className="text-muted">v1.0.0</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-6">
        {/* Overview */}
        <section className="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'Assets Discovered', value: assets.length.toString(), icon: Server, color: 'cyan', sub: `${assets.filter(a => a.platform === 'linux').length} Linux` },
            { label: 'Critical Findings', value: criticalCount.toString(), icon: AlertTriangle, color: 'crimson', sub: 'Requires immediate review' },
            { label: 'High Findings', value: highCount.toString(), icon: Shield, color: 'amber', sub: 'Elevated risk' },
            { label: 'Medium Findings', value: mediumCount.toString(), icon: Activity, color: 'lavender', sub: 'Monitor closely' },
          ].map(card => (
            <div key={card.label} className="glass rounded-2xl p-6 hover:border-cyan/20 transition-colors relative overflow-hidden group">
              <div className={`absolute top-0 right-0 w-32 h-32 -translate-y-1/3 translate-x-1/4 rounded-full bg-${card.color}/10 blur-3xl`} />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono uppercase tracking-wider text-muted">{card.label}</span>
                  <card.icon className={`w-5 h-5 text-${card.color}`} />
                </div>
                <h3 className="text-3xl font-extrabold tracking-tight mb-1">{card.value}</h3>
                <p className="text-xs text-muted">{card.sub}</p>
              </div>
            </div>
          ))}
        </section>

        {/* Main content split */}
        <section className="col-span-12 md:col-span-7 space-y-6">
          {/* Recent Findings */}
          <div className="glass rounded-2xl p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-bold tracking-tight flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber" /> Recent Findings</h2>
              <span className="text-[10px] font-mono text-muted bg-panel px-2 py-0.5 rounded-full border border-border">Last 24h</span>
            </div>
            <div className="space-y-3">
              {findings.map((f, i) => (
                <div key={i} className="flex items-start gap-4 p-3 rounded-xl bg-panel hover:bg-surface transition-colors border border-border/40">
                  <div className={`w-2 h-2 mt-1.5 rounded-full shrink-0 ${f.severity === 'high' ? 'bg-crimson' : f.severity === 'medium' ? 'bg-amber' : 'bg-emerald'}`} />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold truncate">{f.title}</h3>
                    <div className="flex items-center gap-3 mt-1 text-[11px] font-mono text-muted">
                      <span className="uppercase">{f.category}</span>
                      <span>·</span>
                      <span>Confidence: {Math.round(f.confidence * 100)}%</span>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${f.severity === 'high' ? 'bg-crimson/10 text-crimson border-crimson/20' : f.severity === 'medium' ? 'bg-amber/10 text-amber border-amber/20' : 'bg-emerald/10 text-emerald border-emerald/20'}`}>
                    {f.severity.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Attack Surface Graph */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-base font-bold tracking-tight mb-4 flex items-center gap-2"><Globe className="w-4 h-4 text-cyan" /> Attack Surface Graph</h2>
            <div className="bg-ink rounded-xl h-64 flex items-center justify-center border border-border/30 relative overflow-hidden">
              <canvas id="graphCanvas" className="absolute inset-0 w-full h-full" />
              <div className="relative z-10 text-center">
                <p className="text-sm font-semibold">Graph Visualization</p>
                <p className="text-xs text-muted">NetworkX-powered relationship mapping</p>
              </div>
            </div>
          </div>
        </section>

        {/* Sidebar */}
        <aside className="col-span-12 md:col-span-5 space-y-6">
          {/* Assets */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-base font-bold tracking-tight mb-4 flex items-center gap-2"><Server className="w-4 h-4 text-emerald" /> Assets</h2>
            <div className="space-y-2">
              {assets.map(a => (
                <div key={a.id} className="flex items-center justify-between p-3 rounded-xl bg-panel border border-border/40 hover:border-cyan/20 transition-colors">
                  <div>
                    <h4 className="text-sm font-semibold font-mono">{a.hostname}</h4>
                    <p className="text-[11px] text-muted font-mono">{a.platform}</p>
                  </div>
                  <div className="flex gap-1">
                    {a.services.map(s => (
                      <span key={s} className="text-[10px] px-1.5 py-0.5 rounded bg-cyan/10 text-cyan font-mono border border-cyan/10">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Secret Exposure */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-base font-bold tracking-tight mb-4 flex items-center gap-2"><Key className="w-4 h-4 text-lavender" /> Secret Exposure</h2>
            <div className="p-4 rounded-xl bg-panel border border-border/40">
              <div className="flex items-center gap-3 mb-2">
                <span className="w-2 h-2 rounded-full bg-amber animate-pulse" />
                <span className="text-xs font-mono text-muted">Potential credential exposure detected</span>
              </div>
              <p className="text-xs text-muted leading-relaxed">Scan of ./repo identified 1 high-confidence potential secret. Redacted details available in campaign report. Recommended action: rotate/revoke and move to secure secret management.</p>
            </div>
          </div>

          {/* Campaign Status */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-base font-bold tracking-tight mb-4">Campaign</h2>
            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between"><span className="text-muted">Status</span><span className="text-emerald">Running</span></div>
              <div className="flex justify-between"><span className="text-muted">Modules</span><span>dns, http, tls, tech, secrets</span></div>
              <div className="flex justify-between"><span className="text-muted">Scope</span><span>lab.example, 10.10.10.0/24</span></div>
              <div className="flex justify-between"><span className="text-muted">Rate</span><span>5 req/s</span></div>
            </div>
          </div>
        </aside>
      </main>

      <footer className="max-w-7xl mx-auto px-6 py-6 text-[10px] text-muted font-mono border-t border-border/20 mt-auto">
        <div className="flex items-center justify-between">
          <span>NIGHTHAWK v1.0.0 — Ethical Security Assessment Platform</span>
          <span>Strictly for authorized scope only. Never deploy against unauthorized targets.</span>
        </div>
      </footer>
    </div>
  );
}
