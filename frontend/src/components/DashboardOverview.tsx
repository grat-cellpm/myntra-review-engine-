import React from 'react';

interface OverviewProps {
  totalAnalyzed: number;
  relevantReviews: number;
}

export const DashboardOverview: React.FC<OverviewProps> = ({ totalAnalyzed, relevantReviews }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center justify-center">
        <h3 className="text-gray-500 text-sm font-medium mb-1">Total Reviews Analyzed</h3>
        <p className="text-3xl font-bold text-gray-800">{totalAnalyzed.toLocaleString()}</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center justify-center">
        <h3 className="text-gray-500 text-sm font-medium mb-1">Relevant to Fashion Shopping</h3>
        <p className="text-3xl font-bold text-blue-600">{relevantReviews.toLocaleString()}</p>
        <p className="text-xs text-gray-400 mt-1">
          {totalAnalyzed > 0 ? Math.round((relevantReviews / totalAnalyzed) * 100) : 0}% of total
        </p>
      </div>
    </div>
  );
};
