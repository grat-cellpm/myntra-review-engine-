'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, MessageSquare, Briefcase, Cpu, Sparkles, LogOut, Settings } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Reviews', href: '/explorer', icon: MessageSquare },
    { name: 'Opportunities', href: '/opportunities', icon: Briefcase },
    { name: 'AI Assistant', href: '/ai-assistant', icon: Sparkles },
  ];

  return (
    <aside className="w-64 bg-[#1a1d27] border-r border-white/5 flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6 flex items-center gap-3">
        {/* Custom Logo Approximation */}
        <div className="flex -space-x-1">
          <div className="w-4 h-8 bg-gradient-to-t from-[#F34C74] to-[#F88B46] rounded-full transform -rotate-12" />
          <div className="w-4 h-8 bg-gradient-to-t from-[#F34C74] to-[#F88B46] rounded-full transform rotate-12" />
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-lg text-white leading-none">Myntra</span>
          <span className="text-xs text-slate-400 font-medium">Analytics</span>
        </div>
      </div>
      
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link 
              key={item.name}
              href={item.href} 
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors relative ${
                isActive 
                  ? 'bg-white/5 text-white font-medium' 
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 brand-gradient rounded-r-md" />
              )}
              <item.icon className={`w-5 h-5 ${isActive ? 'text-[#F88B46]' : ''}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
