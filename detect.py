"""
detect.py - Simple Local Object Detection App

A simple single-file object detection app using YOLOv8.
Opens your webcam or an image file and detects objects.

Requirements:
    pip install ultralytics opencv-python

Usage:
    python detect.py              # Use webcam
    python detect.py image.jpg    # Use image file
    python detect.py video.mp4    # Use video file

Controls (webcam/video mode):
    q - Quit
    s - Save screenshot

Author: Yoshifumi
"""

import sys
import cv2
from ultralytics import YOLO

# Load YOLOv8 model (downloads automatically on first run)
print("Loading YOLO model...")
model = YOLO('yolov8n.pt')  # nano model (fast, ~6MB)
print("Model loaded!")


def detect_from_webcam():
    """Run object detection on webcam feed."""
    print("\nStarting webcam...")
    print("Press 'q' to quit, 's' to save screenshot")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection
        results = model(frame, verbose=False)

        # Draw bounding boxes
        annotated = results[0].plot()

        # Show detected objects in console
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            name = model.names[class_id]
            print(f"  Detected: {name} ({confidence:.2%})")

        # Display
        cv2.imshow('Object Detection (Press q to quit)', annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('screenshot.jpg', annotated)
            print("Screenshot saved!")

    cap.release()
    cv2.destroyAllWindows()


def detect_from_image(image_path):
    """Run object detection on a single image."""
    print(f"\nProcessing image: {image_path}")

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image: {image_path}")
        return

    # Run detection
    results = model(img)

    # Print results
    print("\n=== Detection Results ===")
    detected = []
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        name = model.names[class_id]
        detected.append(f"{name} ({confidence:.2%})")
        print(f"  - {name}: {confidence:.2%}")

    if not detected:
        print("  No objects detected")

    # Draw and save result
    annotated = results[0].plot()
    output_path = 'detected_' + image_path.split('/')[-1].split('\\')[-1]
    cv2.imwrite(output_path, annotated)
    print(f"\nResult saved: {output_path}")

    # Show image
    cv2.imshow('Detection Result (Press any key to close)', annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detect_from_video(video_path):
    """Run object detection on a video file."""
    print(f"\nProcessing video: {video_path}")
    print("Press 'q' to quit")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection
        results = model(frame, verbose=False)
        annotated = results[0].plot()

        cv2.imshow('Video Detection (Press q to quit)', annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function."""
    print("=" * 50)
    print("  Simple Object Detection App")
    print("  Using YOLOv8 (80 object classes)")
    print("=" * 50)

    if len(sys.argv) > 1:
        # File provided as argument
        file_path = sys.argv[1]

        # Check if image or video
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            detect_from_image(file_path)
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            detect_from_video(file_path)
        else:
            print(f"Unknown file type: {file_path}")
    else:
        # No file - use webcam
        detect_from_webcam()


if __name__ == '__main__':
    main()
