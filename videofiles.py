import cv2
import os

# Base directory containing the annotated frame folders
base_dir = "E:/SIH24/"

# List of annotated frame folders
folders = ["Annotated_Frames_sb1", "Annotated_Frames_sb2", "Annotated_Frames_sb3", "Annotated_Frames_sb4", "Annotated_Frames_sb5"]

# Directory to save the final output videos
output_video_dir = "E:/SIH24/SmartIndiaHackathonProject/static"
os.makedirs(output_video_dir, exist_ok=True)

# Process each folder
for folder in folders:
    frames_dir = os.path.join(base_dir, folder)
    
    # Get list of all frame files
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
    
    # Check if there are frames in the folder
    if not frame_files:
        print(f"No frames found in {frames_dir}. Skipping...")
        continue
    
    # Get the frame dimensions from the first frame
    first_frame_path = os.path.join(frames_dir, frame_files[0])
    first_frame = cv2.imread(first_frame_path)
    height, width, _ = first_frame.shape
    
    # Create a VideoWriter object
    output_video_path = os.path.join(output_video_dir, f"{folder}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for .mp4 files
    fps = 30  # Set the frames per second (adjust as needed)
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    # Write frames to the video file
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv2.imread(frame_path)
        out.write(frame)
    
    # Release the VideoWriter object
    out.release()

    print(f"Video for {folder} created at {output_video_path}")

print("All videos have been processed.")
