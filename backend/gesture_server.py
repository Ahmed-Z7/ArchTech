import cv2
import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from gestures import GestureEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = GestureEngine()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            data = engine.process_frame(frame)
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"WS Error: {e}")
    finally:
        cap.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
