interface ScoreBadgeProps {
  score: number;
  label?: string;
}

export function ScoreBadge({ score, label }: ScoreBadgeProps) {
  let colorClasses: string;
  if (score >= 0.7) {
    colorClasses = 'bg-red-100 text-red-800 border-red-200';
  } else if (score >= 0.4) {
    colorClasses = 'bg-yellow-100 text-yellow-800 border-yellow-200';
  } else {
    colorClasses = 'bg-green-100 text-green-800 border-green-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${colorClasses}`}>
      {label && <span className="mr-1">{label}</span>}
      {(score * 100).toFixed(0)}%
    </span>
  );
}
