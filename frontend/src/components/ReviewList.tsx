import React from 'react';

interface Review {
  review_id: string;
  source: string;
  original_review: string;
  rating?: number;
  date?: string;
  relevance: string;
  user_intent: string;
  opportunity_area: string;
  purchase_barriers: string[];
}

interface ReviewListProps {
  reviews: Review[];
}

export const ReviewList: React.FC<ReviewListProps> = ({ reviews }) => {
  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <div key={review.review_id} className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                {review.source.replace('_', ' ')}
              </span>
              {review.rating && (
                <span className="ml-2 text-sm text-yellow-500 font-medium">★ {review.rating}</span>
              )}
            </div>
            <span className="text-xs text-gray-400">{review.date || 'Unknown Date'}</span>
          </div>
          
          <p className="text-gray-800 text-sm mb-4 whitespace-pre-wrap font-serif">"{review.original_review}"</p>
          
          <div className="bg-gray-50 p-3 rounded-md border border-gray-100 text-sm grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-500 block text-xs">Opportunity Area</span>
              <span className="font-medium text-indigo-700">{review.opportunity_area}</span>
            </div>
            <div>
              <span className="text-gray-500 block text-xs">User Intent</span>
              <span className="font-medium text-gray-700">{review.user_intent}</span>
            </div>
            <div className="col-span-2 mt-2">
              <span className="text-gray-500 block text-xs mb-1">Purchase Barriers</span>
              <div className="flex flex-wrap gap-1">
                {review.purchase_barriers?.map(barrier => (
                  <span key={barrier} className="bg-red-50 text-red-600 px-2 py-0.5 rounded text-xs">
                    {barrier.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}
      {reviews.length === 0 && (
        <div className="text-center p-8 text-gray-500 bg-white rounded-lg border border-gray-200">
          No reviews found matching your criteria.
        </div>
      )}
    </div>
  );
};
