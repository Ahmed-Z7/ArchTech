import React, { useState } from 'react';
import { HelpCircle, X, Maximize2, Rotate3D, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const commands = [
  { name: 'ORBIT ROTATION', icon: <Rotate3D size={24} className="text-cyan-400" />, gesture: 'PALM (POINT & HOLD)', desc: 'Show an open palm. Hold it and move your hand around to smoothly orbit and rotate the 3D object.', color: 'border-cyan-500' },
  { name: 'DYNAMIC ZOOM', icon: <Maximize2 size={24} className="text-purple-400" />, gesture: 'PINCH', desc: 'Pinch your thumb and index finger together. Adjust the distance to dynamically scale the object up or down.', color: 'border-purple-500' },
  { name: 'SYSTEM RESET', icon: <RotateCcw size={24} className="text-yellow-400" />, gesture: 'THREE FINGERS', desc: 'Show exactly 3 fingers to the camera. This instantly resets the object scale and rotation back to default and resumes auto-spin.', color: 'border-yellow-500' },
];

export default function GestureGuide() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 z-[100] w-14 h-14 bg-cyan-500/10 border border-cyan-400 rounded-full flex items-center justify-center text-cyan-400 hover:bg-cyan-400 hover:text-black transition-all shadow-[0_0_15px_#00f3ff] pointer-events-auto"
      >
        <HelpCircle size={28} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed inset-0 z-[200] flex flex-col justify-end p-8 pointer-events-none"
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm pointer-events-auto" onClick={() => setIsOpen(false)} />
            <div className="relative w-full max-w-5xl mx-auto flex flex-col gap-6 pointer-events-auto max-h-[85vh] overflow-y-auto custom-scrollbar pb-12">
              <div className="flex justify-between items-center bg-[#020205] border border-cyan-500 px-8 py-4 rounded-xl shadow-[0_0_30px_rgba(0,243,255,0.2)]">
                <h2 className="text-3xl font-bold tracking-[0.2em] text-[#00f3ff] font-['Orbitron']">NEURAL LINK PROTOCOLS</h2>
                <button onClick={() => setIsOpen(false)} className="text-cyan-400 hover:text-white"><X size={32} /></button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {commands.map((cmd, i) => (
                  <motion.div key={i} className={`bg-black/80 border-l-4 ${cmd.color} p-6 rounded-r-xl flex flex-col gap-4 items-start hover:bg-cyan-900/20 transition-colors`}>
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-white/5 rounded-lg border border-white/10 shrink-0">{cmd.icon}</div>
                        <h3 className="text-lg font-bold font-mono tracking-widest text-white">{cmd.name}</h3>
                    </div>
                    <div>
                      <span className={`inline-block px-2 py-1 bg-white/5 text-[10px] font-bold tracking-widest mb-3 rounded-full border border-current ${cmd.color.replace('border-', 'text-')}`}>
                        GESTURE: {cmd.gesture}
                      </span>
                      <p className="text-sm text-gray-400 font-['Rajdhani'] leading-relaxed">{cmd.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
