import pandas as pd
import os
from datetime import datetime, timedelta
from pydub import AudioSegment
import pygame
import tkinter as tk
from tkinter import messagebox

# Initialize Pygame mixer
pygame.mixer.init()

def find_audio_file(directory, timestamp):
    """
    Find an audio file in the specified directory that matches the given timestamp.

    Args:
        directory (str): The directory to search for audio files.
        timestamp (datetime): The timestamp to match against the audio file names.

    Returns:
        str or None: The path of the matching audio file, or None if no match is found.
    """
    date_str = timestamp.strftime('%Y%m%d-%H%M%S')
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(date_str[:8]):  # Match YYYYMMDD
                if file.endswith('.wav'):
                    file_time = datetime.strptime(file[:-4], '%Y%m%d-%H%M%S')
                    if file_time <= timestamp < file_time + timedelta(minutes=5):
                        return os.path.join(root, file)
    return None

def play_audio_from_time(file_path, start_time):
    """
    Play a segment of audio from a given start time.

    Args:
        file_path (str): The path to the audio file.
        start_time (float): The start time in seconds.

    Returns:
        None
    """
    audio = AudioSegment.from_wav(file_path)
    start_time_ms = start_time * 1000
    window_length = 3 * 1000  # 3 seconds window
    start_index = max(start_time_ms - window_length / 2, 0)
    end_index = min(start_time_ms + window_length / 2, len(audio))
    window = audio[int(start_index):int(end_index)]
    
    # Create a directory for audio excerpts
    output_dir = os.path.join(os.getcwd(), "audio_excerpts")
    os.makedirs(output_dir, exist_ok=True)
    
    # Export the audio excerpt to the directory
    excerpt_path = os.path.join(output_dir, f"excerpt_{start_time}.wav")
    window.export(excerpt_path, format="wav")
    
    # Load and play the audio using Pygame
    pygame.mixer.music.load(excerpt_path)
    pygame.mixer.music.play()

def stop_audio():
    """
    Stops the currently playing audio and unloads it from the mixer.

    This function stops the audio playback using `pygame.mixer.music.stop()`
    and unloads the audio from the mixer using `pygame.mixer.music.unload()`.
    """
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()


class AudioClassifierApp:
    def __init__(self, root, csv_path, audio_directory):
        self.root = root
        self.csv_path = csv_path
        self.audio_directory = audio_directory
        self.current_index = 0
        self.labels = []
        self.history = []

        # Load the CSV file
        self.df = pd.read_csv(csv_path, delimiter=',', on_bad_lines='skip')
        if self.df.empty or 'Date' not in self.df.columns:
            messagebox.showerror("Error", "CSV file is empty or missing required column 'Date'.")
            root.destroy()
            return

        # Add manual labels column if it doesn't exist
        if 'Manual Labels' not in self.df.columns:
            self.df['Manual Labels'] = None

        # Setup the GUI
        self.setup_gui()

        # Load the first audio file
        self.load_audio()

    def setup_gui(self):
        self.root.title("Audio Classifier")

        # Display audio file info
        self.audio_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.audio_label.pack(pady=10)

        # Buttons for classification
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        # Buttons on the left
        left_btn_frame = tk.Frame(btn_frame)
        left_btn_frame.grid(row=0, column=0)

        self.btn_false_alarm = tk.Button(left_btn_frame, text="False Alarm", command=lambda: self.classify_audio("False Alarm"), width=10, height=2, bg="red")
        self.btn_false_alarm.grid(row=0, column=0, padx=5)

        self.btn_noise = tk.Button(left_btn_frame, text="Noise", command=lambda: self.classify_audio("Noise"), width=10, height=2, bg="red")
        self.btn_noise.grid(row=0, column=1, padx=5)

        self.btn_grunt = tk.Button(left_btn_frame, text="Grunt", command=lambda: self.classify_audio("Grunt"), width=10, height=2, bg="yellow")
        self.btn_grunt.grid(row=1, column=0, padx=5)

        self.btn_cough = tk.Button(left_btn_frame, text="Cough", command=lambda: self.classify_audio("Cough"), width=10, height=2, bg="yellow")
        self.btn_cough.grid(row=1, column=1, padx=5)

        self.btn_vocalization = tk.Button(left_btn_frame, text="Vocalization", command=lambda: self.classify_audio("Vocalization"), width=10, height=2, bg="green")
        self.btn_vocalization.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons on the right
        right_btn_frame = tk.Frame(btn_frame)
        right_btn_frame.grid(row=0, column=1)

        self.btn_replay = tk.Button(right_btn_frame, text="Replay", command=self.replay_audio, width=10, height=2)
        self.btn_replay.grid(row=0, column=0, padx=5)

        self.btn_undo = tk.Button(right_btn_frame, text="Undo", command=self.undo_last_label, width=10, height=2)
        self.btn_undo.grid(row=0, column=1, padx=5)

        self.btn_save = tk.Button(right_btn_frame, text="Save", command=self.save_labels, width=10, height=2)
        self.btn_save.grid(row=0, column=2, padx=5)


    def load_audio(self):
        if self.current_index < len(self.df):
            row = self.df.iloc[self.current_index]
            try:
                timestamp = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S')
                self.audio_file = find_audio_file(self.audio_directory, timestamp)
                if self.audio_file:
                    file_start_time = datetime.strptime(os.path.basename(self.audio_file)[:-4], '%Y%m%d-%H%M%S')
                    self.start_time_seconds = (timestamp - file_start_time).total_seconds()
                    self.audio_label.config(text=f"Playing: {self.audio_file}\nTimestamp: {timestamp}")
                    play_audio_from_time(self.audio_file, self.start_time_seconds)
                else:
                    self.audio_label.config(text=f"No audio file found for timestamp {timestamp}")
                    self.current_index += 1
                    self.load_audio()
            except ValueError as e:
                self.audio_label.config(text=f"Error parsing date in row {self.current_index}: {e}")
                self.current_index += 1
                self.load_audio()
        else:
            messagebox.showinfo("Info", "No more audio files to classify.")
            self.root.destroy()

    def classify_audio(self, label):
        self.labels.append((self.current_index, label))
        self.df.at[self.current_index, 'Manual Labels'] = label
        self.history.append(self.current_index)
        self.current_index += 1
        stop_audio()
        self.load_audio()

    def replay_audio(self):
        if self.audio_file:
            stop_audio()
            play_audio_from_time(self.audio_file, self.start_time_seconds)

    def undo_last_label(self):
        if self.history:
            last_index = self.history.pop()
            self.df.at[last_index, 'Manual Labels'] = None
            self.labels = [lbl for lbl in self.labels if lbl[0] != last_index]
            self.current_index = last_index
            stop_audio()
            self.load_audio()
        else:
            messagebox.showwarning("Warning", "No previous label to undo.")

    def save_labels(self):
        try:
            self.df.to_csv(self.csv_path, index=False)
            messagebox.showinfo("Info", "Labels saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save labels: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioClassifierApp(root, r"C:\Users\bergamascot\Documents\Progetti\Audio_Suini_SOMO\Esperimento4\data_array.csv", r"C:\Users\bergamascot\Documents\Progetti\Audio_Suini_SOMO\Esperimento4\output_folder")
    root.mainloop()
