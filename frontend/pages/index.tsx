import React, { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Activity, Lock, Cpu, Database, FolderOpen } from 'lucide-react';

export default function Dashboard() {
  const router = useRouter();
  const [booting, setBooting] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  const startBootServer = () => {
    setBooting(true);
    const systemLogs = [
      "> AUTHENTICATING USER...",
      "> DECRYPTING NEURAL PROTOCOLS...",
      "> CONNECTING TO STARK-LINK [PORT 8000]...",
      "> WARMING UP 3D RENDERING ENGINE...",
      "> READY. TRANSFERRING TO WORKSPACE."
    ];
    
    systemLogs.forEach((log, i) => {
      setTimeout(() => {
        setLogs(prev => [...prev, log]);
        if (i === systemLogs.length - 1) {
          setTimeout(() => router.push('/workspace'), 1000);
        }
      }, i * 400);
    });
  };

  return (
    <div className="w-screen h-screen bg-[#020205] text-white overflow-hidden scanlines relative font-['Rajdhani']">
      <Head><title>ARCH-TECH | DASHBOARD</title></Head>

      <AnimatePresence mode="wait">
        {!booting ? (
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ scale: 1.1, opacity: 0 }}
            className="w-full h-full p-12 flex flex-col justify-between relative z-10"
          >
            <div className="flex justify-between items-start border-b border-cyan-500/20 pb-6">
              <div>
                 <h1 className="text-5xl font-bold tracking-[0.3em] text-white">ARCH<span className="text-cyan-400">TECH</span></h1>
                 <p className="text-cyan-500/50 tracking-[0.6em] text-xs uppercase">Command Center v2.5</p>
              </div>
              <div className="flex items-center gap-8 text-[12px] text-gray-500 font-mono tracking-widest">
                 <div className="flex flex-col items-end">
                    <span className="text-cyan-400">MAIN REACTOR</span>
                    <span>ONLINE / STABLE</span>
                 </div>
                 <Activity size={32} className="text-cyan-400" />
              </div>
            </div>

            <div className="flex flex-1 gap-12 mt-12 mb-12">
               <div className="flex-1 glass p-8 rounded-2xl border-l-4 border-cyan-400 relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent pointer-events-none" />
                  <div className="flex justify-between items-center mb-8">
                     <h2 className="text-2xl font-bold tracking-widest text-[#00f3ff]">PROJECT DATABASE</h2>
                     <Database className="text-cyan-400" />
                  </div>
                  <div className="space-y-4">
                     {['Stark Tower Concept', 'Echo Base Layout', 'Quantum Bridge'].map((proj, i) => (
                        <div key={i} className="flex justify-between items-center p-4 border border-white/10 rounded-lg hover:border-cyan-400 transition-all cursor-pointer hover:bg-cyan-500/10">
                           <div className="flex items-center gap-4">
                              <FolderOpen size={16} className="text-purple-400" />
                              <span className="font-mono text-sm tracking-widest">{proj}</span>
                           </div>
                           <span className="text-[10px] opacity-40 uppercase tracking-widest">v1.0.{i}</span>
                        </div>
                     ))}
                  </div>
               </div>

               <div className="w-[400px] flex flex-col justify-end gap-6">
                  <div className="glass p-6 rounded-xl border border-purple-500/30 text-xs text-purple-200/60 font-mono tracking-widest space-y-2">
                     <p>» DUAL-HAND TRACKING REQUIRED</p>
                     <p>» WEBCAM ACCESS REQUIRED</p>
                     <p>» HIGH-PERFORMANCE GPU RECOMMENDED</p>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 243, 255, 0.4)" }}
                    whileTap={{ scale: 0.95 }}
                    onClick={startBootServer}
                    className="relative w-full h-32 bg-cyan-500/10 border border-cyan-400 text-cyan-400 font-bold tracking-[0.2em] rounded-xl hover:bg-cyan-400 hover:text-black transition-all group overflow-hidden"
                  >
                    <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 z-10">
                       <Zap size={24} className="group-hover:animate-bounce" />
                       <span className="text-xl">ENTER WORKSPACE</span>
                    </div>
                  </motion.button>
               </div>
            </div>

            <div className="flex justify-between items-end border-t border-cyan-500/20 pt-6 text-[10px] text-gray-600 tracking-widest font-mono">
              <span className="flex items-center gap-2"><Lock size={12}/> ENCRYPTED</span>
              <span className="flex items-center gap-2"><Cpu size={12}/> SYSTEM Vitals: NOMINAL</span>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="booting"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-50 bg-black p-24 font-mono text-cyan-500/80 flex flex-col justify-center"
          >
            <div className="max-w-4xl mx-auto w-full space-y-4">
               {logs.map((log, i) => (
                 <motion.div 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={i}
                  className="flex items-center gap-4 text-xl"
                 >
                   <span className="opacity-40">[{new Date().toLocaleTimeString()}]</span>
                   <span className={i === logs.length - 1 ? "text-white glow-cyan font-bold" : ""}>{log}</span>
                 </motion.div>
               ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
