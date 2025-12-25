import face_recognition
import os
import pickle

IMAGE_DIR = "../anhgoc"
ENCODE_FILE = "encodings.pickle"

known_encodings = []
known_names = []

for file in os.listdir(IMAGE_DIR):
    if file.lower().endswith((".jpg", ".png")):
        path = os.path.join(IMAGE_DIR, file)
        name = os.path.splitext(file)[0]

        image = face_recognition.load_image_file(path)
        encs = face_recognition.face_encodings(image)

        if len(encs) == 0:
            print(f"Không tìm thấy khuôn mặt: {file}")
            continue

        known_encodings.append(encs[0])
        known_names.append(name)
        print(f"Encode OK: {name}")

data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(ENCODE_FILE, "wb") as f:
    pickle.dump(data, f)

print("Encode xong tất cả ảnh học sinh!")
