'use client';

import { Button } from '@/components/ui/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-[#fff8fb] px-6 text-slate-900"
    >
      {/* Soft baby-pink background glow */}
      <div className="pointer-events-none absolute -left-32 -top-32 h-80 w-80 rounded-full bg-pink-200/30 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-32 h-80 w-80 rounded-full bg-pink-200/30 blur-3xl" />

      <section className="relative z-10 flex w-full max-w-4xl flex-col items-center text-center">

        {/* Microphone icon */}
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl border border-pink-100 bg-white shadow-lg shadow-pink-100">
          <span className="text-4xl">🎙️</span>
        </div>

        {/* Small label */}
        <p className="mb-3 text-xs font-bold uppercase tracking-[0.3em] text-pink-500">
          Voice AI Assistant
        </p>

        {/* Main heading */}
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">
          Your Personal
          <span className="block text-pink-500">
            Finance & Tech Assistant
          </span>
        </h1>

        {/* Description */}
        <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
          Talk naturally with your AI assistant about finance, technology,
          AI, and the latest tech products.
        </p>

        {/* Start button */}
        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-8 h-14 w-64 rounded-full bg-pink-500 px-8 text-sm font-bold tracking-wide text-white shadow-lg shadow-pink-200 transition-all hover:scale-105 hover:bg-pink-600"
        >
          🎙️ {startButtonText}
        </Button>

        <p className="mt-3 text-xs text-slate-400">
          Click to start a real-time voice conversation
        </p>

        {/* Feature cards */}
        <div className="mt-12 grid w-full max-w-3xl grid-cols-2 gap-4 sm:grid-cols-4">

          <div className="rounded-2xl border border-pink-100 bg-white px-4 py-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="mb-2 text-2xl">💰</div>
            <p className="text-sm font-semibold text-slate-700">
              Finance
            </p>
          </div>

          <div className="rounded-2xl border border-pink-100 bg-white px-4 py-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="mb-2 text-2xl">📱</div>
            <p className="text-sm font-semibold text-slate-700">
              Tech Products
            </p>
          </div>

          <div className="rounded-2xl border border-pink-100 bg-white px-4 py-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="mb-2 text-2xl">🤖</div>
            <p className="text-sm font-semibold text-slate-700">
              AI & Tech
            </p>
          </div>

          <div className="rounded-2xl border border-pink-100 bg-white px-4 py-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            <div className="mb-2 text-2xl">📊</div>
            <p className="text-sm font-semibold text-slate-700">
              Compare
            </p>
          </div>

        </div>

        {/* Footer */}
        <p className="mt-10 text-xs text-pink-400">
          Powered by real-time voice AI
        </p>

      </section>
    </div>
  );
};