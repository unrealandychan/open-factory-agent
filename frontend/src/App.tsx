import { useState } from 'react'
import { Navbar } from './components/Navbar'
import { ProductShowcase } from './components/ProductShowcase'
import { ExternalLink, Play } from 'lucide-react'

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('overview')

  const handleTabChange = (tab: string) => {
    setCurrentTab(tab)
    if (tab === 'agents') {
      const el = document.getElementById('agents-section')
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    } else if (tab === 'install') {
      const el = document.getElementById('install-section')
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    } else if (tab === 'demo') {
      const el = document.getElementById('demo-section')
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      <Navbar currentTab={currentTab} onTabChange={handleTabChange} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {currentTab === 'demo-fullscreen' ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-3 rounded-xl">
              <span className="text-xs text-slate-300 font-mono">http://127.0.0.1:8765/ (Open Factory Agent 1:1 Interface)</span>
              <div className="flex space-x-2">
                <a
                  href="./app.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg flex items-center space-x-1"
                >
                  <span>New Window</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
                <button
                  onClick={() => setCurrentTab('overview')}
                  className="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-lg"
                >
                  Back to Landing Page
                </button>
              </div>
            </div>
            <div className="w-full h-[85vh] rounded-2xl overflow-hidden border border-slate-800">
              <iframe src="./app.html" title="Open Factory Agent" className="w-full h-full border-0" />
            </div>
          </div>
        ) : (
          <ProductShowcase />
        )}
      </main>
    </div>
  )
}
export default App
