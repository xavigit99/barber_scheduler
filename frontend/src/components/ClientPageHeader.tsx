interface ClientPageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
}

export default function ClientPageHeader({
  eyebrow = 'Área do Cliente',
  title,
  description,
}: ClientPageHeaderProps) {
  return (
    <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">{eyebrow}</p>
      <h1 className="mt-2 text-2xl font-semibold text-slate-900">{title}</h1>
      {description && <p className="mt-2 text-sm text-slate-500">{description}</p>}
    </div>
  );
}
