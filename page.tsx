"use client";

import React from 'react';
import { Users, TrendingUp, TrendingDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, LabelList } from 'recharts';
import Link from 'next/link';

const mockStats = {
  totalReviews: 245800,
  highImpactOpportunities: 120,
  avgFitScore: 8.5,
  topBarriers: [
    { name: 'Sizing Issues', value: 35 },
    { name: 'Fabric Quality', value: 25 },
    { name: 'Product Mismatch', value: 20 },
    { name: 'Delivery Delays', value: 15 },
    { name: 'Price Point', value: 5 },
  ],
  sentimentBreakdown: [
    { name: 'Positive', value: 60, color: '#F88B46' }, 
    { name: 'Neutral', value: 25, color: '#F34C74' }, 
    { name: 'Negative', value: 15, color: '#D92D5F' }, 
  ]
};



export default function Dashboard() {
  const [stats, setStats] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    fetch(`${apiUrl}/api/dashboard-stats`)
      .then(res => res.json())
      .then(data => {
        if (data && data.totalReviews) {
          // Add custom colors to sentiment from backend
          const colorMap: any = { "Positive": "#F88B46", "Neutral": "#F34C74", "Negative": "#D92D5F" };
          if (data.sentimentBreakdown) {
            data.sentimentBreakdown = data.sentimentBreakdown.map((s: any) => ({
              ...s, color: colorMap[s.name] || s.color
            }));
          }
          setStats(data);
        } else {
          setStats(mockStats);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Dashboard stats error:", err);
        setStats(mockStats);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-slate-700 border-t-[#F88B46] rounded-full animate-spin"></div>
      </div>
    );
  }

  const renderData = stats || mockStats;

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full">
      <h2 className="text-2xl font-bold text-white mb-2">Discovery Engine Overview</h2>
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Active Metric Card (Total Reviews) */}
        <div className="glass-panel p-5 rounded-2xl border-[1.5px] border-[#F88B46]/60 shadow-[0_0_15px_rgba(248,139,70,0.15)] relative overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <p className="text-sm text-slate-300 font-medium">Total Reviews</p>
            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
              <Users className="w-4 h-4 text-[#F88B46]" />
            </div>
          </div>
          <div className="flex items-end justify-between">
            <h3 className="text-3xl font-bold text-white">{renderData.totalReviews.toLocaleString()}</h3>
            <div className="flex items-center gap-1 text-[#F88B46] text-sm font-medium pb-1">
              <TrendingUp className="w-4 h-4" />
              <span>+5%</span>
            </div>
          </div>
        </div>

        {/* Other Metric Cards */}
        {[
          { title: 'Analyzed Reviews', value: renderData.totalAnalyzed ? renderData.totalAnalyzed.toLocaleString() : renderData.totalReviews.toLocaleString(), change: '+5%', trend: 'up' },
          { title: 'High Impact Opportunities', value: renderData.highImpactOpportunities.toString(), change: renderData.highImpactOpportunities === 0 ? '0%' : '+12%', trend: renderData.highImpactOpportunities === 0 ? 'flat' : 'up' },
          { title: 'Average Fit Score', value: renderData.avgFitScore?.toString() || "N/A", change: '+0.3', trend: 'up' },
        ].map((stat, i) => (
          <div key={i} className="glass-panel p-5 rounded-2xl flex flex-col justify-between">
             <div className="flex justify-between items-start mb-2">
              <p className="text-sm text-slate-400 font-medium">{stat.title}</p>
            </div>
            <div className="flex items-end justify-between mt-4">
              <h3 className="text-3xl font-bold text-slate-200">{stat.value}</h3>
              <div className={`flex items-center gap-1 text-sm font-medium pb-1 ${stat.trend === 'up' ? 'text-[#F88B46]' : stat.trend === 'down' ? 'text-[#F34C74]' : 'text-slate-400'}`}>
                {stat.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : stat.trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
                <span>{stat.change}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[320px]">
        {/* Bar Chart Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col">
          <h3 className="text-base font-semibold text-white mb-6">Top Purchase Barriers</h3>
          <div className="flex-1 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={renderData.topBarriers} layout="vertical" margin={{ top: 0, right: 40, left: 0, bottom: 0 }} barSize={16}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#cbd5e1', fontSize: 13}} width={70} />
                <Tooltip 
                  cursor={{fill: 'rgba(255,255,255,0.02)'}}
                  contentStyle={{ backgroundColor: '#1a1d27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="value" radius={[0, 8, 8, 0] as any} background={{ fill: 'rgba(255,255,255,0.03)', radius: [0, 8, 8, 0] as any }}>
                  {renderData.topBarriers.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={`url(#orangePink)`} />
                  ))}
                  <LabelList dataKey="value" position="insideRight" formatter={(val: any) => `${val}`} fill="#f8fafc" fontSize={12} offset={10} />
                </Bar>
                <defs>
                  <linearGradient id="orangePink" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#F88B46" />
                    <stop offset="100%" stopColor="#F34C74" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col">
          <h3 className="text-base font-semibold text-white mb-2">Sentiment Breakdown</h3>
          <div className="flex-1 w-full flex items-center justify-between">
             <div className="w-[50%] h-full relative flex items-center justify-center">
               <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={renderData.sentimentBreakdown.filter((d: any) => d.value > 0)}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={78}
                    stroke="none"
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {renderData.sentimentBreakdown.filter((d: any) => d.value > 0).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1a1d27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
             </div>
             
              {/* Legend */}
             <div className="w-[45%] flex flex-col gap-3">
                {renderData.sentimentBreakdown.map((d: any, i: number) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full min-w-[12px]" style={{ backgroundColor: d.color, boxShadow: `0 0 10px ${d.color}60` }}></div>
                    <span className="text-sm text-slate-300 truncate" title={d.name}>{d.name} ({d.value}%)</span>
                  </div>
                ))}
             </div>
          </div>
        </div>

        {/* Wishlist Intent Pie Chart Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col">
          <h3 className="text-base font-semibold text-white mb-2">Wishlist Intents</h3>
          <div className="flex-1 w-full flex items-center justify-between">
             <div className="w-[50%] h-full relative flex items-center justify-center">
               <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={(renderData.wishlistBreakdown || []).filter((d: any) => d.value > 0)}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={78}
                    stroke="none"
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {(renderData.wishlistBreakdown || []).filter((d: any) => d.value > 0).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1a1d27', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
             </div>
             
             {/* Legend */}
             <div className="w-[45%] flex flex-col gap-3">
                {(renderData.wishlistBreakdown || []).map((d: any, i: number) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full min-w-[12px]" style={{ backgroundColor: d.color, boxShadow: `0 0 10px ${d.color}60` }}></div>
                    <span className="text-xs text-slate-300 truncate" title={d.name}>{d.name} ({d.value}%)</span>
                  </div>
                ))}
             </div>
          </div>
        </div>
      </div>

    </div>
  );
}
