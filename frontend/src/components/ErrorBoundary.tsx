import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-slate-100">
          <div className="text-center space-y-6">
            <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-slate-800">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                <path d="M10.29 3.86L3 12l7.29 8.14"></path>
                <path d="M17.71 3.86L21 12l-3.29 8.14"></path>
                <line x1="3" y1="12" x2="21" y2="12"></line>
              </svg>
            </div>
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">Terjadi Kesalahan Sistem</h1>
              <p className="text-slate-400 max-w-md mx-auto">
                Mohon maaf, terjadi gangguan pada sistem. Tim teknis kami telah diberitahu.
                Silakan kembali ke beranda atau coba muat ulang halaman.
              </p>
            </div>
            <button
              onClick={this.handleGoHome}
              className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-slate-950"
            >
              Kembali ke Beranda
            </button>
            {this.state.error && (
              <p className="text-xs text-slate-500 mt-4">
                Error: {this.state.error.message}
              </p>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}