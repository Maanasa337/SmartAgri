import React, { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Sun, CircleDollarSign, Sprout, Loader2 } from 'lucide-react';
import API from '../api/axios';

export default function RecommendationEngine() {
  const [reco, setReco] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expressing, setExpressing] = useState(false);

  useEffect(() => {
    fetchReco();
  }, []);

  const fetchReco = async () => {
    try {
      const res = await API.get('/api/recommendations/crop');
      setReco(res.data.recommendation);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInterest = async () => {
    if (!reco) return;
    setExpressing(true);
    try {
      await API.post('/api/recommendations/interested', { crop_name: reco.crop_name });
      alert(`Interest registered! Expected vendor email: ${reco.vendor_match?.name || 'Local Agronomist'}`);
      setReco(prev => ({ ...prev, interested: true }));
    } catch (err) {
      alert('Failed to register interest');
    } finally {
      setExpressing(false);
    }
  };

  if (loading) {
    return (
      <div className="app-card h-[400px] flex items-center justify-center bg-white border border-[var(--brand-200)]">
         <Loader2 className="w-8 h-8 text-[var(--gold)] animate-spin" />
      </div>
    );
  }

  if (!reco) return null;

  return (
    <div className="app-card overflow-hidden h-full flex flex-col border border-[var(--gold)]/30">
      <div className="app-gold-gradient p-4 text-center relative overflow-hidden">
        <Sparkles className="absolute top-2 right-2 text-white/30 w-16 h-16 animate-pulse" />
        <p className="text-[#8B6B22] text-[10px] font-bold uppercase tracking-widest mb-1">AI High-Profit Pick</p>
        <h3 className="text-2xl font-extrabold text-[#5D4613] drop-shadow-sm leading-none">{reco.crop_name}</h3>
      </div>
      
      <div className="p-4 flex-1 flex flex-col bg-white">
        <p className="text-sm text-gray-700 italic mb-4 border-l-2 border-[var(--gold)] pl-3">
            "{reco.why_suitable}"
        </p>

        <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-[#FFF8E1] p-2.5 rounded-xl border border-[#FFE082]">
                <div className="flex items-center gap-1.5 text-[#F57F17] mb-1">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">Est. Profit</span>
                </div>
                <p className="font-bold text-[#E65100]">₹{(reco.expected_profit_inr/1000).toFixed(0)}k <span className="font-normal text-xs text-gray-600">/ac</span></p>
            </div>
            
            <div className="bg-[#E8F5E9] p-2.5 rounded-xl border border-[#A5D6A7]">
                <div className="flex items-center gap-1.5 text-[#2E7D32] mb-1">
                    <Sun className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">Duration</span>
                </div>
                <p className="font-bold text-[#1B5E20]">{reco.grow_duration_days} <span className="font-normal text-xs text-gray-600">Days</span></p>
            </div>
        </div>

        <div className="flex-1 space-y-2">
            <h4 className="text-xs font-bold text-gray-900 border-b pb-1">Care Requirements</h4>
            <p className="text-xs text-gray-600">{reco.care_tips}</p>
        </div>

        {reco.vendor_match && (
           <div className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-xl">
               <p className="text-[10px] font-bold text-blue-500 uppercase tracking-wider">Matched Buyer</p>
               <p className="text-xs font-semibold text-blue-900">{reco.vendor_match.name}</p>
               <p className="text-[11px] text-blue-700">{reco.vendor_match.location}</p>
           </div>
        )}

        <button 
            onClick={handleInterest}
            disabled={expressing || reco.interested}
            className={`w-full mt-4 py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 shadow-sm
               ${reco.interested 
                 ? 'bg-gray-100 text-gray-400 cursor-not-allowed border ' 
                 : 'bg-gradient-to-r from-[var(--gold)] to-[#F5D060] text-white hover:shadow-md hover:-translate-y-0.5'}`}
        >
            {expressing ? <Loader2 className="w-4 h-4 animate-spin"/> 
             : reco.interested ? 'Interest Registered' 
             : <><Sprout className="w-4 h-4"/> Grow This Season</>}
        </button>
      </div>
    </div>
  );
}
