import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands

class GestureEngine:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2, 
            min_detection_confidence=0.85,
            min_tracking_confidence=0.85
        )
        self.tips = [4, 8, 12, 16, 20]
        
    def get_finger_states(self, landmarks, hand_label):
        f = []
        if hand_label == "Right":
            f.append(1 if landmarks[4].x < landmarks[3].x else 0)
        else:
            f.append(1 if landmarks[4].x > landmarks[3].x else 0)
        for t in self.tips[1:]:
            f.append(1 if landmarks[t].y < landmarks[t-2].y else 0)
        return f

    def classify_gesture(self, finger_states, landmarks):
        s = sum(finger_states)
        
        # Click Detection (Thumb tip to Index tip)
        ti_dist = math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y)
        if ti_dist < 0.035: return "CLICK"

        if s == 0: return "FIST"
        if s == 5: return "PALM"
        if s == 1 and finger_states[1]: return "INDEX"
        if s == 2 and finger_states[1] and finger_states[2]: return "TWO"
        if s == 3 and finger_states[1] and finger_states[2] and finger_states[3]: return "THREE"
        if s == 4 and finger_states[1] and finger_states[2] and finger_states[3] and finger_states[4]: return "FOUR"
        
        return "OTHER"

    def process_frame(self, frame):
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            hands_data = []
            special_gesture = "NONE"
            palm_dist = 0

            if results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    try:
                        label = results.multi_handedness[i].classification[0].label
                        landmarks = hand_landmarks.landmark
                        
                        if len(landmarks) < 21: continue
                        
                        f_states = self.get_finger_states(landmarks, label)
                        gesture = self.classify_gesture(f_states, landmarks)
                        
                        hands_data.append({
                            "label": label,
                            "gesture": gesture,
                            "index_tip": {"x": landmarks[8].x, "y": landmarks[8].y},
                            "thumb_tip": {"x": landmarks[4].x, "y": landmarks[4].y},
                            "palm_center": {"x": landmarks[9].x, "y": landmarks[9].y},
                            "active_fingers": sum(f_states)
                        })
                    except: continue

                # Multi-hand Logic
                if len(hands_data) == 2:
                    h1, h2 = hands_data[0], hands_data[1]
                    g1, g2 = h1["gesture"], h2["gesture"]
                    s1, s2 = h1["active_fingers"], h2["active_fingers"]

                    # Distance for Super Zoom
                    palm_dist = math.hypot(h1["palm_center"]["x"] - h2["palm_center"]["x"], 
                                           h1["palm_center"]["y"] - h2["palm_center"]["y"])

                    # 10 Fingers (Full Reset)
                    if s1 == 5 and s2 == 5:
                        special_gesture = "TEN_FINGERS"
                    # 6 Fingers (Cinematic Reveal)
                    elif (s1 == 5 and g2 == "INDEX") or (g1 == "INDEX" and s2 == 5):
                        special_gesture = "SIX_FINGERS"
                    # Numeric shortcuts (1, 2, 3...)
                    elif s1 == 5 and s2 in [1, 2, 3, 4]:
                        special_gesture = f"GOTO_FLOOR_{s2}"
                    elif s2 == 5 and s1 in [1, 2, 3, 4]:
                        special_gesture = f"GOTO_FLOOR_{s1}"

            return {
                "hands": hands_data,
                "hand_count": len(hands_data),
                "special_gesture": special_gesture,
                "palm_distance": palm_dist
            }
        except Exception as e:
            return {"hands": [], "hand_count": 0, "special_gesture": "NONE", "palm_distance": 0}
