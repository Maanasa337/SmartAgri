import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mic, MicOff, Leaf, MapPin, Loader2 } from 'lucide-react';
import API from '../api/axios';
import useVoiceInput from '../hooks/useVoiceInput';

const InputField = ({ 
  label, 
  name, 
  type = 'text', 
  placeholder, 
  overrideValue,
  formData,
  handleChange,
  isVoiceMode,
  activeVoiceField,
  handleVoiceToggle,
  isProcessing
}) => (
  <div className="relative mb-5 group">
    <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-500)] mb-1 pointer-events-none px-1">
      {label}
    </label>
    <div className="relative flex items-center">
      {type === 'select' ? (
        <select 
          name={name} 
          value={formData[name]} 
          onChange={handleChange}
          className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition-all focus:border-[var(--brand-500)] focus:bg-white focus:ring-4 focus:ring-[var(--brand-100)] appearance-none"
        >
          <option value="sowing">Sowing</option>
          <option value="vegetative">Vegetative</option>
          <option value="flowering">Flowering</option>
          <option value="harvest">Harvest Phase</option>
        </select>
      ) : (
        <input
          type={type}
          name={name}
          value={overrideValue !== undefined ? overrideValue : formData[name]}
          onChange={handleChange}
          placeholder={placeholder}
          className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition-all focus:border-[var(--brand-500)] focus:bg-white focus:ring-4 focus:ring-[var(--brand-100)]"
          required={['username', 'email', 'password'].includes(name)}
          readOnly={name === 'gps_coordinates'}
        />
      )}

      {isVoiceMode && name !== 'gps_coordinates' && name !== 'password' && (
        <button
          type="button"
          onClick={() => handleVoiceToggle(name)}
          className={`absolute right-3 p-2 rounded-full transition-all ${
            activeVoiceField === name 
              ? 'bg-[var(--brand-100)] text-[var(--brand-600)] animate-pulse' 
              : 'text-gray-400 hover:bg-gray-100 hover:text-[var(--brand-500)]'
          }`}
        >
         {activeVoiceField === name ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
        </button>
      )}
    </div>
    {activeVoiceField === name && isProcessing && (
      <p className="absolute -bottom-5 left-2 text-[10px] text-[var(--brand-600)] font-semibold flex items-center gap-1">
        <Loader2 className="w-3 h-3 animate-spin" /> Processing speech...
      </p>
    )}
  </div>
);

export default function SignUp() {
  const navigate = useNavigate();
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { isRecording, isProcessing, transcript, startRecording, stopRecording, reset } = useVoiceInput();
  
  // Track which field is currently expecting voice input
  const [activeVoiceField, setActiveVoiceField] = useState(null);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    present_crop: '',
    present_crop_stage: 'sowing',
    land_acres: '',
    past_crop: '',
    past_disease: '',
    gps_coordinates: { lat: 0, lng: 0 },
  });

  // Attempt to auto-detect GPS on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setFormData(prev => ({ 
          ...prev, 
          gps_coordinates: { lat: pos.coords.latitude, lng: pos.coords.longitude } 
        })),
        (err) => console.warn('GPS denied:', err)
      );
    }
  }, []);

  // Update field when transcript returns
  useEffect(() => {
    if (transcript && activeVoiceField) {
      setFormData(prev => ({ ...prev, [activeVoiceField]: transcript }));
      setActiveVoiceField(null);
      reset();
    }
  }, [transcript, activeVoiceField, reset]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleVoiceToggle = async (fieldName) => {
    if (isRecording) {
      await stopRecording();
    } else {
      setActiveVoiceField(fieldName);
      await startRecording();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const payload = {
        ...formData,
        land_acres: parseFloat(formData.land_acres) || 2.0,
      };
      const res = await API.post('/api/auth/signup', payload);
      localStorage.setItem('smartagri_token', res.data.access_token);
      localStorage.setItem('smartagri_user', JSON.stringify(res.data.user));
      navigate('/home');
    } catch (err) {
      console.error("Signup error:", err.response?.data);
      const errorMsg = err.response?.data?.detail 
        ? typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : JSON.stringify(err.response.data.detail, null, 2)
        : 'Signup failed';
      alert(errorMsg);
      setIsLoading(false);
    }
  };


  return (
    <div className="app-frame flex flex-col justify-center min-h-[100dvh]">
      <div className="px-6 py-10 w-full animate-fade-in relative z-10">
        
        {/* Header */}
        <div className="text-center mb-10">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl app-gradient shadow-lg mb-4">
            <Leaf className="text-white h-8 w-8" />
          </div>
          <h1 className="text-2xl font-extrabold text-[var(--brand-900)] tracking-tight">Join SmartAgri</h1>
          <p className="text-[var(--text-500)] text-sm font-medium mt-1">Farm smarter, yield better.</p>
        </div>

        {/* Voice Mode Toggle */}
        <div className="mb-8 flex items-center justify-between p-4 bg-[var(--brand-50)] rounded-xl border border-[var(--brand-100)]">
          <div>
            <p className="text-sm font-bold text-[var(--brand-900)]">Voice Assistant Mode</p>
            <p className="text-xs text-[var(--brand-600)] font-medium">Auto-fill using your voice</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" className="sr-only peer" checked={isVoiceMode} onChange={() => setIsVoiceMode(!isVoiceMode)} />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--brand-500)]"></div>
          </label>
        </div>

        <form onSubmit={handleSubmit} className="space-y-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4">
            <InputField label="Full Name" name="username" placeholder="e.g. Murugan Selvam" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            <InputField label="Email Address" name="email" type="email" placeholder="murugan@example.com" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            
            <InputField label="Password" name="password" type="password" placeholder="••••••••" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            <InputField label="Present Crop" name="present_crop" placeholder="e.g. Paddy, Sugarcane" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            
            <InputField label="Crop Stage" name="present_crop_stage" type="select" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            <InputField label="Land Area (Acres)" name="land_acres" type="number" placeholder="e.g. 5.5" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            
            <InputField label="Past Season Crop" name="past_crop" placeholder="e.g. Groundnut" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
            <InputField label="Past Crop Disease" name="past_disease" placeholder="e.g. Blast, Nil" formData={formData} handleChange={handleChange} isVoiceMode={isVoiceMode} activeVoiceField={activeVoiceField} handleVoiceToggle={handleVoiceToggle} isProcessing={isProcessing} />
          </div>

          <div className="relative mb-8 pt-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-500)] mb-1">GPS Location (Auto-detected)</label>
            <div className="flex items-center gap-3 bg-[var(--surface-hover)] border border-[var(--line)] rounded-xl p-3">
              <div className="bg-[var(--brand-100)] p-2 rounded-lg text-[var(--brand-600)]">
                <MapPin className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-[var(--text-900)]">
                  {formData.gps_coordinates.lat.toFixed(4)}, {formData.gps_coordinates.lng.toFixed(4)}
                </p>
                <p className="text-xs text-[var(--text-500)]">Used for soil & weather analysis</p>
              </div>
            </div>
          </div>

          <button type="submit" disabled={isLoading} className="app-button flex items-center justify-center gap-2">
            {isLoading ? <><Loader2 className="w-5 h-5 animate-spin" /> Creating Profile...</> : 'Complete Profile & Join'}
          </button>
        </form>

        <p className="text-center mt-6 text-sm text-[var(--text-500)] font-medium">
          Already have an account? <Link to="/login" className="text-[var(--brand-600)] font-bold hover:underline">Log in</Link>
        </p>

      </div>
    </div>
  );
}
