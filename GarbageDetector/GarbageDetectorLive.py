import cv2
import math
import cvzone
import hashlib
import sqlite3
from ultralytics import YOLO

conn = sqlite3.connect("video_hashes.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS video_hashes (hash TEXT PRIMARY KEY)")
conn.commit()

user_conn = sqlite3.connect("users.db")
user_cursor = user_conn.cursor()
user_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, coins INTEGER)")
user_conn.commit()

def get_video_hash(video_path):
    hasher = hashlib.md5()
    with open(video_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_duplicate(video_hash):
    cursor.execute("SELECT hash FROM video_hashes WHERE hash=?", (video_hash,))
    return cursor.fetchone() is not None

def save_hash(video_hash):
    cursor.execute("INSERT INTO video_hashes (hash) VALUES (?)", (video_hash,))
    conn.commit()

def get_user_coins():
    user_cursor.execute("SELECT coins FROM users WHERE id=1")
    result = user_cursor.fetchone()
    return result[0] if result else 0

def update_user_coins():
    current_coins = get_user_coins()
    new_coins = current_coins + 5
    user_cursor.execute("INSERT OR REPLACE INTO users (id, coins) VALUES (1, ?)", (new_coins,))
    user_conn.commit()
    print(f"User rewarded! Total Coins: {new_coins}")

video_path = "Media/garbage.mp4"

video_hash = get_video_hash(video_path)
print(f"\nVideo Hash: {video_hash}\n")

if is_duplicate(video_hash):
    print("Duplicate video detected! Upload a different video.")
    exit()
else:
    print("New video detected. Processing...")
    save_hash(video_hash)

cap = cv2.VideoCapture(video_path)

model = YOLO("Weights/best.pt")

classNames = ['0', 'c', 'garbage', 'garbage_bag', 'sampah-detection', 'trash']

garbage_detected = False  

frame_count = 0
max_frames = None
stop_processing = False

fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video Info: {fps} FPS, {total_frames} total frames")

print("Controls:")
print("  - Press 'q' to quit")
print("  - Press 's' to stop processing and reward coins")
print("  - Press 'p' to pause/unpause")
print("  - Press SPACE to step frame by frame (when paused)")

paused = False

while True:
    if not paused:
        success, img = cap.read()
        if not success:
            print("Video processing complete.")
            break
        
        frame_count += 1
        
        if max_frames and frame_count >= max_frames:
            print(f"Video cut at frame {frame_count}")
            stop_processing = True
            break

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w, h = x2 - x1, y2 - y1
                conf = round(float(box.conf[0]), 2)
                cls = int(box.cls[0])

                if conf > 0.1 and classNames[cls] in ['garbage', 'garbage_bag', 'trash']:
                    garbage_detected = True
                    cvzone.cornerRect(img, (x1, y1, w, h), t=2)
                    cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)
        
        progress_text = f"Frame: {frame_count}/{total_frames} | Progress: {(frame_count/total_frames)*100:.1f}%"
        cvzone.putTextRect(img, progress_text, (10, 30), scale=0.8, thickness=1, colorR=(0, 0, 255))
        
        status_text = "Garbage Detected: YES" if garbage_detected else "Garbage Detected: NO"
        cvzone.putTextRect(img, status_text, (10, 70), scale=0.8, thickness=1, 
        colorR=(0, 255, 0) if garbage_detected else (0, 0, 255))

    cv2.imshow("Garbage Detection", img)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        print("Quit requested by user")
        break
    elif key == ord('s'):
        print("Stop processing requested by user")
        stop_processing = True
        break
    elif key == ord('p'):
        paused = not paused
        print("Paused" if paused else "Resumed")
    elif key == ord(' ') and paused:
        success, img = cap.read()
        if success:
            frame_count += 1
            results = model(img, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w, h = x2 - x1, y2 - y1
                    conf = round(float(box.conf[0]), 2)
                    cls = int(box.cls[0])
                    if conf > 0.1 and classNames[cls] in ['garbage', 'garbage_bag', 'trash']:
                        garbage_detected = True
                        cvzone.cornerRect(img, (x1, y1, w, h), t=2)
                        cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)

if garbage_detected:
    update_user_coins()
else:
    print("No garbage detected. No coins rewarded.")

cap.release()
cv2.destroyAllWindows()

conn.close()
user_conn.close()

print("\nProcessing finished!")
print(f"Final Stats:")
print(f"   - Frames processed: {frame_count}")
print(f"   - Garbage detected: {'Yes' if garbage_detected else 'No'}")
print(f"   - Total user coins: {get_user_coins()}")