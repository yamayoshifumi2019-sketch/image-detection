"""
detect.py - Simple Local Object Detection App

A simple single-file object detection app using YOLOv8.
Run it and a file picker will open to choose your image.

Requirements:
    pip install ultralytics opencv-python

Usage:
    python detect.py              # Opens file picker to choose image
    python detect.py image.jpg    # Use specific image file

Controls:
    Press any key to close the result window

Author: Yoshifumi
"""

import sys
import cv2
from ultralytics import YOLO
from tkinter import Tk, filedialog

# Hide the main tkinter window
Tk().withdraw()


def select_image():
    """Open a file picker dialog to select an image."""
    print("Opening file picker...")
    file_path = filedialog.askopenfilename(
        title="Select an image for object detection",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*")
        ]
    )
    return file_path


def detect_image(image_path):
    """Run object detection on an image."""
    print(f"\nProcessing: {image_path}")

    # Load YOLO model
    print("Loading YOLO model...")
    model = YOLO('yolov8n.pt')
    print("Model loaded!")

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image: {image_path}")
        return

    # Run detection
    results = model(img)

    # Print results
    print("\n" + "=" * 40)
    print("  Detection Results")
    print("=" * 40)

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        name = model.names[class_id]
        print(f"  - {name}: {confidence:.1%}")

    if len(results[0].boxes) == 0:
        print("  No objects detected")

    print("=" * 40)

    # Draw bounding boxes
    annotated = results[0].plot()

    # Save result
    output_path = 'detected_result.jpg'
    cv2.imwrite(output_path, annotated)
    print(f"\nResult saved: {output_path}")

    # Show result window
    cv2.imshow('Detection Result - Press any key to close', annotated)
    print("Press any key to close the window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    print("=" * 40)
    print("  Object Detection App")
    print("  Using YOLOv8")
    print("=" * 40)

    if len(sys.argv) > 1:
        # Image path provided as argument
        image_path = sys.argv[1]
    else:
        # Open file picker
        image_path = select_image()

    if image_path:
        detect_image(image_path)
    else:
        print("No image selected. Exiting.")


if __name__ == '__main__':
    main()
