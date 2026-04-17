import { useState } from 'react';
import { StatsBar } from './components/StatsBar';
import { Dashboard } from './components/Dashboard';
import { LinkedInLogo } from './components/LinkedInLogo';
import {
  ScoreDistributionChart,
  FeedContextChart,
  TimelineChart,
  TopOffendersWidget,
  AmplifiersWidget,
} from './components/Charts';

type Tab = 'dashboard' | 'analytics';

function App() {
  const [tab, setTab] = useState<Tab>('dashboard');

  return (
    <div className="min-h-screen bg-[#f3f2ef]">
      {/* LinkedIn-style header */}
      <header className="bg-white border-b border-[#e0dfdc] sticky top-0 z-10">
        <div className="max-w-[1128px] mx-auto px-4 h-[52px] flex items-center gap-3">
          <LinkedInLogo className="w-[34px] h-[34px] text-[#0a66c2]" />
          <div className="flex items-baseline gap-1.5">
            <h1 className="text-xl font-semibold text-[#191919]">LinkedInalyzer</h1>
            <span className="text-xs text-[#666] font-normal">Feed Quality Analyzer</span>
          </div>

          {/* Navigation tabs */}
          <nav className="ml-8 flex gap-1">
            <button
              onClick={() => setTab('dashboard')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
                tab === 'dashboard'
                  ? 'bg-[#0a66c2] text-white'
                  : 'text-[#666] hover:bg-[#eef3f8] hover:text-[#191919]'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setTab('analytics')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
                tab === 'analytics'
                  ? 'bg-[#0a66c2] text-white'
                  : 'text-[#666] hover:bg-[#eef3f8] hover:text-[#191919]'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-[1128px] mx-auto px-4 py-4">
        <StatsBar />

        {tab === 'dashboard' && (
          <div className="grid grid-cols-[minmax(0,1fr)_300px] gap-4">
            <Dashboard />
            <aside className="space-y-4">
              <TopOffendersWidget />
              <AmplifiersWidget />
            </aside>
          </div>
        )}

        {tab === 'analytics' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <ScoreDistributionChart />
              <FeedContextChart />
            </div>
            <TimelineChart />
            <div className="grid grid-cols-2 gap-4">
              <TopOffendersWidget />
              <AmplifiersWidget />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
