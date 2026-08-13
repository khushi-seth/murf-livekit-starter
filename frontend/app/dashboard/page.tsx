"use client";

import { useEffect, useState } from "react";

type Stats = {
  total: number;
  successful: number;
  failed: number;
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total: 0,
    successful: 0,
    failed: 0,
  });

  const [loading, setLoading] = useState(true);

  async function loadStats() {
    try {
      const response = await fetch("/api/stats", {
        cache: "no-store",
      });

      const data = await response.json();

      if (response.ok) {
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to load dashboard stats", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStats();

    const interval = setInterval(
      loadStats,
      3000
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-background px-6 py-12">

      <div className="mx-auto max-w-6xl">

        <div className="mb-10">

          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
            Day 8
          </p>

          <h1 className="text-4xl font-bold tracking-tight">
            Voice Agent Dashboard
          </h1>

          <p className="mt-3 text-muted-foreground">
            Real-time performance from actual voice calls.
          </p>

        </div>


        <div className="grid gap-6 md:grid-cols-3">

          <div className="rounded-2xl border bg-card p-8 shadow-sm">

            <p className="text-sm font-medium text-muted-foreground">
              Total Calls
            </p>

            <p className="mt-4 text-5xl font-bold">
              {loading ? "—" : stats.total}
            </p>

            <p className="mt-3 text-sm text-muted-foreground">
              All recorded calls
            </p>

          </div>


          <div className="rounded-2xl border bg-card p-8 shadow-sm">

            <p className="text-sm font-medium text-muted-foreground">
              Successful Calls
            </p>

            <p className="mt-4 text-5xl font-bold">
              {loading ? "—" : stats.successful}
            </p>

            <p className="mt-3 text-sm text-muted-foreground">
              Calls reaching the success condition
            </p>

          </div>


          <div className="rounded-2xl border bg-card p-8 shadow-sm">

            <p className="text-sm font-medium text-muted-foreground">
              Failed Calls
            </p>

            <p className="mt-4 text-5xl font-bold">
              {loading ? "—" : stats.failed}
            </p>

            <p className="mt-3 text-sm text-muted-foreground">
              Calls not reaching the success condition
            </p>

          </div>

        </div>


        <div className="mt-8 rounded-2xl border bg-card p-6">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="font-semibold">
                Live Statistics
              </h2>

              <p className="mt-1 text-sm text-muted-foreground">
                Dashboard refreshes automatically every 3 seconds.
              </p>

            </div>

            <div className="flex items-center gap-2 text-sm">

              <span className="h-2.5 w-2.5 rounded-full bg-green-500" />

              Live

            </div>

          </div>

        </div>


        <p className="mt-8 text-center text-xs text-muted-foreground">
          No passwords, OTPs, PINs, account numbers, or conversation
          transcripts are displayed.
        </p>

      </div>

    </main>
  );
}