import React, { useState, useEffect } from 'react';
import { Bug, AlertTriangle, Send, Loader2, PackageOpen } from 'lucide-react';
import API from '../api/axios';

export default function PestAlert() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reporting, setReporting] = useState(false);
  
  const [reportData, setReportData] = useState({
    pest_name: '',
    severity: 5,
  });

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await API.get('/api/pest/alerts');
      setAlerts(res.data.alerts || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReport = async (e) => {
    e.preventDefault();
    if (!reportData.pest_name) return;
    
    setReporting(true);
    try {
      const res = await API.post('/api/pest/report', reportData);
      alert(`Pest reported! Notified ${res.data.nearby_farmers_notified} nearby farmers.`);
      setReportData({ pest_name: '', severity: 5 });
      fetchAlerts();
    } catch (err) {
      alert('Failed to report');
    } finally {
      setReporting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      
      {/* Active Alerts */}
      <div className="app-card flex-1 flex flex-col overflow-hidden max-h-[300px]">
        <div className="p-3 border-b border-gray-100 bg-[#FFF3E0] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#F57C00]" />
            <h3 className="font-bold text-[#E65100] text-sm">Cluster Pest Alerts</h3>
          </div>
          <span className="app-chip bg-[#FFE0B2] border-[#FFCC80] text-[#E65100]">{alerts.length} Active</span>
        </div>
        
        <div className="p-3 flex-1 overflow-y-auto space-y-2 bg-[#FAFAF7] text-sm">
          {loading ? (
             <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 animate-spin text-[#F57C00]" /></div>
          ) : alerts.length === 0 ? (
             <p className="text-center text-gray-500 text-xs py-4">No active pests in your 15km cluster.</p>
          ) : (
            alerts.map(a => (
              <div key={a.id} className={`p-3 rounded-xl border ${a.severity >= 7 ? 'bg-red-50 border-red-200' : 'bg-orange-50 border-orange-200'}`}>
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-bold ${a.severity >= 7 ? 'text-red-800' : 'text-orange-800'}`}>{a.pest_name}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${a.severity >= 7 ? 'bg-red-200 text-red-900' : 'bg-orange-200 text-orange-900'}`}>Sev: {a.severity}/10</span>
                </div>
                <p className="text-xs text-gray-600">Reported by {a.reporter_name} on {a.crop}</p>
                <div className="mt-2 flex gap-2">
                    <button className="text-[10px] bg-white border border-gray-200 px-2 py-1 rounded shadow-sm flex items-center gap-1 hover:bg-gray-50">
                        <PackageOpen className="w-3 h-3" /> Order Cure
                    </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Report Form */}
      <div className="app-card p-4 bg-white">
        <h4 className="font-bold text-[var(--text-900)] text-sm mb-3 flex items-center gap-2">
            <Bug className="w-4 h-4 text-red-500" /> Report Pest Sighting
        </h4>
        <form onSubmit={handleReport} className="space-y-3">
          <input
            type="text"
            placeholder="e.g. Stem Borer"
            className="w-full text-sm p-2 bg-gray-50 border border-gray-200 rounded-lg outline-none focus:border-red-400 focus:bg-white"
            value={reportData.pest_name}
            onChange={e => setReportData({...reportData, pest_name: e.target.value})}
            required
          />
          <div className="flex items-center gap-3">
             <label className="text-xs font-semibold text-gray-500">Severity (1-10):</label>
             <input 
                type="range" min="1" max="10" 
                value={reportData.severity}
                onChange={e => setReportData({...reportData, severity: parseInt(e.target.value)})}
                className="flex-1 cursor-pointer accent-red-500"
             />
             <span className="text-xs font-bold w-4">{reportData.severity}</span>
          </div>
          <button 
             type="submit" 
             disabled={reporting}
             className="w-full bg-red-50 hover:bg-red-100 text-red-700 font-bold text-sm py-2 rounded-lg border border-red-200 transition-colors flex items-center justify-center gap-2"
          >
             {reporting ? <Loader2 className="w-4 h-4 animate-spin"/> : <><Send className="w-4 h-4"/> Broadcast to Cluster</>}
          </button>
        </form>
      </div>

    </div>
  );
}
