import React, { useRef, useEffect } from 'react';

interface WebcamOverlayProps {
  hands: any[];
}

const WebcamOverlay: React.FC<WebcamOverlayProps> = ({ hands }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    hands.forEach((hand) => {
      if (!hand || !hand.raw_landmarks) return;
      
      ctx.fillStyle = hand.label === 'Right' ? '#00f3ff' : '#bc13fe';
      ctx.strokeStyle = '#ffffff55';
      ctx.lineWidth = 1;

      hand.raw_landmarks.forEach((lm: any) => {
        const x = lm.x * canvas.width;
        const y = lm.y * canvas.height;
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
      });

      const connections = [
        [0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [0, 17, 18, 19, 20],
        [5, 9, 13, 17], [9, 10, 11, 12], [13, 14, 15, 16]
      ];

      ctx.beginPath();
      connections.forEach(path => {
        if (!hand.raw_landmarks[path[0]]) return;
        ctx.moveTo(hand.raw_landmarks[path[0]].x * canvas.width, hand.raw_landmarks[path[0]].y * canvas.height);
        for(let i=1; i<path.length; i++) {
          if (!hand.raw_landmarks[path[i]]) continue;
          ctx.lineTo(hand.raw_landmarks[path[i]].x * canvas.width, hand.raw_landmarks[path[i]].y * canvas.height);
        }
      });
      ctx.stroke();
    });
  }, [hands]);

  return (
    <div className="fixed top-24 right-6 w-64 h-48 glass rounded-xl border border-cyan-500/30 overflow-hidden group">
      <div className="absolute top-0 left-0 bg-cyan-500 text-[8px] px-2 py-0.5 font-bold uppercase tracking-tighter">
        Live Feed: Tracking-Link
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent h-1/4 w-full animate-scan-slow pointer-events-none" />
      <canvas ref={canvasRef} width={320} height={240} className="w-full h-full object-cover opacity-80" />
      <div className="absolute bottom-2 left-2 flex gap-1">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="w-1 h-3 bg-cyan-500/50 animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
        ))}
      </div>
    </div>
  );
};

export default WebcamOverlay;
