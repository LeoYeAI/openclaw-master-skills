import React from 'react';
import { LayoutDashboard, BarChart3, List, Settings } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <h1 className="text-xl font-bold text-indigo-600">Eval Skills</h1>
          <p className="text-xs text-gray-500 mt-1">v0.1.0 (Phase 3)</p>
        </div>
        <nav className="px-4 space-y-1">
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg">
            <LayoutDashboard className="w-5 h-5" />
            Dashboard
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">
            <List className="w-5 h-5" />
            Skills
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">
            <BarChart3 className="w-5 h-5" />
            Reports
          </a>
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">
            <Settings className="w-5 h-5" />
            Settings
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <h2 className="text-lg font-semibold text-gray-800">Dashboard</h2>
        </header>
        
        <div className="p-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard title="Total Skills" value="12" change="+2 this week" />
            <StatCard title="Benchmarks" value="5" change="Running" />
            <StatCard title="Avg Score" value="87%" change="+5%" trend="up" />
            <StatCard title="Tasks Run" value="1,240" change="Last 24h" />
          </div>

          {/* Placeholder Chart Area */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-96 flex items-center justify-center text-gray-400">
            Chart Visualization Placeholder (Recharts integration coming soon)
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, change, trend }: { title: string, value: string, change: string, trend?: 'up' | 'down' }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-gray-500'}`}>
          {change}
        </span>
      </div>
    </div>
  );
}

export default App;
