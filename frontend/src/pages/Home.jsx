import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import API from '../api/axios';

import FarmerAvatar from '../components/FarmerAvatar';
import AdvisoryEngine from '../components/AdvisoryEngine';
import PestAlert from '../components/PestAlert';
import RecommendationEngine from '../components/RecommendationEngine';
import MarketTrends from '../components/MarketTrends';

export default function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [errorStatus, setErrorStatus] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await API.get('/api/auth/me');
        setUser(res.data);
      } catch (err) {
        // Handled by axios interceptor for 401, but we catch network errors here
        if (!err.response || err.response.status !== 401) {
          setErrorStatus('Cannot connect to the SmartAgri backend service. Please verify the API is running.');
        }
      }
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('smartagri_token');
    localStorage.removeItem('smartagri_user');
    navigate('/login');
  };

  if (errorStatus) {
    return (
      <div className="min-h-screen bg-[var(--off-white)] flex flex-col items-center justify-center p-6 text-center">
         <h2 className="text-xl font-bold text-red-600 mb-2">Connection Error</h2>
         <p className="text-gray-600 mb-4">{errorStatus}</p>
         <button onClick={() => window.location.reload()} className="px-6 py-2 bg-[var(--brand-500)] text-white rounded-xl shadow-md font-medium hover:bg-[var(--brand-600)] transition-colors">
            Retry Connection
         </button>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[var(--off-white)] flex items-center justify-center">
         <div className="animate-pulse text-[var(--brand-600)] font-semibold flex items-center gap-2">
            Loading your digital farm...
         </div>
      </div>
    );
  }

  return (
    <div className="bg-[var(--off-white)] min-h-screen app-frame pb-safe sm:pb-8 flex flex-col relative">
       
       {/* Top Nav */}
       <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100 px-4 py-3 flex justify-between items-center shadow-sm">
           <div>
               <h1 className="text-xl font-extrabold text-[var(--brand-900)] tracking-tight">SmartAgri</h1>
               <p className="text-[10px] uppercase tracking-widest font-bold text-[var(--brand-500)]">Agentic Precision</p>
           </div>
           <button onClick={handleLogout} className="p-2 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors">
               <LogOut className="w-5 h-5" />
           </button>
       </header>

       <main className="flex-1 p-4 flex flex-col gap-5 overflow-y-auto w-full">
           
           {/* Row 1: Profile Header */}
           <div className="animate-fade-in" style={{ animationDelay: '0ms' }}>
               <FarmerAvatar user={user} />
           </div>

           {/* Row 2: Krishi Voice Advisory (Full Width) */}
           <div className="animate-fade-in" style={{ animationDelay: '100ms' }}>
               <AdvisoryEngine />
           </div>

           {/* Grid: 2 Columns for Web, 1 Column for Mobile */}
           <div className="grid grid-cols-1 gap-5 animate-fade-in" style={{ animationDelay: '200ms' }}>
               
               {/* Market Trends */}
               <div className="h-full">
                  <MarketTrends />
               </div>

               {/* Pest Alert System */}
               <div className="h-full">
                  <PestAlert />
               </div>

               {/* Recommendation Engine (Full Width at bottom) */}
               <div className="h-full pb-6">
                  <RecommendationEngine />
               </div>

           </div>
           
       </main>
    </div>
  );
}
