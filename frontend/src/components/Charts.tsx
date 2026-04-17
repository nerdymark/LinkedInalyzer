import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell,
  AreaChart, Area,
} from 'recharts';
import { getScoreDistribution, getFeedContext, getTimeline, getTopOffenders, getAmplifiers } from '../api/client';

const COLORS = ['#0a66c2', '#057642', '#b24020', '#915907', '#5f4bb6', '#c37d16', '#e16745', '#44712e', '#7c3592', '#2977c9'];

export function ScoreDistributionChart() {
  const { data } = useQuery({ queryKey: ['score-distribution'], queryFn: getScoreDistribution });
  if (!data) return null;

  const chartData = data.buckets.map((bucket, i) => ({
    range: bucket,
    Political: data.political[i],
    'AI Slop': data.ai_slop[i],
  }));

  return (
    <div className="bg-white rounded-lg border border-[#e0dfdc] p-4">
      <h3 className="text-base font-semibold text-[#191919] mb-3">Score Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData}>
          <XAxis dataKey="range" tick={{ fontSize: 11, fill: '#666' }} />
          <YAxis tick={{ fontSize: 11, fill: '#666' }} />
          <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e0dfdc' }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="Political" fill="#b24020" radius={[2, 2, 0, 0]} />
          <Bar dataKey="AI Slop" fill="#915907" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function FeedContextChart() {
  const { data } = useQuery({ queryKey: ['feed-context'], queryFn: getFeedContext });
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border border-[#e0dfdc] p-4">
      <h3 className="text-base font-semibold text-[#191919] mb-3">How Posts Reach You</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={85}
            paddingAngle={2}
            dataKey="value"
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e0dfdc' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TimelineChart() {
  const { data } = useQuery({ queryKey: ['timeline'], queryFn: getTimeline });
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border border-[#e0dfdc] p-4">
      <h3 className="text-base font-semibold text-[#191919] mb-3">Scrape Timeline</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#666' }} />
          <YAxis tick={{ fontSize: 11, fill: '#666' }} />
          <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e0dfdc' }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Area type="monotone" dataKey="clean" stackId="1" fill="#057642" stroke="#057642" fillOpacity={0.6} name="Clean" />
          <Area type="monotone" dataKey="political" stackId="1" fill="#b24020" stroke="#b24020" fillOpacity={0.8} name="Political" />
          <Area type="monotone" dataKey="ai_slop" stackId="1" fill="#915907" stroke="#915907" fillOpacity={0.8} name="AI Slop" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TopOffendersWidget() {
  const { data } = useQuery({ queryKey: ['top-offenders'], queryFn: getTopOffenders });
  if (!data) return null;

  const hasData = data.political.length > 0 || data.ai_slop.length > 0;
  if (!hasData) return null;

  return (
    <div className="bg-white rounded-lg border border-[#e0dfdc] p-4">
      <h3 className="text-base font-semibold text-[#191919] mb-3">Top Offenders</h3>
      <div className="grid grid-cols-2 gap-4">
        {data.political.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-[#b24020] uppercase tracking-wide mb-2">Political</h4>
            <div className="space-y-1.5">
              {data.political.map((a) => (
                <div key={a.id} className="flex items-center justify-between text-sm">
                  <a href={a.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-[#0a66c2] hover:underline truncate mr-2">
                    {a.name}
                  </a>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-xs text-[#666]">{a.political_post_count}x</span>
                    <span className="inline-block px-1.5 py-0.5 rounded text-xs font-medium bg-red-100 text-[#b24020]">
                      {(a.avg_political_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {data.ai_slop.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-[#915907] uppercase tracking-wide mb-2">AI Slop</h4>
            <div className="space-y-1.5">
              {data.ai_slop.map((a) => (
                <div key={a.id} className="flex items-center justify-between text-sm">
                  <a href={a.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-[#0a66c2] hover:underline truncate mr-2">
                    {a.name}
                  </a>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-xs text-[#666]">{a.ai_slop_post_count}x</span>
                    <span className="inline-block px-1.5 py-0.5 rounded text-xs font-medium bg-amber-100 text-[#915907]">
                      {(a.avg_ai_slop_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function AmplifiersWidget() {
  const { data } = useQuery({ queryKey: ['amplifiers'], queryFn: getAmplifiers });
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-white rounded-lg border border-[#e0dfdc] p-4">
      <h3 className="text-base font-semibold text-[#191919] mb-3">Connections Amplifying Flagged Content</h3>
      <p className="text-xs text-[#666] mb-2">These connections liked, commented, or reposted political/slop posts that appeared in your feed.</p>
      <div className="space-y-1.5">
        {data.map((a: { name: string; count: number; url?: string }) => (
          <div key={a.name} className="flex items-center justify-between text-sm">
            <a
              href={a.url || `https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(a.name)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#0a66c2] hover:underline truncate mr-2"
            >
              {a.name}
            </a>
            <span className="text-xs px-1.5 py-0.5 rounded bg-[#eef3f8] text-[#0a66c2] font-medium shrink-0">
              {a.count} post{a.count !== 1 ? 's' : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
