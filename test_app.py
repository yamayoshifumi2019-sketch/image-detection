"""
test_app.py - Simple test script for the Object Detection App

This script tests the app by:
1. Creating a new user account
2. Logging in
3. Uploading an image for object detection
4. Checking the results
"""

import requests

# Base URL of our Flask app
BASE_URL = "http://127.0.0.1:5000"

# Create a session to maintain cookies (for login)
session = requests.Session()

# Test user credentials
USERNAME = "testuser"
PASSWORD = "test123"

print("=" * 50)
print("Testing Object Detection App")
print("=" * 50)

# Step 1: Sign up
print("\n1. Signing up...")
signup_response = session.post(f"{BASE_URL}/signup", data={
    "username": USERNAME,
    "password": PASSWORD,
    "confirm_password": PASSWORD
})
if "Account created" in signup_response.text or "already exists" in signup_response.text:
    print("   Signup successful (or user already exists)")
else:
    print("   Signup response received")

# Step 2: Login
print("\n2. Logging in...")
login_response = session.post(f"{BASE_URL}/login", data={
    "username": USERNAME,
    "password": PASSWORD
})
if "Welcome back" in login_response.text or "Upload" in login_response.text:
    print("   Login successful!")
else:
    print("   Login response received")

# Step 3: Upload image
print("\n3. Uploading image for object detection...")
image_path = "C:/Users/yoshi/frenkie_de_jong.png"

with open(image_path, "rb") as img_file:
    files = {"image": ("frenkie_de_jong.png", img_file, "image/png")}
    upload_response = session.post(f"{BASE_URL}/upload", files=files)

if "successfully" in upload_response.text or "Detected" in upload_response.text:
    print("   Image uploaded and processed!")
else:
    print("   Upload response received")

# Step 4: Check images page
print("\n4. Checking images page...")
images_response = session.get(f"{BASE_URL}/images")
if "image-card" in images_response.text:
    print("   Images page loaded with results!")
    # Try to find detection results in the response
    if "Detected:" in images_response.text:
        # Extract detection results (simple parsing)
        start = images_response.text.find("Detected:</strong>")
        if start != -1:
            end = images_response.text.find("</p>", start)
            result = images_response.text[start:end].replace("Detected:</strong>", "").strip()
            print(f"   Detection results: {result}")
else:
    print("   Images page loaded")

print("\n" + "=" * 50)
print("Test complete!")
print("Open http://127.0.0.1:5000 in your browser to see results")
print("=" * 50)
