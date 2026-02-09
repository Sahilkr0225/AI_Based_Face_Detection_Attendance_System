from fastapi import FastAPI
import cv2
from ai_engine.face_detection.detector import detect_faces

app = FastAPI()

# temporary structure
attendance = {}

# create classroom
@app.post("/session/start")
def start_session(student_count: int):
    global attendance
    attendance = {}

    for i in range(student_count):
        attendance[f"student_{i+1}"] = {
            "start": False,
            "mid": False,
            "end": False
        }

    return {"message": "Session started", "students": list(attendance.keys())}


# webcam scan
@app.post("/scan/{scan_type}")
def webcam_scan(scan_type: str):
    global attendance

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {"error": "Camera not accessible"}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"error": "Frame capture failed"}

    faces = detect_faces(frame)

    detected = min(len(faces), len(attendance))

    students = list(attendance.keys())

    for i in range(detected):
        attendance[students[i]][scan_type] = True

    return {
        "scan_type": scan_type,
        "faces_detected": len(faces)
    }


# final result
@app.get("/result")
def result():
    final = {}

    for student, logs in attendance.items():
        if logs["start"] and logs["mid"] and logs["end"]:
            final[student] = "PRESENT"
        else:
            final[student] = "ABSENT"

    return final
