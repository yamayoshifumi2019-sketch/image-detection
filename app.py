"""
app.py - Main Application File

This is the main entry point for the Flask application.
It contains all routes and configuration.

To run the app:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2

# Import our database models
from models import db, User, Image

# =============================================================================
# APP CONFIGURATION
# =============================================================================

# Create Flask app instance
app = Flask(__name__)

# Secret key for session management and CSRF protection
# In production, use a random secret key stored in environment variables!
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Database configuration - using SQLite for simplicity
# The database file will be created in the same folder as app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warning

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Maximum file size (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize the database with the app
db.init_app(app)

# =============================================================================
# FLASK-LOGIN CONFIGURATION
# =============================================================================

# Create LoginManager instance
login_manager = LoginManager()
login_manager.init_app(app)

# Where to redirect when login is required
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback to load a user from the database.
    This is called on every request to get the current user.
    """
    return User.query.get(int(user_id))


# =============================================================================
# YOLO MODEL (loaded once at startup)
# =============================================================================

# Load the YOLOv8 nano model (smallest and fastest)
# This will download the model on first run (~6MB)
print("Loading YOLO model...")
yolo_model = YOLO('yolov8n.pt')
print("YOLO model loaded!")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    Returns True if the file extension is in ALLOWED_EXTENSIONS.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """
    Generate a unique filename to avoid conflicts.
    Uses UUID to create a random prefix.

    Example: "photo.jpg" -> "a1b2c3d4_photo.jpg"
    """
    # Get the file extension
    ext = original_filename.rsplit('.', 1)[1].lower()
    # Generate unique name
    unique_name = f"{uuid.uuid4().hex[:8]}_{secure_filename(original_filename)}"
    return unique_name


def run_object_detection(image_path, output_path):
    """
    Run YOLO object detection on an image.

    Args:
        image_path: Path to the input image
        output_path: Path to save the image with bounding boxes

    Returns:
        List of detected object names
    """
    # Read the image using OpenCV
    img = cv2.imread(image_path)

    # Run YOLO detection
    results = yolo_model(img)

    # Get the first result (we only have one image)
    result = results[0]

    # Get class names for detected objects
    detected_objects = []
    for box in result.boxes:
        # Get class ID and convert to class name
        class_id = int(box.cls[0])
        class_name = yolo_model.names[class_id]
        detected_objects.append(class_name)

    # Draw bounding boxes on the image
    # result.plot() returns the image with boxes drawn
    annotated_img = result.plot()

    # Save the annotated image
    cv2.imwrite(output_path, annotated_img)

    return detected_objects


# =============================================================================
# ROUTES - HOME PAGE
# =============================================================================

@app.route('/')
def index():
    """
    Home page route.
    Shows welcome message and navigation.
    """
    return render_template('index.html')


# =============================================================================
# ROUTES - AUTHENTICATION (SIGNUP, LOGIN, LOGOUT)
# =============================================================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User registration page.

    GET: Show the signup form
    POST: Process the signup form and create new user
    """
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('signup.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('signup.html')

        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return render_template('signup.html')

        # Create new user with hashed password
        # generate_password_hash uses pbkdf2:sha256 by default (secure!)
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)

        # Save to database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    # GET request - show the form
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page.

    GET: Show the login form
    POST: Process login and create session
    """
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Find user in database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password_hash, password):
            # Log the user in (creates session)
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')

            # Redirect to the page user was trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    Log out the current user.
    Requires user to be logged in.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# =============================================================================
# ROUTES - IMAGE UPLOAD AND DETECTION
# =============================================================================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Image upload page.

    GET: Show the upload form
    POST: Process uploaded image and run object detection
    """
    if request.method == 'POST':
        # Check if file was uploaded
        if 'image' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload.html')

        file = request.files['image']

        # Check if user selected a file
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload.html')

        # Check if file type is allowed
        if not allowed_file(file.filename):
            flash('File type not allowed. Please upload an image (png, jpg, jpeg, gif, bmp).', 'error')
            return render_template('upload.html')

        # Generate unique filename
        original_filename = file.filename
        stored_filename = generate_unique_filename(original_filename)
        detected_filename = 'detected_' + stored_filename

        # Save paths
        stored_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
        detected_path = os.path.join(app.config['UPLOAD_FOLDER'], detected_filename)

        # Save the uploaded file
        file.save(stored_path)

        # Run object detection
        try:
            detected_objects = run_object_detection(stored_path, detected_path)
            detection_results = ', '.join(detected_objects) if detected_objects else 'No objects detected'
        except Exception as e:
            # If detection fails, delete the uploaded file and show error
            os.remove(stored_path)
            flash(f'Error during object detection: {str(e)}', 'error')
            return render_template('upload.html')

        # Save image info to database
        new_image = Image(
            original_filename=original_filename,
            stored_filename=stored_filename,
            detected_filename=detected_filename,
            detection_results=detection_results,
            user_id=current_user.id
        )
        db.session.add(new_image)
        db.session.commit()

        flash(f'Image uploaded successfully! Detected: {detection_results}', 'success')
        return redirect(url_for('images'))

    return render_template('upload.html')


# =============================================================================
# ROUTES - IMAGE LIST AND DELETE
# =============================================================================

@app.route('/images')
@login_required
def images():
    """
    Display list of images uploaded by the current user.
    Images are ordered by upload date (newest first).
    """
    # Get all images for the current user
    user_images = Image.query.filter_by(user_id=current_user.id)\
                             .order_by(Image.uploaded_at.desc())\
                             .all()
    return render_template('images.html', images=user_images)


@app.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    """
    Delete an image.
    Only the owner can delete their own images.
    """
    # Find the image
    image = Image.query.get_or_404(image_id)

    # Check if current user is the owner
    if image.user_id != current_user.id:
        flash('You can only delete your own images.', 'error')
        return redirect(url_for('images'))

    # Delete the files from disk
    stored_path = os.path.join(app.config['UPLOAD_FOLDER'], image.stored_filename)
    detected_path = os.path.join(app.config['UPLOAD_FOLDER'], image.detected_filename)

    try:
        if os.path.exists(stored_path):
            os.remove(stored_path)
        if os.path.exists(detected_path):
            os.remove(detected_path)
    except Exception as e:
        flash(f'Error deleting files: {str(e)}', 'error')

    # Delete from database
    db.session.delete(image)
    db.session.commit()

    flash('Image deleted successfully.', 'success')
    return redirect(url_for('images'))


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 error page.
    Shown when a page is not found.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    Custom 500 error page.
    Shown when there's a server error.
    """
    return render_template('500.html'), 500


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created!")

    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Run the Flask development server
    # debug=True enables auto-reload and detailed error pages
    print("Starting Flask server...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
