"use client";

import React, { useState } from 'react';
import { Search, ChevronDown, Star } from 'lucide-react';

const mockReviews = [
  {
    id: 1,
    rating: 4,
    text: "The fabric is great, but the fit on the shoulders is a bit tight. I'd buy it again if it were more comfortable.",
    intent: "Wishlist Intent",
    barrier: "Purchase Barrier",
    area: "Opportunity Area: Fit",
  },
  {
    id: 2,
    rating: 2,
    text: "Very disappointed with the color. It looked much brighter online.",
    intent: "Wishlist Intent",
    barrier: "Purchase Barrier",
    area: "Opportunity Area: Color Accuracy",
  },
  {
    id: 3,
    rating: 5,
    text: "Absolutely love this dress! Perfect for summer weddings. Will definitely check out more from this brand.",
    intent: "Wishlist Intent",
    barrier: "Purchase Barrier",
    area: "Opportunity Area: Styling",
  },
  {
    id: 4,
    rating: 3,
    text: "The material is okay, but the delivery was delayed by a week.",
    intent: "Wishlist Intent",
    barrier: "Purchase Barrier",
    area: "Opportunity Area: Logistics",
  }
];

export default function Explorer() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('All Sentiments');
  const [opportunityFilter, setOpportunityFilter] = useState('Opportunity Area');

  const filteredReviews = reviews.filter(review => {
    const matchesSearch = searchQuery === '' || review.text.toLowerCase().includes(searchQuery.toLowerCase());
    
    const reviewSentiment = review.sentiment ? review.sentiment.toLowerCase() : 'neutral';
    const matchesSentiment = sentimentFilter === 'All Sentiments' || reviewSentiment === sentimentFilter.toLowerCase();
    
    const oppFilterNormalized = opportunityFilter === 'Opportunity Area' ? '' : opportunityFilter.toLowerCase().replace(' issue', '');
    const reviewArea = review.area ? review.area.toLowerCase() : '';
    const matchesOpportunity = oppFilterNormalized === '' || reviewArea.includes(oppFilterNormalized);
    
    return matchesSearch && matchesSentiment && matchesOpportunity;
  });

  React.useEffect(() => {
    fetch('http://localhost:5000/api/reviews')
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          setReviews(data);
        } else {
          setReviews(mockReviews); // Fallback to mock if db is empty
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching reviews:", err);
        setReviews(mockReviews);
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex flex-col gap-6 max-w-6xl mx-auto w-full">
      
      <div>
        <h4 className="text-sm font-medium text-slate-400 mb-1">Internal analytics dashboard</h4>
        <h2 className="text-2xl font-bold text-white mb-6">Review Explorer Tool</h2>
      </div>

      {/* Header & Filters */}
      <div className="glass-panel p-4 flex items-end gap-4 rounded-xl flex-wrap lg:flex-nowrap">
        <div className="flex flex-col flex-1 gap-2 min-w-[250px]">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Filter</label>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search reviews..." 
              className="w-full glass-input pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        


        <div className="flex flex-col gap-2 min-w-[180px]">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sentiment</label>
          <div className="relative">
            <select 
              className="w-full glass-input appearance-none cursor-pointer pr-10"
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
            >
              <option>All Sentiments</option>
              <option>Positive</option>
              <option>Neutral</option>
              <option>Negative</option>
            </select>
            <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <div className="flex flex-col gap-2 min-w-[200px]">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Opportunity Area</label>
          <div className="relative">
            <select 
              className="w-full glass-input appearance-none cursor-pointer pr-10 border-[#F88B46] border-opacity-50 text-white"
              value={opportunityFilter}
              onChange={(e) => setOpportunityFilter(e.target.value)}
            >
              <option>Opportunity Area</option>
              <option>Fit Issue</option>
              <option>Price Point</option>
              <option>Quality</option>
            </select>
            <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Grid of Reviews */}
      <div className="mt-2">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-10 h-10 border-4 border-slate-700 border-t-[#F88B46] rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredReviews.length === 0 && (
              <div className="col-span-full text-center text-slate-400 py-10">No reviews match your filters</div>
            )}
            {filteredReviews.map((review) => {
              return (
                <div key={review.id} className="glass-card p-6 flex flex-col justify-between min-h-[180px]">
                  <div>
                    <div className="flex items-center gap-1 mb-4">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star 
                          key={star} 
                          className={`w-5 h-5 ${star <= review.rating ? "fill-amber-400 text-amber-400" : "text-slate-600 fill-slate-700"}`} 
                        />
                      ))}
                    </div>
                    <p className="text-slate-300 text-[15px] leading-relaxed mb-6">
                      {review.text}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Sentiment Pill */}
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${
                      review.sentiment?.toLowerCase() === 'positive' ? 'bg-emerald-500/80' : 
                      review.sentiment?.toLowerCase() === 'negative' ? 'bg-[#F34C74]' : 
                      'bg-[#F88B46]'
                    }`}>
                      {review.sentiment ? review.sentiment.charAt(0).toUpperCase() + review.sentiment.slice(1) : 'Neutral'}
                    </span>
                    {/* User Intent Pill */}
                    {review.intent && review.intent !== 'Unknown' && (
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#F88B46] text-white">
                        {review.intent}
                      </span>
                    )}
                    {/* Opportunity / Barrier Pill */}
                    {review.barrier && review.barrier !== 'None' && (
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[#D92D5F] text-white">
                        {review.barrier}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
