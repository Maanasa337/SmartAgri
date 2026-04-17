import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, CalendarClock, Droplet, Sprout, Wheat, Loader2, Volume2 } from 'lucide-react';
import API from '../api/axios';
import useVoiceInput from '../hooks/useVoiceInput';

export default function AdvisoryEngine() {
  const [plan, setPlan] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(true);

  // Voice chat state
  const { isRecording, isProcessing: hookIsProcessing, startRecording, stopRecording } = useVoiceInput();
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState([{ role: 'agent', text: 'Vanakkam! I am Krishi, your AI farm assistant. How can I help you today?' }]);
  const [audioUrl, setAudioUrl] = useState(null);
  const audioRef = useRef(null);
  const chatEndRef = useRef(null);

  // New Voice Features State
  const [languages, setLanguages] = useState([]);
  const [selectedLang, setSelectedLang] = useState('ta');
  
  const [isDiagnosticsOpen, setIsDiagnosticsOpen] = useState(false);
  const [translateInput, setTranslateInput] = useState('');
  const [translateOutput, setTranslateOutput] = useState('');
  const [bleuRefStr, setBleuRefStr] = useState('');
  const [bleuCandStr, setBleuCandStr] = useState('');
  const [bleuResult, setBleuResult] = useState('');

  useEffect(() => {
    fetchPlan();
    fetchLanguages();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchLanguages = async () => {
    try {
      const res = await API.get('/api/voice/languages');
      if (res.data?.languages) {
        setLanguages(res.data.languages.slice(0, 5)); // First 5
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLanguageChange = async (e) => {
    const newLang = e.target.value;
    setSelectedLang(newLang);
    
    // Auto trigger prefetch
    API.post('/api/voice/prefetch', { lang_code: newLang }).catch(console.error);

    // Auto trigger ask
    try {
      const user = JSON.parse(localStorage.getItem('smartagri_user') || '{}');
      const askRes = await API.post('/api/voice/ask', {
        question: `Introduce yourself in one sentence. Address me briefly.`,
        profile: user,
        is_comprehensive: false,
      });
      const answer = askRes.data.answer || 'Ready!';
      setMessages(prev => [...prev, { role: 'agent', text: answer }]);

      // Speak in new lang
      const speakRes = await API.post('/api/voice/speak', { text: answer, lang_code: newLang });
      if (speakRes.data.audio) {
        setAudioUrl(`data:audio/wav;base64,${speakRes.data.audio}`);
        setTimeout(() => audioRef.current?.play(), 100);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTranslate = async () => {
    try {
      const res = await API.post('/api/voice/translate-field', { text: translateInput, tgt_lang: selectedLang });
      setTranslateOutput(res.data.translated || 'Error');
    } catch (err) {
      setTranslateOutput('Translation failed');
    }
  };

  const handleBleuCheck = async () => {
    try {
      const res = await API.post('/api/voice/bleu', { reference: bleuRefStr, candidate: bleuCandStr });
      setBleuResult(res.data.chrf_score !== undefined ? `BLEU: ${res.data.bleu_score} | chRF: ${res.data.chrf_score}` : JSON.stringify(res.data));
    } catch (err) {
      setBleuResult('Failed test');
    }
  };

  const fetchPlan = async () => {
    try {
      setLoadingPlan(true);
      const res = await API.get('/api/advisory/current-plan');
      if (res.data.status === 'success' && res.data.plan) {
        setPlan(res.data.plan);
      } else {
        generatePlan();
      }
    } catch (err) {
      console.error(err);
      generatePlan();
    }
  };

  const generatePlan = async () => {
    try {
      setLoadingPlan(true);
      const res = await API.post('/api/advisory/generate-plan');
      setPlan(res.data.plan);
    } catch (err) {
      console.error('Plan generation failed', err);
    } finally {
      setLoadingPlan(false);
    }
  };

  const toggleMic = async () => {
    if (isRecording) {
      const audioBase64 = await stopRecording();
      if (audioBase64) {
        sendConverseRequest(audioBase64);
      }
    } else {
      await startRecording();
    }
  };

  const sendConverseRequest = async (audioBase64) => {
    setIsProcessing(true);
    setMessages(prev => [...prev, { role: 'user', text: '🔊 Processing Voice...' }]);
    try {
      const user = JSON.parse(localStorage.getItem('smartagri_user') || '{}');
      const res = await API.post('/api/voice/converse', {
        audio: audioBase64,
        lang_code: selectedLang,
        profile: user,
        is_comprehensive: true,
      });

      const { transcribed, answer_local, audio } = res.data;

      setMessages(prev => {
        const newArr = [...prev];
        // Replace the "Processing..." state with actual transcribed text
        newArr[newArr.length - 1] = { role: 'user', text: transcribed };
        return [...newArr, { role: 'agent', text: answer_local }];
      });

      if (audio) {
        setAudioUrl(`data:audio/wav;base64,${audio}`);
        setTimeout(() => audioRef.current?.play(), 100);
      }
    } catch (err) {
      console.error('Converse API failed:', err);
      setMessages(prev => [...prev, { role: 'agent', text: 'Sorry, I couldn\'t process that voice request.' }]);
    } finally {
      setIsProcessing(false);
    }
  };


  return (
    <div className="flex flex-col gap-4">
      {/* Plan Card */}
      <div className="app-card overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div className="flex items-center gap-2">
            <CalendarClock className="w-5 h-5 text-[var(--brand-600)]" />
            <h3 className="font-bold text-[var(--text-900)]">Krishi Weekly Plan</h3>
          </div>
          {loadingPlan && <Loader2 className="w-4 h-4 animate-spin text-[var(--brand-500)]" />}
        </div>

        <div className="p-4 max-h-[300px] overflow-y-auto space-y-4 text-sm">
          {!plan && !loadingPlan && <p className="text-center text-gray-500 py-4">No plan available.</p>}

          {plan && (
            <>
              {/* Irrigation */}
              <div>
                <h4 className="font-semibold text-blue-700 flex items-center gap-1 mb-2"><Droplet className="w-4 h-4" /> Irrigation</h4>
                <div className="space-y-2">
                  {plan.irrigation_schedule?.map((item, i) => (
                    <div key={i} className="flex justify-between bg-blue-50 p-2 rounded-lg border border-blue-100 text-xs">
                      <span className="font-bold text-blue-900">{item.day} {item.time}</span>
                      <span className="text-blue-800">{item.duration_mins}m • {item.method}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sustainable */}
              <div>
                <h4 className="font-semibold text-green-700 flex items-center gap-1 mb-2"><Sprout className="w-4 h-4" /> Actions</h4>
                <ul className="list-disc pl-5 space-y-1 text-green-900 text-xs">
                  {plan.sustainable_tips?.map((tip, i) => <li key={i}>{tip}</li>)}
                </ul>
              </div>

              {/* Harvest */}
              {plan.harvest_plan && (
                <div>
                  <h4 className="font-semibold text-amber-700 flex items-center gap-1 mb-2"><Wheat className="w-4 h-4" /> Harvest</h4>
                  <div className="bg-amber-50 p-2 text-xs rounded-lg border border-amber-100 text-amber-900">
                    <p><strong>Est. Date:</strong> {plan.harvest_plan.expected_date}</p>
                    <p><strong>Yield:</strong> {plan.harvest_plan.yield_estimate}</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Voice Chat Card */}
      <div className="app-card flex flex-col h-[350px]">
        <div className="p-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
          <h3 className="font-bold text-[var(--text-900)] text-sm flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-[var(--brand-600)]" />
            Ask Krishi
          </h3>
          <select 
            value={selectedLang} 
            onChange={handleLanguageChange} 
            className="text-xs bg-white border border-gray-200 rounded-lg px-2 py-1 outline-none text-[var(--text-900)] shadow-sm"
          >
            {languages.map(l => (
              <option key={l.id} value={l.code}>{l.native} ({l.name})</option>
            ))}
            {languages.length === 0 && <option value="ta">தமிழ் (Tamil)</option>}
          </select>
        </div>

        <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-white text-sm">
          {messages.map((m, i) => (
            <div key={i} className={`max-w-[85%] rounded-2xl p-3 ${m.role === 'agent' ? 'bg-gray-100 text-gray-800 rounded-tl-none self-start mr-auto' : 'bg-[var(--brand-500)] text-white rounded-tr-none self-end ml-auto'}`}>
              {m.text}
            </div>
          ))}
          {(isProcessing || hookIsProcessing) && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-500 rounded-2xl rounded-tl-none p-3 text-xs flex items-center gap-2">
                <Loader2 className="w-3 h-3 animate-spin" /> {isProcessing ? 'Translating & Thinking...' : 'Listening...'}
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="p-3 bg-white border-t border-gray-100 flex flex-col gap-3">
          <div className="flex justify-center">
            <button
              onClick={toggleMic}
              className={`p-4 rounded-full shadow-lg transition-all ${isRecording ? 'bg-red-500 hover:bg-red-600 animate-pulse-ring' : 'bg-[var(--brand-600)] hover:bg-[var(--brand-700)]'}`}
            >
              {isRecording ? <Mic className="w-6 h-6 text-white" /> : <MicOff className="w-6 h-6 text-white" />}
            </button>
          </div>

          <div className="border-t border-gray-100 pt-3">
            <button 
              onClick={() => setIsDiagnosticsOpen(!isDiagnosticsOpen)}
              className="text-xs text-[var(--brand-600)] font-semibold w-full text-center hover:underline"
            >
              {isDiagnosticsOpen ? 'Hide Diagnostics' : 'Show Translate/BLEU Tools'}
            </button>
            
            {isDiagnosticsOpen && (
              <div className="mt-3 space-y-4 animate-fade-in bg-gray-50 p-3 rounded-xl border border-gray-200 text-xs text-[var(--text-900)]">
                {/* Translate Field */}
                <div>
                  <label className="font-bold mb-1 block">Test Translate Field (To current lang)</label>
                  <div className="flex gap-2">
                    <input type="text" value={translateInput} onChange={e => setTranslateInput(e.target.value)} placeholder="Type in English..." className="flex-1 rounded border px-2 py-1 outline-none" />
                    <button onClick={handleTranslate} className="bg-[var(--brand-500)] text-white px-3 py-1 rounded font-bold shadow-sm">Translate</button>
                  </div>
                  {translateOutput && <div className="mt-1 bg-white p-2 border rounded">Output: {translateOutput}</div>}
                </div>

                {/* Bleu Score */}
                <div className="border-t border-gray-200 pt-3">
                  <label className="font-bold mb-1 block">Test BLEU Score</label>
                  <div className="flex flex-col gap-2">
                    <input type="text" value={bleuRefStr} onChange={e => setBleuRefStr(e.target.value)} placeholder="Reference text" className="rounded border px-2 py-1 outline-none" />
                    <input type="text" value={bleuCandStr} onChange={e => setBleuCandStr(e.target.value)} placeholder="Candidate text" className="rounded border px-2 py-1 outline-none" />
                    <button onClick={handleBleuCheck} className="bg-[var(--text-900)] text-white px-3 py-1 rounded font-bold shadow-sm w-full">Calculate Score</button>
                  </div>
                  {bleuResult && <div className="mt-1 bg-white p-2 border rounded font-mono text-[10px]">Result: {bleuResult}</div>}
                </div>
              </div>
            )}
          </div>
        </div>

        {audioUrl && <audio ref={audioRef} src={audioUrl} className="hidden" />}
      </div>
    </div>
  );
}
