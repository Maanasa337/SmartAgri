import React, { useState } from 'react';
import { User, MapPin, Droplets, Thermometer, Wind, Mic, MicOff, Loader2 } from 'lucide-react';
import API from '../api/axios';
import useVoiceInput from '../hooks/useVoiceInput';

export default function FarmerAvatar({ user }) {
  const [avatarState, setAvatarState] = useState('idle'); // idle, listening, thinking, speaking
  const { isRecording, startRecording, stopRecording } = useVoiceInput();
  
  if (!user) return null;
  
  const weather = user.weather_data || {};
  const soil = user.soil_data || {};

  const handleMicClick = async () => {
    if (isRecording) {
      setAvatarState('thinking');
      const audioBase64 = await stopRecording();
      if (!audioBase64) {
        setAvatarState('idle');
        return;
      }

      try {
        const res = await API.post('/api/voice/converse', {
          audio: audioBase64,
          lang_code: 'ta', // Default for now
          profile: user,
          is_comprehensive: true,
        });

        const { answer_local, audio } = res.data;
        
        if (audio) {
          setAvatarState('speaking');
          const audioUrl = `data:audio/wav;base64,${audio}`;
          const audioEl = new Audio(audioUrl);
          audioEl.onended = () => setAvatarState('idle');
          audioEl.play();
        } else {
          setAvatarState('idle');
        }
      } catch (err) {
        console.error('Voice pipeline error:', err);
        setAvatarState('idle');
      }
    } else {
      setAvatarState('listening');
      await startRecording();
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden relative">
      <div className={`app-gradient p-5 flex items-center gap-4 transition-all ${avatarState === 'listening' ? 'bg-red-500' : ''}`}>
        <div className={`h-16 w-16 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border-2 border-white/40 relative ${avatarState === 'speaking' ? 'animate-pulse' : ''}`}>
          {avatarState === 'thinking' ? (
            <Loader2 className="h-8 w-8 text-white animate-spin" />
          ) : (
            <User className="h-8 w-8 text-white" />
          )}
          
          <button 
            onClick={handleMicClick}
            className={`absolute -bottom-1 -right-1 p-2 rounded-full shadow-lg border-2 border-white transition-all ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-white text-[var(--brand-600)]'}`}
          >
            {isRecording ? <Mic className="h-3 w-3 text-white" /> : <Mic className="h-3 w-3" />}
          </button>
        </div>
        <div>
          <h2 className="text-xl font-bold text-white leading-tight">{user.username}</h2>
          <div className="flex items-center gap-1.5 text-[var(--brand-100)] text-sm mt-1">
            <MapPin className="h-3.5 w-3.5" />
            <span>{user.land_acres} Acres • {user.present_crop}</span>
          </div>
        </div>
      </div>

      <div className="p-4 grid grid-cols-3 divide-x divide-gray-100 bg-gray-50/50">
        <div className="text-center px-1">
          <div className="flex items-center justify-center gap-1 text-[var(--text-500)] mb-1">
            <Thermometer className="h-3.5 w-3.5" />
            <span className="text-[10px] font-bold uppercase tracking-wider">Temp</span>
          </div>
          <p className="text-sm font-semibold text-[var(--text-900)]">{weather.temp || '--'}°C</p>
        </div>
        
        <div className="text-center px-1">
          <div className="flex items-center justify-center gap-1 text-[var(--text-500)] mb-1">
            <Droplets className="h-3.5 w-3.5 text-blue-400" />
            <span className="text-[10px] font-bold uppercase tracking-wider">Soil pH</span>
          </div>
          <p className="text-sm font-semibold text-[var(--text-900)]">{soil.ph || '--'}</p>
        </div>

        <div className="text-center px-1">
          <div className="flex items-center justify-center gap-1 text-[var(--text-500)] mb-1">
            <Wind className="h-3.5 w-3.5" />
            <span className="text-[10px] font-bold uppercase tracking-wider">NPK</span>
          </div>
          <p className="text-xs font-semibold text-[var(--text-900)] line-clamp-1">{soil.nitrogen_kg_ha}/{soil.phosphorus_kg_ha}/{soil.potassium_kg_ha}</p>
        </div>
      </div>

      {avatarState !== 'idle' && (
        <div className="absolute top-2 right-2 px-2 py-0.5 rounded bg-black/20 backdrop-blur-sm text-[10px] text-white font-bold uppercase tracking-widest animate-pulse">
          {avatarState}
        </div>
      )}
    </div>
  );
}
