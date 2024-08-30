import cv2
import torch
import os
import gdown

# Download training images
training_images_url = 'https://drive.google.com/uc?id=1WUvvWlG56rLtTaKI1Tyvj_AJth-xKOOU'
output_folder = 'training_images'
gdown.download_folder(training_images_url, output_folder, quiet=False)

# Download training video
video_url = 'https://drive.google.com/uc?id=1wbKB6V469MgB-1DF_uH9yFvKulYVb5CU'
video_output_path = 'training_video.avi'
gdown.download(video_url, video_output_path, quiet=False)

# Download annotated images
annotated_images_url = 'https://drive.google.com/uc?id=1i6qvNER-zmWtCh4JkENn47zTI-f5epl7'
annotated_output_folder = 'annotated_images'
gdown.download_folder(annotated_images_url, annotated_output_folder, quiet=False)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # 'yolov5s' is the small version, suitable for faster processing

# Define vehicle classes to filter
vehicle_classes = ['car', 'bus', 'motorbike', 'truck']

# Process each image
for img_name in os.listdir(output_folder):
    img_path = os.path.join(output_folder, img_name)

    # Load the image
    image = cv2.imread(img_path)

    # Convert the image from BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize the image to the desired size
    image_resized = cv2.resize(image_rgb, (640, 640))

    # Normalize the image
    image_normalized = image_resized / 255.0

    # Perform inference on the image
    results = model(image_resized)

    # Extract the detections
    detections = results.pandas().xyxy[0]  # Results in a Pandas DataFrame

    # Draw bounding boxes for vehicles
    for _, detection in detections.iterrows():
        if detection['name'] in vehicle_classes:
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            cv2.rectangle(image_resized, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Save or display the processed image
    processed_img_path = os.path.join('processed_images', img_name)
    os.makedirs('processed_images', exist_ok=True)
    cv2.imwrite(processed_img_path, cv2.cvtColor(image_resized, cv2.COLOR_RGB2BGR))
    cv2.imshow('Processed Image', image_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Process video
cap = cv2.VideoCapture(video_output_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Directory to save annotated frames
os.makedirs(annotated_output_folder, exist_ok=True)

# Initialize total vehicle count
total_vehicle_count = 0

# Frame counter for saving frames
frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (640, 640))

    results = model(frame_resized)
    detections = results.pandas().xyxy[0]

    vehicle_count = 0
    for _, detection in detections.iterrows():
        if detection['name'] in vehicle_classes:
            vehicle_count += 1
            total_vehicle_count += 1
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = detection['name']
            confidence = detection['confidence']
            label_text = f'{label} {confidence:.2f}'
            cv2.putText(frame_resized, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.putText(frame_resized, f'Vehicle Count: {vehicle_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    frame_filename = os.path.join(annotated_output_folder, f"frame_{frame_counter:05d}.jpg")
    cv2.imwrite(frame_filename, cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR))

    cv2.imshow('Detected Vehicles', frame_resized)
    frame_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(f'Total number of vehicles detected: {total_vehicle_count}')

cap.release()
cv2.destroyAllWindows()

# Stitch images to video
def stitch_images_to_video(image_paths, output_path, fps=20, frame_size=(640, 640)):
    if not image_paths:
        print("Error: No images to stitch.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}. Skipping...")
            continue

        if (image.shape[1], image.shape[0]) != frame_size:
            image = cv2.resize(image, frame_size)

        video_writer.write(image)

    video_writer.release()
    print(f"Video saved as {output_path}")

image_paths = [os.path.join(annotated_output_folder, img) for img in os.listdir(annotated_output_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
image_paths.sort()

output_video_path = 'output_video.mp4'
frame_size = (640, 640)
fps = 20

stitch_images_to_video(image_paths, output_video_path, fps=fps, frame_size=frame_size)
