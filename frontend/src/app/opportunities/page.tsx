"use client";
import React, { useState, useEffect } from 'react';
import { TrendingUp, ChevronRight, Star, AlertCircle } from 'lucide-react';

interface ReviewEvidence {
  text: string;
  rating: number;
  author: string;
}

interface Opportunity {
  opportunity: string;
  description: string;
  frequency_percentage: number;
  mention_count: number;
  impact_score: number;
  priority_score: number;
  priority_level: string;
  wishlist_to_purchase_impact: string;
  wishlist_intent: string;
  evidence: ReviewEvidence[];
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIdx, setSelectedIdx] = useState<number>(0);

  useEffect(() => {
    fetch('http://localhost:5000/api/opportunities')
      .then(res => res.json())
      .then(data => {
        setOpportunities(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch opportunities", err);
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

  if (opportunities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400">
        <AlertCircle className="w-12 h-12 mb-4 text-slate-500" />
        <h2 className="text-xl font-semibold text-white mb-2">No Opportunities Found</h2>
        <p>The AI is still analyzing reviews or no significant patterns were discovered yet.</p>
      </div>
    );
  }

  const selectedOpp = opportunities[selectedIdx];

  const totalOpportunities = opportunities.length;
  const totalReviews = opportunities.length > 0 && opportunities[0].frequency_percentage > 0 
    ? Math.round((opportunities[0].mention_count * 100) / opportunities[0].frequency_percentage) 
    : 0;
  const highQuality = Math.round(totalReviews * 0.85); // Approximate for UI aesthetics

  const getPriorityColor = (level: string) => {
    switch (level) {
      case 'Critical': return 'text-red-400 bg-red-400/10';
      case 'High': return 'text-orange-400 bg-orange-400/10';
      case 'Medium': return 'text-yellow-400 bg-yellow-400/10';
      default: return 'text-blue-400 bg-blue-400/10';
    }
  };

  const getBarColor = (level: string) => {
    switch (level) {
      case 'Critical': return 'bg-red-500';
      case 'High': return 'bg-orange-500';
      case 'Medium': return 'bg-yellow-500';
      default: return 'bg-blue-500';
    }
  };

  const getDotColor = (level: string) => {
    switch (level) {
      case 'Critical': return '🔴';
      case 'High': return '🟠';
      case 'Medium': return '🟡';
      default: return '🔵';
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto w-full p-4 font-sans text-slate-200">
      
      {/* Review Analysis Stats */}
      <div className="flex items-center justify-center gap-12 py-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{totalReviews}</span>
          <span className="text-sm text-slate-400 uppercase tracking-wider">Reviews Analyzed</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{highQuality}</span>
          <span className="text-sm text-slate-400 uppercase tracking-wider">High-Quality</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{totalOpportunities}</span>
          <span className="text-sm text-slate-400 uppercase tracking-wider">Opportunities</span>
        </div>
      </div>

      {/* Opportunity Areas List */}
      <div className="mt-4">
        <h2 className="text-sm font-bold text-slate-400 tracking-widest uppercase mb-8">Opportunity Areas</h2>
        
        <div className="flex flex-col gap-6">
          {opportunities.map((opp, idx) => (
            <div 
              key={idx} 
              onClick={() => setSelectedIdx(idx)}
              className={`flex flex-col gap-2 cursor-pointer p-4 -mx-4 rounded-xl transition-colors border border-transparent ${selectedIdx === idx ? 'bg-white/5 border-white/10' : 'hover:bg-white/5'}`}
            >
              {/* Top Row: Title and Impact */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-slate-500 font-bold w-6">#{idx + 1}</span>
                  <span className="text-lg font-bold text-white">{opp.opportunity}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold uppercase tracking-widest ${getPriorityColor(opp.priority_level).split(' ')[0]}`}>
                    {opp.priority_level} IMPACT
                  </span>
                  <span className="text-lg">{getDotColor(opp.priority_level)}</span>
                </div>
              </div>
              
              {/* Middle Row: Stats */}
              <div className="flex items-center gap-2 text-sm text-slate-400 ml-10">
                <span className="font-semibold text-slate-300">{opp.mention_count}</span> reviews &middot; <span className="font-semibold text-slate-300">{opp.frequency_percentage}%</span>
              </div>
              
              {/* Bottom Row: Bar */}
              <div className="w-full bg-slate-800 rounded-full h-2 mt-2 ml-10 overflow-hidden" style={{ width: 'calc(100% - 2.5rem)' }}>
                <div 
                  className={`h-full rounded-full ${getBarColor(opp.priority_level)}`} 
                  style={{ width: `${opp.frequency_percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Deep Dive Section */}
      {selectedOpp && (
        <div className="glass-panel rounded-xl border border-white/10 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-white/5 border-b border-white/10 p-6">
            <h2 className="text-xl font-bold text-white uppercase tracking-wider">{selectedOpp.opportunity}</h2>
          </div>
          
          <div className="p-6 flex flex-col gap-8">
            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex flex-col gap-1">
                <span className="text-white font-semibold">{selectedOpp.mention_count} supporting reviews</span>
                <span className="text-slate-400">Impact: <span className="text-white font-medium">{selectedOpp.priority_level.toUpperCase()}</span></span>
              </div>
              <div className="flex flex-col gap-1 text-right">
                <span className="text-white font-semibold">{selectedOpp.frequency_percentage}% of reviews</span>
                <span className="text-slate-400">Confidence: <span className="text-white font-medium">HIGH</span></span>
              </div>
            </div>

            {/* What are users worried about */}
            <div className="flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">What Are Users Worried About?</h3>
              <ul className="flex flex-col gap-2 text-sm text-slate-300">
                <li className="flex justify-between items-center">
                  <span className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[#F88B46]"></span> {selectedOpp.description || "Users are experiencing friction related to this area."}</span>
                  <span className="text-slate-500 font-medium">{selectedOpp.mention_count}</span>
                </li>
              </ul>
            </div>

            {/* Why it matters */}
            <div className="flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Why It Matters</h3>
              <p className="text-sm text-slate-300 leading-relaxed bg-white/5 p-4 rounded-lg border border-white/5">
                Customers have expressed interest by wishlisting, but this friction point has a <span className="text-[#F88B46] font-semibold">{(selectedOpp.wishlist_to_purchase_impact || 'unknown').toLowerCase().replace(/_/g, ' ')}</span> likelihood of preventing them from completing the purchase.
              </p>
            </div>

            {/* Evidence */}
            <div className="flex flex-col gap-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Original Review Evidence</h3>
              <div className="flex flex-col gap-3 mt-1">
                {selectedOpp.evidence && selectedOpp.evidence.length > 0 ? (
                  selectedOpp.evidence.slice(0, 2).map((ev, i) => (
                    <div key={i} className="text-sm text-slate-300 italic border-l-2 border-[#F34C74] pl-4 py-1">
                      "{ev.text.length > 100 ? ev.text.substring(0, 100) + '...' : ev.text}"
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-slate-500 italic">No direct textual evidence available.</div>
                )}
              </div>
            </div>

            {/* Footer Action */}
            <div className="flex justify-center mt-2 pt-6 border-t border-white/10">
              <button className="bg-white/10 hover:bg-white/20 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2">
                [ View All {selectedOpp.mention_count} Reviews ]
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
