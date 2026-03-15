import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950 p-8">
          <div className="max-w-lg rounded-2xl border border-red-800 bg-slate-900 p-8 text-center">
            <div className="mb-4 text-4xl">⚠️</div>
            <h1 className="mb-2 text-xl font-bold text-red-400">Algo correu mal</h1>
            <p className="mb-6 text-sm text-slate-400">
              {this.state.error.message}
            </p>
            <pre className="mb-6 max-h-40 overflow-auto rounded-lg bg-slate-800 p-4 text-left text-xs text-slate-300">
              {this.state.error.stack}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-amber-500 px-6 py-2 text-sm font-bold text-slate-900 hover:bg-amber-400"
            >
              Recarregar
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
