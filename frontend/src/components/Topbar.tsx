import React from 'react';
import { Search, User } from 'lucide-react';

export default function Topbar() {
  return (
    <header className="h-20 flex items-center justify-between px-8">
      <h2 className="text-xl font-bold text-white tracking-wide">Myntra Dashboard</h2>
      
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search" 
            className="glass-input pl-10 w-64 rounded-full bg-slate-800/40 border-slate-700/50"
          />
        </div>
        <div className="w-10 h-10 rounded-full bg-slate-800/80 border border-slate-700/50 flex items-center justify-center cursor-pointer hover:bg-slate-700 transition-colors">
          <User className="w-5 h-5 text-slate-300" />
        </div>
      </div>
    </header>
  );
}
