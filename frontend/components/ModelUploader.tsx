import React, { useCallback, useState } from 'react';
import { UploadCloud, CheckCircle } from 'lucide-react';

interface ModelUploaderProps {
  onModelLoad: (data: { url: string; ext: string }) => void;
}

const ModelUploader: React.FC<ModelUploaderProps> = ({ onModelLoad }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsHovered(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
      if (['.glb', '.gltf', '.obj'].includes(ext)) {
        const url = URL.createObjectURL(file);
        setFileName(file.name);
        onModelLoad({ url, ext });
      } else {
        alert('Only .glb, .gltf, or .obj files are supported right now.');
      }
    }
  }, [onModelLoad]);

  return (
    <div 
      className={`glass w-64 p-4 rounded-xl border transition-all duration-300 ${
        isHovered ? 'border-cyan-400 bg-cyan-500/20' : 'border-cyan-500/30'
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsHovered(true); }}
      onDragLeave={() => setIsHovered(false)}
      onDrop={handleDrop}
    >
      <div className="flex flex-col items-center gap-2 text-center pointer-events-none">
        {fileName ? (
           <CheckCircle className="text-green-400 animate-pulse" size={32} />
        ) : (
           <UploadCloud className={`transition-colors ${isHovered ? 'text-cyan-400' : 'text-gray-400'}`} size={32} />
        )}
        <div>
           <p className="text-xs font-bold tracking-widest uppercase text-[#00f3ff]">
             {fileName ? 'MODEL LOADED' : 'DROP 3D MODEL'}
           </p>
           <p className="text-[9px] opacity-50 font-mono mt-1">
             {fileName || 'Supported: .GLB, .GLTF, .OBJ'}
           </p>
        </div>
      </div>
      <input 
        type="file" 
        accept=".glb,.gltf,.obj" 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer pointer-events-auto"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
            const url = URL.createObjectURL(file);
            setFileName(file.name);
            onModelLoad({ url, ext });
          }
        }}
      />
    </div>
  );
};

export default ModelUploader;
