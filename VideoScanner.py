"""
README - Video Scanner App using Tkinter & OpenCV

This project is a desktop GUI application built using Tkinter, OpenCV, and Pillow
to scan videos, draw custom scanlines, navigate through frames, and export processed
frames. It is useful for video analysis, frame inspection, and technical visualization.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import os
from PIL import Image, ImageTk
import numpy as np

class VideoScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Scanner Project")
        self.root.geometry("1000x700")
        
        self.video_path = ""
        self.first_frame = None
        self.x_lines = []
        self.y_lines = []
        self.custom_lines = []
        self.output_dir = "output"
        self.current_frame_index = 0
        self.cap = None
        self.playing = False
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.setup_ui()
    
    def setup_ui(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)
        
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(pady=10)
        
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10)
        
        self.load_btn = tk.Button(self.top_frame, text="Load Video", command=self.load_video)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.process_btn = tk.Button(self.top_frame, text="Process Video", command=self.process_video)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.show_index_btn = tk.Button(self.top_frame, text="Show Index", command=self.show_index)
        self.show_index_btn.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.middle_frame, width=640, height=480, bg="gray")
        self.canvas.pack(side=tk.LEFT)
        
        self.control_panel = tk.Frame(self.middle_frame, width=300, height=480)
        self.control_panel.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.control_panel, text="X Scanlines:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.x_frame = tk.Frame(self.control_panel)
        self.x_frame.pack(fill=tk.X, pady=5)
        
        self.x_entries = []
        for i in range(3):
            row = tk.Frame(self.x_frame)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"Line {i+1}:").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            self.x_entries.append(entry)
        
        tk.Label(self.control_panel, text="Y Scanlines:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.y_frame = tk.Frame(self.control_panel)
        self.y_frame.pack(fill=tk.X, pady=5)
        
        self.y_entries = []
        for i in range(3):
            row = tk.Frame(self.y_frame)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"Line {i+1}:").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            self.y_entries.append(entry)
        
        tk.Label(self.control_panel, text="Custom Lines:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.custom_line_btn = tk.Button(self.control_panel, text="Add Custom Line", command=self.add_custom_line)
        self.custom_line_btn.pack(pady=5)
        
        self.play_btn = tk.Button(self.bottom_frame, text="Play", command=self.play_video)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(self.bottom_frame, text="Pause", command=self.pause_video)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(self.bottom_frame, text="Stop", command=self.stop_video)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = tk.Button(self.bottom_frame, text="<< Prev", command=self.prev_frame)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(self.bottom_frame, text="Next >>", command=self.next_frame)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            ret, frame = self.cap.read()
            
            if ret:
                self.first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_frame(self.first_frame)
                self.status_var.set(f"Loaded: {os.path.basename(self.video_path)}")
            else:
                messagebox.showerror("Error", "Could not read video file")
                self.cap.release()
    
    def display_frame(self, frame):
        frame = self.resize_with_aspect_ratio(frame, width=640)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)
        self.canvas.config(width=img.width, height=img.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk
    
    def resize_with_aspect_ratio(self, image, width=None, height=None):
        (h, w) = image.shape[:2]
        
        if width is None and height is None:
            return image
        
        if width is not None:
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            r = height / float(h)
            dim = (int(w * r), height)
            
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    
    def get_scanlines(self):
        self.x_lines = []
        self.y_lines = []
        
        for entry in self.x_entries:
            if entry.get():
                try:
                    x = int(entry.get())
                    if 0 <= x <= 1000:
                        self.x_lines.append(x)
                except ValueError:
                    pass
        
        for entry in self.y_entries:
            if entry.get():
                try:
                    y = int(entry.get())
                    if 0 <= y <= 1000:
                        self.y_lines.append(y)
                except ValueError:
                    pass
    
    def add_custom_line(self):
        messagebox.showinfo("Info", "Custom line drawing can be added here.")
    
    def process_video(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please load a video first")
            return
        
        self.get_scanlines()
        
        if not self.x_lines and not self.y_lines:
            messagebox.showwarning("Warning", "No scanlines defined")
            return
        
        cap = cv2.VideoCapture(self.video_path)
        frame_count = 0
        
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_with_lines = frame.copy()
            
            for x in self.x_lines:
                cv2.line(frame_with_lines, (x, 0), (x, frame.shape[0]), (0, 255, 0), 2)
            
            for y in self.y_lines:
                cv2.line(frame_with_lines, (0, y), (frame.shape[1], y), (0, 0, 255), 2)
            
            output_path = os.path.join(self.output_dir, f"frame_{frame_count:04d}.png")
            cv2.imwrite(output_path, frame_with_lines)
            frame_count += 1
        
        cap.release()
        messagebox.showinfo("Success", f"Processed {frame_count} frames")
    
    def show_index(self):
        index_window = tk.Toplevel(self.root)
        index_window.title("Video Index")
        
        frames = sorted([f for f in os.listdir(self.output_dir) if f.startswith("frame_")])
        
        if not frames:
            messagebox.showerror("Error", "No processed frames found.")
            index_window.destroy()
            return
        
        for i, frame_file in enumerate(frames[:4]):
            frame_path = os.path.join(self.output_dir, frame_file)
            img = Image.open(frame_path)
            img.thumbnail((200, 200))
            
            img_tk = ImageTk.PhotoImage(img)
            panel = tk.Label(index_window, image=img_tk)
            panel.image = img_tk
            panel.grid(row=0, column=i, padx=5, pady=5)
            
            btn = tk.Button(index_window, text=f"Play from {frame_file}", 
                          command=lambda f=frame_file: self.play_from_frame(f))
            btn.grid(row=1, column=i, padx=5, pady=5)
    
    def play_from_frame(self, frame_file):
        frame_num = int(frame_file.split("_")[1].split(".")[0])
        self.current_frame_index = frame_num
        self.play_video()
    
    def play_video(self):
        if not self.video_path:
            messagebox.showerror("Error", "Load a video first")
            return
        
        if not self.cap:
            self.cap = cv2.VideoCapture(self.video_path)
        
        self.playing = True
        self.update_video()
    
    def update_video(self):
        if not self.playing:
            return
        
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
            ret, frame = self.cap.read()
            
            if ret:
                frame_with_lines = frame.copy()
                for x in self.x_lines:
                    cv2.line(frame_with_lines, (x, 0), (x, frame.shape[0]), (0, 255, 0), 2)
                for y in self.y_lines:
                    cv2.line(frame_with_lines, (0, y), (frame.shape[1], y), (0, 0, 255), 2)
                
                cv2.imshow("Video Player", frame_with_lines)
                self.current_frame_index += 1
                
                delay = int(1000 / self.cap.get(cv2.CAP_PROP_FPS))
                self.root.after(delay, self.update_video)
            else:
                self.stop_video()
    
    def pause_video(self):
        self.playing = False
        try:
            cv2.destroyWindow("Video Player")
        except:
            pass
    
    def stop_video(self):
        self.playing = False
        self.current_frame_index = 0
        if self.cap:
            self.cap.release()
            self.cap = None
        try:
            cv2.destroyWindow("Video Player")
        except:
            pass
    
    def prev_frame(self):
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.show_current_frame()
    
    def next_frame(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(self.video_path)
        
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.current_frame_index < total_frames - 1:
            self.current_frame_index += 1
            self.show_current_frame()
    
    def show_current_frame(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(self.video_path)
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
        ret, frame = self.cap.read()
        
        if ret:
            frame_with_lines = frame.copy()
            for x in self.x_lines:
                cv2.line(frame_with_lines, (x, 0), (x, frame.shape[0]), (0, 255, 0), 2)
            for y in self.y_lines:
                cv2.line(frame_with_lines, (0, y), (frame.shape[1], y), (0, 0, 255), 2)
            
            cv2.imshow("Video Player", frame_with_lines)
            self.status_var.set(f"Frame: {self.current_frame_index}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScannerApp(root)
    root.mainloop()
