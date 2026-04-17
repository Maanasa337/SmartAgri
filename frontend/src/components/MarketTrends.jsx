import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Store, PackageSearch, Loader2 } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import API from '../api/axios';

export default function MarketTrends() {
  const [data, setData] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    try {
      const [trendRes, vendorRes] = await Promise.all([
        API.get('/api/market/trends'),
        API.get('/api/market/vendors')
      ]);
      setData(trendRes.data);
      setVendors(vendorRes.data.vendors);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (dir) => {
    if (dir === 'rising') return <TrendingUp className="w-5 h-5 text-emerald-500" />;
    if (dir === 'falling') return <TrendingDown className="w-5 h-5 text-red-500" />;
    return <Minus className="w-5 h-5 text-gray-500" />;
  };

  if (loading) return (
    <div className="app-card h-[400px] flex items-center justify-center">
      <Loader2 className="w-8 h-8 text-[var(--brand-500)] animate-spin" />
    </div>
  );

  if (!data) return null;

  // Format chart data
  const chartData = data.trends.map(t => ({
    date: new Date(t.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
    price: Math.round(t.price_per_quintal)
  }));

  return (
    <div className="flex flex-col gap-4 h-full">
      
      {/* Price Chart Card */}
      <div className="app-card p-4">
        <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-3">
            <div>
               <h3 className="text-sm font-bold text-gray-900 capitalize">{data.crop} Market Price</h3>
               <p className="text-xs text-gray-500 font-medium">30-Day Trend (₹/Quintal)</p>
            </div>
            <div className="bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-100 flex items-center gap-2">
               <span className="text-lg font-bold text-gray-900">₹{data.average_price}</span>
               {getTrendIcon(data.trend_direction)}
            </div>
        </div>
        
        <div className="h-[140px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#37a372" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#37a372" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <Tooltip 
                 contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                 labelStyle={{ color: '#6b7280', fontSize: '12px', fontWeight: 'bold' }}
              />
              <Area type="monotone" dataKey="price" stroke="#37a372" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Vendors Card */}
      <div className="app-card flex-1 flex flex-col overflow-hidden max-h-[220px]">
        <div className="p-3 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
            <Store className="w-4 h-4 text-[var(--brand-600)]" />
            <h3 className="font-bold text-sm text-gray-900">Verified Local Buyers</h3>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-white">
            {vendors.filter(v => v.match).map(v => (
                <div key={v.id} className="p-3 bg-white border border-gray-200 rounded-xl hover:border-[var(--brand-300)] transition-colors flex justify-between items-center group">
                    <div>
                        <h4 className="font-bold text-gray-900 text-sm group-hover:text-[var(--brand-700)] transition-colors">{v.name}</h4>
                        <p className="text-[11px] text-gray-500 font-medium">{v.location}</p>
                    </div>
                    <button className="bg-[var(--brand-50)] text-[var(--brand-700)] p-2 rounded-lg hover:bg-[var(--brand-100)]">
                        <PackageSearch className="w-4 h-4" />
                    </button>
                </div>
            ))}
            {vendors.filter(v => v.match).length === 0 && (
                <p className="text-center text-xs text-gray-500 py-4">No direct buyers found for {data.crop}.</p>
            )}
        </div>
      </div>

    </div>
  );
}
