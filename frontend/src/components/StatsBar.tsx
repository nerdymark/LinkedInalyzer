import { useStats } from '../hooks/useAuthors';

export function StatsBar() {
  const { data: stats, isLoading } = useStats();

  if (isLoading || !stats) {
    return <div className="animate-pulse h-20 bg-[#f3f2ef] rounded-lg" />;
  }

  const items = [
    { label: 'Authors Tracked', value: stats.total_authors, color: 'text-[#191919]' },
    { label: 'Posts Scraped', value: stats.total_posts, color: 'text-[#191919]' },
    { label: 'Political Posts', value: stats.political_posts, color: 'text-[#b24020]' },
    { label: 'AI Slop', value: stats.ai_slop_posts, color: 'text-[#915907]' },
    { label: 'Pending Review', value: stats.pending_review, color: 'text-[#0a66c2]' },
  ];

  return (
    <div className="grid grid-cols-5 gap-3 mb-4">
      {items.map((item) => (
        <div key={item.label} className="bg-white rounded-lg border border-[#e0dfdc] p-3 text-center">
          <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
          <div className="text-xs text-[#666] mt-0.5">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
