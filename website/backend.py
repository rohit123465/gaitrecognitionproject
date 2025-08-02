from flask import Flask, request, jsonify, send_file, send_from_directory, redirect, url_for, session, current_app
from pyngrok import ngrok
from flask_socketio import SocketIO, emit
from flask_ngrok import run_with_ngrok
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, Column, Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess
import threading
import io
import json
from animations import save_smpl_animation
from main import results 
from gait_database import human_identification


# Set up Flask
app = Flask(__name__, static_folder='/content/drive/MyDrive/4D-Humans/website')
app.secret_key = "$3cR3T_K3Y"
socketio = SocketIO(app, cors_allowed_origins="*")  

ALLOWED_EXTENSIONS = {"mp4"}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "loginpage"  

# Define SQLAlchemy ORM Base and Database
Base = declarative_base()
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    user = session.query(User).get(int(user_id))
    session.close()
    return user

# Define the User table
class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


    # Relationship to Videos table
    videos = relationship("Video", back_populates="user")

# Define the Video table
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    video = Column(LargeBinary, nullable=False)
    mesh = Column(LargeBinary, nullable=True)
    animate = Column(LargeBinary, nullable=True)

    # Relationship to User table
    user = relationship("User", back_populates="videos")



# Create the tables in the database
Base.metadata.create_all(engine)

TRACK_SCRIPT_PATH = "/content/drive/MyDrive/4D-Humans/track.py"

# Route to serve the registration HTML page
@app.route("/")
def home():
    return send_file("/content/drive/MyDrive/4D-Humans/website/register.html")

# Route to serve static files (Video frames)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Route to handle the registration form submission
@app.route("/register", methods=["POST"])
def register():
    # Get data from the form
    name = request.json.get('name')
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if not name or not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400
    
    # Check if the username or email already exists
    session = SessionLocal()
    existing_user = session.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "Username or Email already exists"}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Create a new user object
    new_user = User(name=name, username=username, email=email, password=hashed_password)
    session.add(new_user)
    session.commit()
    session.close()

    # Return a response with a success message and login page URL
    return jsonify({
        "message": "User registered successfully",
        "redirect_url": "/loginpage"  # URL for the login page
    }), 201


# Route to serve the login page
@app.route("/loginpage")
def loginpage():
    return send_file("/content/drive/MyDrive/4D-Humans/website/login.html")

@app.route("/login", methods=["POST"])
def login():
    # Get data from the form
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({"message": "Both username and password are required."}), 400

    # Retrieve user from the database
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    if user is None:
        return jsonify({"message": "User not found. Please check your username."}), 400

    # Check if the password is correct
    if check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful", "redirect_url": "/home"}), 200
    else:
        return jsonify({"message": "Incorrect password. Please try again."}), 400

# Home route for after login
@app.route("/home")
def homepage():
    return send_file("/content/drive/MyDrive/4D-Humans/website/home_page.html")

@app.route("/upload")
def uploadpage():
    return send_file("/content/drive/MyDrive/4D-Humans/website/upload.html")

@app.route("/visualizations")
def visualizationpage():
    return send_file("/content/drive/MyDrive/4D-Humans/website/visualization.html")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


from flask_login import current_user
# Route to handle video upload
@app.route("/upload", methods=["POST"])
@login_required

def upload_video():
    if "video" not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files["video"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Invalid file format. Only MP4 allowed."}), 400

    # Read the file in binary mode
    video_binary = file.read()

    # Get the user ID from the logged-in user
    user_id = current_user.id

    # Store the binary data in the database
    session = SessionLocal()
    new_video = Video(user_id=user_id, video=video_binary)
    session.add(new_video)
    session.commit()

    vid_id = new_video.id

    session.close()

    
    def background_task(vid_id):
        run_hmr2_model(vid_id)  

    
    thread = threading.Thread(target=background_task, args=(vid_id,))
    thread.daemon = True 
    thread.start()
    
    return jsonify({"message": "Video uploaded successfully. Analysis is running in the background."}), 201



# Route to retrieve uploaded videos
def retrieve_video_from_db(video_id, output_filename):
    session = SessionLocal()
    video = session.query(Video).filter(Video.id == video_id).first()
    if video:
        # Convert the binary video data back to a file
        video_stream = io.BytesIO(video.video) 
        video_stream.seek(0) 
        
        # Create a file to write the binary data into
        with open(output_filename, 'wb') as f:
            f.write(video_stream.read()) 

        session.close()
        return output_filename  # Return the path to the saved video file
    else:
        session.close()
        raise ValueError("Video not found in the database")

def save_video_to_file(video_data, file_path):
    """Save the retrieved binary video data to a temporary file."""
    with open(file_path, 'wb') as f:
        f.write(video_data)
    

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("loginpage"))

