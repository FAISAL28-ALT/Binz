from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import hashlib
import sqlite3
from werkzeug.utils import secure_filename
import traceback
import logging
from flask_cors import CORS  # Added for cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"), 
                              logging.StreamHandler()])

# Setup upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Modified YOLO model loading with better error handling
try:
    from ultralytics import YOLO
    model = YOLO("Weights/best.pt")
    logging.info("YOLO model loaded successfully.")
    # Class names
    classNames = ['0', 'c', 'garbage', 'garbage_bag', 'sampah-detection', 'trash']
    yolo_available = True
except Exception as e:
    logging.error(f"Error loading YOLO model: {e}")
    logging.error(traceback.format_exc())
    yolo_available = False
    model = None
    classNames = []

# Database connection function
def get_db_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# DB Setup with proper connection handling
try:
    video_db = get_db_connection("video_hashes.db")
    if video_db:
        cursor = video_db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS video_hashes (hash TEXT PRIMARY KEY)")
        video_db.commit()
        
    user_db = get_db_connection("users.db")
    if user_db:
        user_cursor = user_db.cursor()
        user_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, coins INTEGER)")
        user_db.commit()
        
    logging.info("Database setup complete")
except sqlite3.Error as e:
    logging.error(f"Database setup error: {e}")
    logging.error(traceback.format_exc())

def get_video_hash(path):
    """Calculate MD5 hash of video file"""
    hasher = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        logging.error(f"Error: File not found at {path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return None

def is_duplicate(video_hash):
    """Check if video hash exists in database"""
    try:
        if video_db:
            cursor = video_db.cursor()
            cursor.execute("SELECT hash FROM video_hashes WHERE hash=?", (video_hash,))
            return cursor.fetchone() is not None
        return False
    except sqlite3.Error as e:
        logging.error(f"Database error checking for duplicate: {e}")
        return False

def save_hash(video_hash):
    """Save video hash to database"""
    try:
        if video_db:
            cursor = video_db.cursor()
            cursor.execute("INSERT INTO video_hashes (hash) VALUES (?)", (video_hash,))
            video_db.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error saving hash: {e}")
        if video_db:
            video_db.rollback()

def get_user_id(email):
    """Get user ID from email or create if not exists"""
    try:
        if user_db:
            user_cursor = user_db.cursor()
            user_cursor.execute("SELECT id FROM users WHERE email=?", (email,))
            result = user_cursor.fetchone()
            return result[0] if result else None
        return None
    except sqlite3.Error as e:
        logging.error(f"Database error getting user: {e}")
        return None

def create_user(email, name):
    """Create new user and return ID"""
    try:
        if user_db:
            user_cursor = user_db.cursor()
            user_cursor.execute("INSERT INTO users (email, name, coins) VALUES (?, ?, 0)", (email, name))
            user_db.commit()
            return user_cursor.lastrowid
        return None
    except sqlite3.Error as e:
        logging.error(f"Database error creating user: {e}")
        if user_db:
            user_db.rollback()
        return None

def get_user_coins(user_id):
    """Get user coins from database"""
    try:
        if user_db:
            user_cursor = user_db.cursor()
            user_cursor.execute("SELECT coins FROM users WHERE id=?", (user_id,))
            result = user_cursor.fetchone()
            return result[0] if result else 0
        return 0
    except sqlite3.Error as e:
        logging.error(f"Database error getting coins: {e}")
        return 0

def update_user_coins(user_id):
    """Update user coins in database (+5)"""
    try:
        if user_db:
            coins = get_user_coins(user_id) + 5
            user_cursor = user_db.cursor()
            user_cursor.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))
            user_db.commit()
            return coins
        return 0
    except sqlite3.Error as e:
        logging.error(f"Database error updating coins: {e}")
        if user_db:
            user_db.rollback()
        return 0

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload.html')
def upload_page():
    return send_from_directory('.', 'upload.html')

@app.route('/uploadVideo', methods=['POST'])
def upload_video():
    """Handle video upload and garbage detection"""
    try:
        if 'video' not in request.files:
            logging.warning("No video file in request")
            return jsonify({"status": "error", "message": "No video file provided."})
        
        video = request.files['video']
        email = request.form.get('email')
        name = request.form.get('name')
        
        logging.info(f"Received upload request. Email: {email}, Name: {name}")
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required."})
            
        if video.filename == '':
            logging.warning("Empty filename")
            return jsonify({"status": "error", "message": "Empty filename."})

        # Check if YOLO is available
        if not yolo_available:
            return jsonify({"status": "error", "message": "YOLO model not available. Server configuration error."})

        # Get or create user
        user_id = get_user_id(email)
        if not user_id:
            user_id = create_user(email, name)
            if not user_id:
                return jsonify({"status": "error", "message": "Error creating user."})

        # Save video file
        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        logging.info(f"Saving video to: {video_path}")
        
        try:
            video.save(video_path)
            logging.info(f"Video saved successfully to: {video_path}")
        except Exception as e:
            logging.error(f"Error saving video: {e}")
            return jsonify({"status": "error", "message": f"Error saving video: {str(e)}"})

        # Get video hash and check for duplicates
        hash_value = get_video_hash(video_path)
        if hash_value is None:
            try:
                os.remove(video_path)
            except:
                pass
            return jsonify({"status": "error", "message": "Error getting video hash."})
            
        if is_duplicate(hash_value):
            try:
                os.remove(video_path)
            except:
                pass
            return jsonify({"status": "duplicate", "message": "Duplicate video detected!", "coins": get_user_coins(user_id)})

        # Process video
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                try:
                    os.remove(video_path)
                except:
                    pass
                return jsonify({"status": "error", "message": "Error opening video file."})
                
            garbage_found = False
            frames_processed = 0
            max_frames = 100  # Limit processing to avoid timeouts

            while frames_processed < max_frames:
                success, img = cap.read()
                if not success:
                    break

                try:
                    results = model(img, stream=True)
                    
                    for r in results:
                        for box in r.boxes:
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            if conf > 0.1 and classNames[cls] in ['garbage', 'garbage_bag', 'trash']:
                                garbage_found = True
                                break
                        if garbage_found:
                            break
                except Exception as e:
                    logging.error(f"Error processing frame: {e}")
                    
                if garbage_found:
                    break
                    
                frames_processed += 1

            cap.release()
        except Exception as e:
            logging.error(f"Error during video processing: {e}")
            logging.error(traceback.format_exc())
            try:
                os.remove(video_path)
            except:
                pass
            return jsonify({"status": "error", "message": f"Error processing video: {str(e)}"})
        
        # Clean up after processing
        try:
            os.remove(video_path)
        except Exception as e:
            logging.warning(f"Could not remove video file: {e}")

        # Update user coins if garbage found
        if garbage_found:
            save_hash(hash_value)
            coins = update_user_coins(user_id)
            return jsonify({
                "status": "success", 
                "coins": coins, 
                "message": "Garbage detected. 5 coins added!"
            })
        else:
            return jsonify({
                "status": "no_garbage", 
                "coins": get_user_coins(user_id),
                "message": "No garbage detected. Try again."
            })
            
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        logging.error(traceback.format_exc())
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)