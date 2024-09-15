import cv2
import os

# Base directory containing the annotated frame folders
base_dir = "E:/SIH24/"

# List of annotated frame folders
folders = ["Annotated_Frames_sb1", "Annotated_Frames_sb2", "Annotated_Frames_sb3", 
           "Annotated_Frames_sb4", "Annotated_Frames_sb5"]

# Directory to save the final output videos
output_video_dir = "E:/SIH24/SmartIndiaHackathonProject/static"
os.makedirs(output_video_dir, exist_ok=True)  # Ensure the output directory exists

# Process each folder
for folder in folders:
    frames_dir = os.path.join(base_dir, folder)
    
    # Get list of all frame files in sorted order (important for frame sequence)
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
    
    # Check if there are frames in the folder
    if not frame_files:
        print(f"No frames found in {frames_dir}. Skipping...")
        continue
    
    # Load the first frame to get its dimensions
    first_frame_path = os.path.join(frames_dir, frame_files[0])
    first_frame = cv2.imread(first_frame_path)
    
    if first_frame is None:
        print(f"Error reading the first frame from {first_frame_path}. Skipping...")
        continue
    
    height, width, _ = first_frame.shape
    
    # Create the output video file path
    output_video_path = os.path.join(output_video_dir, f"{folder}.mp4")
    
    # Create a VideoWriter object for saving the video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 video
    fps = 30  # Set the frames per second, can adjust as necessary
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    # Write each frame into the video
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv2.imread(frame_path)
        
        # Check if frame is read correctly
        if frame is None:
            print(f"Error reading {frame_path}. Skipping this frame...")
            continue
        
        out.write(frame)  # Write frame to the video
    
    # Release the VideoWriter object to save the video
    out.release()
    
    print(f"Video for {folder} created at {output_video_path}")

print("All videos have been processed.")
