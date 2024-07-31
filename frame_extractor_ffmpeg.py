import ffmpeg
import os
import tkinter as tk
from tkinter import filedialog

def choose_video_file():
    """
    Opens a file dialog to allow the user to choose a video file.
    
    Returns:
        str: The path of the selected video file.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    video_path = filedialog.askopenfilename(title="Choose a video file", filetypes=[("AVI files", "*.avi")])
    return video_path

def choose_destination_folder():
    """
    Opens a file dialog to allow the user to choose a destination folder.
    
    Returns:
        str: The path of the selected destination folder.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Choose a destination folder")
    return folder_path

# Uncomment these lines to get user input for the video file and destination folder
video_file_path = choose_video_file()
dest_folder_path = choose_destination_folder()
num_frames = int(input("Enter the number of frames to extract: "))



def extract_frames(video_path, dest_folder, num_frames):
    """
    Extracts frames from a video file and saves them as individual images.
    
    Args:
        video_path (str): The path of the video file.
        dest_folder (str): The path of the destination folder to save the frames.
        num_frames (int): The number of frames to extract.
    """
    # Get video duration using ffmpeg
    probe = ffmpeg.probe(video_path)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    duration = float(video_info['duration'])
    fps = eval(video_info['r_frame_rate'])

    interval = duration / num_frames
    timestamps = [interval * i for i in range(num_frames)]

    for i, timestamp in enumerate(timestamps):
        output_filename = os.path.join(dest_folder, f"frame_{i+1:03d}.jpg")
        (
            ffmpeg
            .input(video_path, ss=timestamp)
            .output(output_filename, vframes=1)
            .run(quiet=True)
        )
        print(f"Extracted frame {i+1}/{num_frames} at {timestamp:.2f}s and saved to {output_filename}")

    print("Frame extraction completed.")

# Run the frame extraction
extract_frames(video_file_path, dest_folder_path, num_frames)