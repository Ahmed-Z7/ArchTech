import React, { useRef, useState, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree, useLoader } from '@react-three/fiber';
import { PerspectiveCamera, Grid, Center, Bounds, useGLTF, Html, useBounds } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';

const HOLO_COLOR_1 = "#00f3ff";
const HOLO_COLOR_2 = "#bc13fe";

// ─── Details Panel Component ──────────────────────────────────────────────────
const DetailsPanel = ({ active, data }: { active: boolean; data: any }) => {
  if (!active) return null;
  return (
    <Html center position={[5, 2, 0]}>
      <div className="glass p-6 rounded-xl w-[320px] border-l-4 border-l-cyan-500 animate-in fade-in slide-in-from-left duration-500">
        <h2 className="text-cyan-400 font-bold text-xl tracking-tighter mb-4 uppercase">{data.name || "ARCH-TECH STRUCTURE"}</h2>
        <div className="space-y-3 font-mono text-[10px]">
          <div className="flex justify-between border-b border-white/10 pb-1">
            <span className="opacity-50">START DATE:</span>
            <span>2024-01-15</span>
          </div>
          <div className="flex justify-between border-b border-white/10 pb-1">
            <span className="opacity-50">EST. COMPLETION:</span>
            <span>2026-12-20</span>
          </div>
          <div className="flex justify-between border-b border-white/10 pb-1">
            <span className="opacity-50">CONCRETE:</span>
            <span className="text-cyan-400">12,450 m³</span>
          </div>
          <div className="flex justify-between border-b border-white/10 pb-1">
            <span className="opacity-50">IRON REINFORCEMENT:</span>
            <span className="text-cyan-400">2,800 Tons</span>
          </div>
          <div className="mt-4">
            <div className="flex justify-between mb-1">
              <span className="opacity-50 uppercase text-[8px]">Construction Progress</span>
              <span className="text-cyan-400">68%</span>
            </div>
            <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-500 shadow-[0_0_10px_#00f3ff]" style={{ width: '68%' }} />
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/10">
            <span className="opacity-50 text-[8px]">ACTIVE WORKFORCE:</span>
            <div className="flex gap-2 mt-2">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/50 flex items-center justify-center text-[8px]">W{i}</div>
              ))}
              <div className="w-6 h-6 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-[8px] opacity-50">+12</div>
            </div>
          </div>
        </div>
      </div>
    </Html>
  );
};

// ─── Building with Floor Logic ────────────────────────────────────────────────
const Building = ({ url, viewLevel, scanIndex, onSelect }: any) => {
  const { scene } = useGLTF(url) as any;
  const groupRef = useRef<THREE.Group>(null);
  const bounds = useBounds();

  // Divide building into 4 floors based on Y height
  const floors = useMemo(() => {
    const box = new THREE.Box3().setFromObject(scene);
    const min = box.min.y;
    const max = box.max.y;
    const height = max - min;
    const floorHeight = height / 4;

    return [1, 2, 3, 4].map(i => ({
      index: i,
      minY: min + (i - 1) * floorHeight,
      maxY: min + i * floorHeight,
      center: min + (i - 0.5) * floorHeight
    }));
  }, [scene]);

  useFrame((state) => {
    if (!groupRef.current) return;
    
    // Apply glowing effect to scan index
    scene.traverse((child: any) => {
      if (child.isMesh) {
        const floor = floors.find(f => child.position.y >= f.minY && child.position.y < f.maxY);
        if (floor && floor.index === scanIndex) {
          child.material.emissive = new THREE.Color(HOLO_COLOR_2);
          child.material.emissiveIntensity = Math.sin(state.clock.elapsedTime * 10) * 0.5 + 0.5;
        } else {
          child.material.emissive = new THREE.Color(0, 0, 0);
          child.material.emissiveIntensity = 0;
        }
      }
    });
  });

  return (
    <Center>
      <primitive object={scene} ref={groupRef} onClick={(e: any) => { e.stopPropagation(); onSelect(); }} />
      {scanIndex > 0 && (
        <Html position={[0, floors[scanIndex-1].center, 0]}>
          <div className="text-pink-500 font-black text-6xl animate-pulse-pink drop-shadow-[0_0_20px_#bc13fe]">
            LEVEL {scanIndex}
          </div>
        </Html>
      )}
    </Center>
  );
};

