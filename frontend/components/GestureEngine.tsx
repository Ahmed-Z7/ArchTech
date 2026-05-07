import React, { useEffect, useRef } from 'react';

// Use any to bypass MediaPipe type resolution issues on Vercel
declare global {
  interface Window {
    Hands: any;
    Camera: any;
    drawConnectors: any;
    drawLandmarks: any;
    HAND_CONNECTIONS: any;
  }
}

interface GestureEngineProps {
  onGestureData: (data: any) => void;
  enabled: boolean;
}

export default function GestureEngine({ onGestureData, enabled }: GestureEngineProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!enabled || !videoRef.current || !canvasRef.current) return;

    // Load scripts dynamically to ensure they are available on the window
    const loadScript = (src: string) => {
      return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        document.head.appendChild(script);
      });
    };

    const init = async () => {
      await Promise.all([
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js'),
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js'),
        loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js'),
      ]);

      const Hands = (window as any).Hands;
      const Camera = (window as any).Camera;
      const drawConnectors = (window as any).drawConnectors;
      const drawLandmarks = (window as any).drawLandmarks;
      const HAND_CONNECTIONS = (window as any).HAND_CONNECTIONS;

      const hands = new Hands({
        locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });

      hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });

      const classifyGesture = (landmarks: any, handedness: string) => {
        const tips = [4, 8, 12, 16, 20];
        const fingerStates = [];

        // Thumb
        if (handedness === 'Right') {
          fingerStates.push(landmarks[4].x < landmarks[3].x ? 1 : 0);
        } else {
          fingerStates.push(landmarks[4].x > landmarks[3].x ? 1 : 0);
        }

        // Other fingers
        for (let i = 1; i < tips.length; i++) {
          fingerStates.push(landmarks[tips[i]].y < landmarks[tips[i] - 2].y ? 1 : 0);
        }

        const sum = fingerStates.reduce((a, b) => a + b, 0);
        
        // Click Detection
        const tiDist = Math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y);
        if (tiDist < 0.035) return "CLICK";

        if (sum === 0) return "FIST";
        if (sum === 5) return "PALM";
        if (sum === 1 && fingerStates[1]) return "INDEX";
        if (sum === 2 && fingerStates[1] && fingerStates[2]) return "TWO";
        if (sum === 3 && fingerStates[1] && fingerStates[2] && fingerStates[3]) return "THREE";
        if (sum === 4 && fingerStates[1] && fingerStates[2] && fingerStates[3] && fingerStates[4]) return "FOUR";
        
        return "OTHER";
      };

      hands.onResults((results: any) => {
        if (!canvasRef.current || !videoRef.current) return;
        
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        ctx.save();
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        
        const handsData: any[] = [];
        let special_gesture = "NONE";
        let palm_distance = 0;

        if (results.multiHandLandmarks) {
          for (let i = 0; i < results.multiHandLandmarks.length; i++) {
            const landmarks = results.multiHandLandmarks[i];
            const label = results.multiHandedness[i].label;
            const gesture = classifyGesture(landmarks, label);
            
            const active_fingers = landmarks.slice(4, 21).filter((_: any, idx: number) => idx % 4 === 0).length; // Rough count

            handsData.push({
              label,
              gesture,
              palm_center: { x: landmarks[9].x, y: landmarks[9].y },
              index_tip: { x: landmarks[8].x, y: landmarks[8].y },
              thumb_tip: { x: landmarks[4].x, y: landmarks[4].y },
              active_fingers: gesture === "PALM" ? 5 : (gesture === "INDEX" ? 1 : 0) // Simplified for special check
            });

            drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: '#00F3FF', lineWidth: 2 });
            drawLandmarks(ctx, landmarks, { color: '#BC13FE', lineWidth: 1, radius: 2 });
          }

          if (handsData.length === 2) {
            const h1 = handsData[0];
            const h2 = handsData[1];
            
            palm_distance = Math.hypot(h1.palm_center.x - h2.palm_center.x, h1.palm_center.y - h2.palm_center.y);
            
            if (h1.gesture === "PALM" && h2.gesture === "PALM") special_gesture = "TEN_FINGERS";
            else if ((h1.gesture === "PALM" && h2.gesture === "INDEX") || (h1.gesture === "INDEX" && h2.gesture === "PALM")) special_gesture = "SIX_FINGERS";
          }
        }
        ctx.restore();

        onGestureData({
          hands: handsData,
          hand_count: handsData.length,
          special_gesture,
          palm_distance,
          source: 'browser'
        });
      });

      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current) await hands.send({ image: videoRef.current });
        },
        width: 640,
        height: 480,
      });

      camera.start();
    };

    init();
  }, [enabled, onGestureData]);

  return (
    <div className="fixed bottom-4 right-4 z-[100] w-48 h-36 border-2 border-cyan-500/30 rounded-lg overflow-hidden bg-black/50 shadow-[0_0_20px_rgba(0,243,255,0.2)]">
      <video ref={videoRef} className="hidden" />
      <canvas ref={canvasRef} className="w-full h-full object-cover scale-x-[-1]" width={640} height={480} />
      <div className="absolute top-2 left-2 flex items-center gap-1">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        <span className="text-[10px] text-green-500 font-mono tracking-tighter uppercase">AR Engine Active</span>
      </div>
    </div>
  );
}
