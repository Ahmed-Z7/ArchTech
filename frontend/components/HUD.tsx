import React from 'react';
import { Activity, Shield, Cpu, Layers, Box, Maximize2 } from 'lucide-react';

const HUD = ({ hands, connected }: any) => {
  const h1 = hands[0] || { gesture: 'NONE' };
  
  return (
    <div className="absolute inset-0 pointer-events-none font-['Rajdhani']">
      {/* Top Left: System Stats */}
      <div className="absolute top-10 left-10 flex flex-col gap-4">
        <div className="glass px-4 py-2 flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-cyan-500 shadow-[0_0_10px_#00f3ff]' : 'bg-red-500'} animate-pulse`} />
          <div className="flex flex-col">
            <span className="text-[10px] opacity-50 font-bold uppercase tracking-widest">System Status</span>
            <span className="text-xs font-bold text-white uppercase">{connected ? 'Core Online' : 'Core Offline'}</span>
          </div>
        </div>
        
        <div className="flex gap-2">
          <StatBox icon={<Activity size={14} />} label="Sync" value="98.2%" />
          <StatBox icon={<Shield size={14} />} label="Security" value="Encrypted" />
        </div>
      </div>

      {/* Top Right: Hand Tracking Info */}
      <div className="absolute top-10 right-10 flex flex-col items-end gap-2">
        <div className="glass px-4 py-2 border-r-4 border-r-cyan-500 text-right">
          <span className="text-[10px] opacity-50 font-bold uppercase block">Active Gesture</span>
          <span className="text-xl font-black text-cyan-400 neon-text italic uppercase tracking-tighter">
            {h1.gesture}
          </span>
        </div>
        <div className="flex gap-2">
          <div className="glass px-3 py-1 flex items-center gap-2">
             <Cpu size={12} className="text-cyan-500" />
             <span className="text-[10px] font-mono">LATENCY: 12ms</span>
          </div>
        </div>
      </div>

      {/* Bottom Right: Navigation Context */}
      <div className="absolute bottom-10 right-10">
        <div className="glass p-4 min-w-[200px] border-b-4 border-b-pink-500">
          <div className="flex items-center gap-2 mb-3 border-b border-white/10 pb-2">
            <Layers size={16} className="text-pink-500" />
            <span className="text-sm font-bold uppercase tracking-widest">Structural View</span>
          </div>
          <div className="space-y-2">
            <NavLevel label="Building" active={true} />
            <NavLevel label="Floors" active={false} />
            <NavLevel label="Departments" active={false} />
            <NavLevel label="Rooms" active={false} />
          </div>
        </div>
      </div>

      {/* Bottom Center: Interaction Guide (Minimalist) */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4">
        <GuideItem gesture="6F" action="Cinematic Scan" />
        <GuideItem gesture="Palm-Dist" action="Super Zoom" />
        <GuideItem gesture="Tip-Touch" action="Data Access" />
        <GuideItem gesture="10F" action="Global Reset" />
      </div>

      {/* Overlay Vignette */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20 pointer-events-none" />
    </div>
  );
};

const StatBox = ({ icon, label, value }: any) => (
  <div className="glass px-3 py-2 flex items-center gap-3">
    <div className="text-cyan-500">{icon}</div>
    <div className="flex flex-col">
      <span className="text-[8px] opacity-50 font-bold uppercase">{label}</span>
      <span className="text-[10px] font-bold text-white">{value}</span>
    </div>
  </div>
);

const NavLevel = ({ label, active }: any) => (
  <div className={`flex items-center justify-between text-[10px] uppercase font-bold tracking-tighter ${active ? 'text-pink-400' : 'opacity-30'}`}>
    <span>{label}</span>
    <div className={`w-1 h-1 rounded-full ${active ? 'bg-pink-400 shadow-[0_0_5px_#bc13fe]' : 'bg-white'}`} />
  </div>
);

const GuideItem = ({ gesture, action }: any) => (
  <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1 rounded-md backdrop-blur-sm">
    <span className="text-[10px] font-black text-cyan-400 bg-cyan-400/20 px-1 rounded uppercase tracking-tighter">{gesture}</span>
    <span className="text-[10px] text-white/60 font-bold uppercase tracking-widest">{action}</span>
  </div>
);

export default HUD;