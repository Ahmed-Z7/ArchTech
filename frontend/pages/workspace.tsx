import React, { useState, useEffect, useCallback, useRef } from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import HUD from '../components/HUD';
import WebcamOverlay from '../components/WebcamOverlay';
import ModelUploader from '../components/ModelUploader';
import GestureGuide from '../components/GestureGuide';
import GestureEngine from '../components/GestureEngine';
import { LogOut, Wifi, WifiOff, Cpu } from 'lucide-react';

const Viewer = dynamic<any>(() => import('../components/Viewer'), { ssr: false });

export default function Workspace() {
  const router = useRouter();
  const [hands, setHands] = useState<any>({ hands: [] });
  const [connected, setConnected] = useState(false);
  const [useInternal, setUseInternal] = useState(false);
  const [modelData, setModelData] = useState<{ url: string; ext: string } | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWS = () => {
      const socket = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = socket;

      socket.onopen = () => {
        setConnected(true);
        setUseInternal(false); // Disable browser engine if local server found
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setHands(data || { hands: [] });
        } catch (e) {
          console.error("Failed to parse websocket data");
        }
      };

      socket.onclose = () => {
        setConnected(false);
        // If websocket fails, wait a bit and enable internal engine
        setTimeout(() => {
          if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
            setUseInternal(true);
          }
        }, 2000);
      };
    };

    connectWS();
    return () => wsRef.current?.close();
  }, []);

  const handleInternalGesture = useCallback((data: any) => {
    if (!connected) {
      setHands(data);
    }
  }, [connected]);

  return (
    <div className="w-screen h-screen bg-black overflow-hidden relative scanlines font-['Rajdhani'] flex">
      <Head>
        <title>ARCH-TECH | HOLOGRAPHIC WORKSPACE</title>
      </Head>

      <div className="absolute inset-0 z-0">
        <Viewer hands={hands} modelData={modelData} />
      </div>

      <HUD hands={hands.hands || []} connected={connected || useInternal} />
      
      {/* Show overlay only if using local server. 
          If using internal, the GestureEngine already has a preview. */}
      {connected && <WebcamOverlay hands={hands.hands || []} />}
      
      <GestureEngine onGestureData={handleInternalGesture} enabled={useInternal} />

      {/* Connection Status Badge */}
      <div className="absolute top-8 right-8 z-[100] flex flex-col gap-2 items-end">
        <div className={`px-3 py-1 rounded-full flex items-center gap-2 border text-[10px] font-bold tracking-[0.2em] uppercase backdrop-blur-md transition-all ${
          connected 
          ? 'bg-green-500/10 border-green-500/50 text-green-400' 
          : useInternal 
            ? 'bg-blue-500/10 border-blue-500/50 text-blue-400'
            : 'bg-red-500/10 border-red-500/50 text-red-400'
        }`}>
          {connected ? <Wifi size={12} /> : useInternal ? <Cpu size={12} /> : <WifiOff size={12} />}
          {connected ? 'Local Engine (Python)' : useInternal ? 'Cloud Engine (Browser)' : 'Connecting...'}
        </div>
      </div>

      <div className="absolute top-32 left-8 z-50 pointer-events-auto">
        <ModelUploader onModelLoad={(data) => setModelData(data)} />
      </div>

      <GestureGuide />

      <button 
        onClick={() => router.push('/')}
        className="absolute bottom-8 left-8 z-50 glass px-4 py-2 rounded-lg flex items-center gap-2 text-red-400 hover:bg-red-500/20 border border-red-500/30 transition-colors pointer-events-auto"
      >
        <LogOut size={16} />
        <span className="text-xs font-bold tracking-widest uppercase">Terminate Session</span>
      </button>
    </div>
  );
}