// ─── Hologram Navigation Engine (Heavy Duty) ──────────────────────────────────
const HologramNavigationEngine = ({ handsRef, modelUrl }: any) => {
  const groupRef = useRef<THREE.Group>(null);
  const { camera, size } = useThree();
  
  // Navigation State
  const [viewLevel, setViewLevel] = useState('GLOBAL'); // GLOBAL, FLOOR, DEPT, ROOM
  const [scanIndex, setScanIndex] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  
  // Persistent refs for smoothness
  const orbitRef = useRef({ rx: 0, ry: 0 });
  const zoomRef = useRef(20);
  const lastSpecialRef = useRef("NONE");
  const clickCooldown = useRef(0);

  useEffect(() => {
    // Initial camera position
    gsap.to(camera.position, { z: 25, duration: 2, ease: "expo.out" });
  }, []);

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    const data = handsRef.current || { hands: [], special_gesture: "NONE", palm_distance: 0 };
    const h1 = data.hands[0];
    const sg = data.special_gesture;
    
    // 1. ISOLATION: Handle Special Gestures FIRST
    if (sg !== lastSpecialRef.current) {
      if (sg === "SIX_FINGERS") {
        // Start Cinematic Scan Sequence
        setViewLevel('SCAN');
        gsap.to(camera.position, { x: 15, y: 10, z: 25, duration: 1.5, ease: "power3.inOut" });
        gsap.to(camera.rotation, { x: -0.3, y: 0.5, z: 0, duration: 1.5 });
        
        let idx = 1;
        const interval = setInterval(() => {
          setScanIndex(idx);
          if (idx > 4) {
            clearInterval(interval);
            setScanIndex(0);
            setViewLevel('GLOBAL');
            // Back to center
            gsap.to(camera.position, { x: 0, y: 0, z: 20, duration: 1 });
          }
          idx++;
        }, 6000);
      } else if (sg === "TEN_FINGERS") {
        // Full Reset
        setViewLevel('GLOBAL');
        setScanIndex(0);
        setShowDetails(false);
        gsap.to(camera.position, { x: 0, y: 0, z: 25, duration: 1.5, ease: "expo.out" });
      } else if (sg.startsWith("GOTO_FLOOR_")) {
        const fIdx = parseInt(sg.split('_').pop() || "1");
        setViewLevel('FLOOR');
        // Cinematic Zoom to Floor
        gsap.to(camera.position, { x: 0, y: (fIdx-2.5)*4, z: 8, duration: 2, ease: "power4.out" });
      }
      lastSpecialRef.current = sg;
    }

    // 2. FIST -> Back
    if (h1?.gesture === "FIST" && viewLevel !== 'GLOBAL') {
      setViewLevel('GLOBAL');
      gsap.to(camera.position, { x: 0, y: 0, z: 25, duration: 1 });
    }

    // 3. CLICK -> Toggle Details
    if (h1?.gesture === "CLICK" && clickCooldown.current === 0) {
      setShowDetails(!showDetails);
      clickCooldown.current = 30; // 0.5s cooldown
    }
    if (clickCooldown.current > 0) clickCooldown.current--;

    // 4. SUPER ZOOM (Dual Palm Distance)
    if (data.palm_distance > 0) {
      // Map 0.1-0.8 to zoom range 5-40 (Inverted)
      const targetZ = 5 + (1 - data.palm_distance) * 40;
      zoomRef.current = THREE.MathUtils.lerp(zoomRef.current, targetZ, 0.1);
      camera.position.z = zoomRef.current;
    }

    // 5. 360 ORBIT CONTROL (Palm Move)
    if (h1?.gesture === "PALM" && sg === "NONE") {
      const dx = (h1.palm_center.x - 0.5) * 4.0;
      const dy = (h1.palm_center.y - 0.5) * -4.0;
      
      if (viewLevel === 'GLOBAL') {
        // Rotate Model
        groupRef.current.rotation.y = THREE.MathUtils.lerp(groupRef.current.rotation.y, dx * Math.PI, 0.1);
        groupRef.current.rotation.x = THREE.MathUtils.lerp(groupRef.current.rotation.x, dy * Math.PI, 0.1);
      } else {
        // Rotate Camera (Immersive)
        camera.rotation.y = THREE.MathUtils.lerp(camera.rotation.y, dx, 0.1);
        camera.rotation.x = THREE.MathUtils.lerp(camera.rotation.x, dy, 0.1);
      }
    }
  });

  return (
    <group ref={groupRef}>
      <Bounds fit clip observe margin={1.2}>
        <Building 
          url={modelUrl} 
          viewLevel={viewLevel} 
          scanIndex={scanIndex} 
          onSelect={() => setShowDetails(true)} 
        />
      </Bounds>
      <DetailsPanel active={showDetails} data={{ name: "METROPOLIS TOWER v.2" }} />
    </group>
  );
};

export default function Viewer({ hands, modelData }: any) {
  const handsRef = useRef(hands);
  useEffect(() => { handsRef.current = hands; }, [hands]);

  // Use requested house.glb or default
  const modelUrl = modelData?.url || "/models/house.glb";

  return (
    <div className="w-full h-full bg-[#020204] relative grid-bg overflow-hidden">
      <Canvas shadows dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 30]} fov={35} />
        
        <ambientLight intensity={0.5} />
        <pointLight position={[20, 20, 20]} intensity={2} color={HOLO_COLOR_1} />
        <spotLight position={[-20, 20, 20]} angle={0.5} penumbra={1} color={HOLO_COLOR_2} intensity={3} castShadow />
        
        <React.Suspense fallback={null}>
          <HologramNavigationEngine handsRef={handsRef} modelUrl={modelUrl} />
        </React.Suspense>

        <Grid 
          position={[0, -10, 0]} 
          infiniteGrid 
          fadeDistance={50} 
          fadeStrength={5} 
          cellSize={1} 
          sectionSize={5} 
          sectionColor={HOLO_COLOR_1} 
          cellColor="#080815" 
        />
      </Canvas>

      {/* Futuristic HUD Overlay Decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full border-[1px] border-cyan-500/10 mix-blend-overlay" />
        <div className="absolute top-10 left-10 w-20 h-20 border-t-2 border-l-2 border-cyan-500/40" />
        <div className="absolute top-10 right-10 w-20 h-20 border-t-2 border-r-2 border-cyan-500/40" />
        <div className="absolute bottom-10 left-10 w-20 h-20 border-b-2 border-l-2 border-cyan-500/40" />
        <div className="absolute bottom-10 right-10 w-20 h-20 border-b-2 border-r-2 border-cyan-500/40" />
      </div>
    </div>
  );
}