def clear_json():
    json_file_path = "/content/drive/MyDrive/4D-Humans/website/output/walking_man.json"
    try:
        with open(json_file_path, 'w') as json_file:
            json_file.truncate(0)  # Overwrite with an empty object
        print(f"Cleared JSON file: {json_file_path}")
    except Exception as e:
        print(f"Error clearing JSON file: {e}")

def clear_preprocessed_json():
  json_file_path = "/content/drive/MyDrive/4D-Humans/website/output/walking_man_preprocessed.json"
  try:
        with open(json_file_path, 'w') as json_file:
            json_file.truncate(0)  
        print(f"Cleared JSON file: {json_file_path}")
  except Exception as e:
        print(f"Error clearing JSON file: {e}")

def preprocessdata():
    json_path='/content/drive/MyDrive/4D-Humans/website/output/walking_man.json'
    if os.path.exists(json_path) and os.stat(json_path).st_size > 0:
        with open(json_path, "r") as file:
            data = json.load(file)
    else:
        print("Error: JSON file is empty or missing!")
        return None

    # Iterate over the frames and modify the 'joints' key
    for frame in data:
        joints = frame.get('joints')
        vertices= frame.get('vertices')
        betas= frame.get('betas')
        body_pose= frame.get('body_pose')
        global_orient= frame.get('global_orient')

        frame['joints']=joints[0]
        frame['vertices']=vertices[0]
        frame['betas']
        frame['body_pose']=body_pose[0][0]
        frame['global_orient']=global_orient[0][0]
        del frame['camera_translation']

    data2 = {
        "frames": data
    }

    clear_preprocessed_json()

    # Save the modified data back to a JSON file
    with open('/content/drive/MyDrive/4D-Humans/website/output/walking_man_preprocessed.json', 'w') as file:
        json.dump(data2, file, indent=4)

    print("JSON file modified successfully.")




mesh_path = '/content/drive/MyDrive/4D-Humans/outputs'

@app.route('/mesh_processor')
def run_hmr2_model(video_id):

    json_file_path = "/content/drive/MyDrive/4D-Humans/website/output/walking_man.json"
    json_file_preprocessed_path="/content/drive/MyDrive/4D-Humans/website/output/walking_man_preprocessed.json"
    try:
        clear_json()

        # Data is saved to a temporary file
        temp_video_path = '/temp_video.mp4' 
        video_data = retrieve_video_from_db(video_id, temp_video_path)

        # Call the track method of the HMR 2.0 mesh recovery model
        command = ['python', '/content/drive/MyDrive/4D-Humans/track.py', f'video.source={temp_video_path}']
        subprocess.run(command, check=True)  # Run the track function through a subprocess
        print("Tracking completed successfully.")

        result_file_path = os.path.join(mesh_path, f"PHALP_temp_video.mp4")  # Result file path
        animation_output_path = '/content/drive/MyDrive/4D-Humans/website/outputs/walkingman_animation.mp4'
        if os.path.exists(result_file_path):
            print(f"Results saved at: {result_file_path}")
            
            session = SessionLocal()
            existing_video = session.query(Video).filter(Video.id == video_id).first()

            mesh_binary = None
            with open(result_file_path, 'rb') as video_file:
              mesh_binary = video_file.read()

            existing_video.mesh = mesh_binary
            session.commit()
            session.close()

            preprocessdata()

            return True
        else:
            raise FileNotFoundError("Tracking results file not found.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        preprocessdata() 
        save_smpl_animation(json_file_preprocessed_path,animation_output_path , sigma=1.0)
        results()
        get_identification_results()
        
    return False  

@app.route('/get_identification_results', methods=['GET'])
def get_identification_results():
    print("Endpoint detected")
    with current_app.app_context():  
      result = human_identification()
      return jsonify({"identification": result})




# Start Flask server on port 5000
ngrok_tunnel = ngrok.connect(5000)
print(f"Public URL: {ngrok_tunnel.public_url}")

app.run(port=5000)