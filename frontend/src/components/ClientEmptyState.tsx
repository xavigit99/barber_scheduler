import { Link } from 'react-router-dom';

interface ClientEmptyStateProps {
  message: string;
  linkTo?: string;
  linkLabel?: string;
}

export default function ClientEmptyState({
  message,
  linkTo,
  linkLabel,
}: ClientEmptyStateProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <p className="text-sm text-slate-500">{message}</p>
      {linkTo && linkLabel && (
        <Link
          to={linkTo}
          className="mt-4 inline-flex rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700"
        >
          {linkLabel}
        </Link>
      )}
    </div>
  );
}
