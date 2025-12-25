from flask import Flask, request, jsonify
import face_recognition
import cv2
import pickle
import numpy as np
import os
from datetime import datetime, date
import base64
import shutil

app = Flask(__name__)

DATA_FILE = "attendance_today.csv"
STORAGE_DIR = "storage"
CLASS_NAME = "11A1"   # tạm fix cứng

# ================= LOAD ENCODINGS =================
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# ================= XOAY FILE THEO NGÀY =================
def rotate_daily_file():
    if not os.path.exists(DATA_FILE):
        return

    today = date.today().isoformat()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return

    first_date = lines[0].split(",")[0]
    if first_date != today:
        archive = os.path.join(STORAGE_DIR, f"{first_date}.csv")
        shutil.move(DATA_FILE, archive)

# ================= API ĐIỂM DANH =================
@app.route("/attendance", methods=["POST"])
def attendance():
    rotate_daily_file()

    img_data = request.json.get("image")
    if not img_data:
        return jsonify({"status": "error", "message": "Không có ảnh"})

    # Decode base64 → ảnh
    img_bytes = base64.b64decode(img_data.split(",")[1])
    np_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    if not encodings:
        return jsonify({"status": "fail", "message": "Không phát hiện khuôn mặt"})

    encoding = encodings[0]
    distances = face_recognition.face_distance(data["encodings"], encoding)
    min_dist = float(np.min(distances))
    accuracy = round((1 - min_dist) * 100, 2)

    if accuracy < 90:
        return jsonify({
            "status": "fail",
            "message": "Không khớp",
            "accuracy": accuracy
        })

    idx = int(np.argmin(distances))
    name = data["names"][idx]
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M:%S")
    image_name = f"{name}.jpg"

    # Chống điểm danh trùng
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.split(",")[2] == name:
                    return jsonify({
                        "status": "success",
                        "name": name,
                        "accuracy": accuracy,
                        "message": "Đã điểm danh trước đó"
                    })

    # Ghi file: Ngày,Giờ,Tên,Lớp,Ảnh
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{today},{now_time},{name},{CLASS_NAME},{image_name}\n")

    return jsonify({
        "status": "success",
        "name": name,
        "accuracy": accuracy
    })

# ================= API LẤY DANH SÁCH HÔM NAY =================
@app.route("/today", methods=["GET"])
def today_list():
    if not os.path.exists(DATA_FILE):
        return jsonify([])

    result = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            d, t, name, cls, img = line.strip().split(",")
            result.append({
                "date": d,
                "time": t,
                "name": name,
                "class": cls,
                "image": img
            })

    return jsonify(result)

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(debug=True)
