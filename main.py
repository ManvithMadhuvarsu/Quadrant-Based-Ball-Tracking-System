import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np

# Global variables
quadrants = []  
selected_quadrant = 0  

# Color ranges for each ball (adjust as per your video and lighting conditions)
color_ranges = {
    'orange': ((5, 150, 150), (15, 255, 255)),  
    'white': ((0, 0, 100), (0, 255, 255)),   
    'greenish_blue': ((80, 100, 5), (100, 255, 65)), 
    'yellow': ((20, 100, 100), (30, 255, 255))
}

balls = {
    'orange': None,
    'white': None,
    'greenish_blue': None,
    'yellow': None
}

ball_quadrants = {
    'orange': None,
    'white': None,
    'greenish_blue': None,
    'yellow': None
}

def detect_color(frame, color_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_range = np.array(color_ranges[color_name][0])
    upper_range = np.array(color_ranges[color_name][1])
    mask = cv2.inRange(hsv, lower_range, upper_range)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        center, radius = cv2.minEnclosingCircle(contours[0])
        return center, radius
    return None, None

def get_quadrant(x, y):
    for i, (q_x, q_y, q_x2, q_y2) in enumerate(quadrants):
        if q_x <= x <= q_x2 and q_y <= y <= q_y2:
            return i + 1  
    return None

def on_mouse_click(event, x, y, flags, param):
    global selected_quadrant
    if selected_quadrant < 4 and event == cv2.EVENT_LBUTTONDOWN:
        quadrants.append((x - 230, y - 230, x + 230, y + 230))
        selected_quadrant += 1
        if selected_quadrant == 4:
            cv2.destroyAllWindows()
            process_selected_files()

def show_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return
    
    ret, frame = cap.read()
    if ret:
        cv2.namedWindow('Select Quadrants', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Select Quadrants', frame.shape[1], frame.shape[0])
        cv2.setMouseCallback('Select Quadrants', on_mouse_click)
        cv2.putText(frame, "Click to define each quadrant", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        while True:
            for (q_x, q_y, q_x2, q_y2) in quadrants:
                cv2.rectangle(frame, (q_x, q_y), (q_x2, q_y2), (0, 255, 0), 2)
            
            cv2.imshow('Select Quadrants', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if selected_quadrant == 4:
                break
    else:
        print("Error: Couldn't read frame from the video file.")
    
    cap.release()

def process_video(video_path, output_video_path, output_text_path, video_format):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if video_format == 'AVI':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    elif video_format == 'MP4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        messagebox.showerror("Error", "Unsupported video format.")
        return
    
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    events = []
    frame_index = 0
    
    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', frame_width, frame_height)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        for (q_x, q_y, q_x2, q_y2) in quadrants:
            cv2.rectangle(frame, (q_x, q_y), (q_x2, q_y2), (0, 255, 0), 2)
        
        for color_name in balls.keys():
            center, radius = detect_color(frame, color_name)
            if center is not None and radius is not None:
                x, y = int(center[0]), int(center[1])
                
                current_quadrant = get_quadrant(x, y)
                
                if current_quadrant is not None:
                    if ball_quadrants[color_name] != current_quadrant:
                        if ball_quadrants[color_name] is not None:
                            events.append({'time': frame_index / fps, 'quadrant': ball_quadrants[color_name], 'color': color_name, 'event_type': 'Exit'})
                            cv2.putText(frame, f"Exit {color_name} ({ball_quadrants[color_name]})", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        events.append({'time': frame_index / fps, 'quadrant': current_quadrant, 'color': color_name, 'event_type': 'Entry'})
                        cv2.putText(frame, f"Entry {color_name} ({current_quadrant})", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    ball_quadrants[color_name] = current_quadrant
                else:
                    if ball_quadrants[color_name] is not None:
                        events.append({'time': frame_index / fps, 'quadrant': ball_quadrants[color_name], 'color': color_name, 'event_type': 'Exit'})
                        cv2.putText(frame, f"Exit {color_name} ({ball_quadrants[color_name]})", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    ball_quadrants[color_name] = None
            
            for color_name, ball_data in balls.items():
                if ball_data is not None:
                    center, radius = ball_data
                    x, y = int(center[0]), int(center[1])
                    cv2.circle(frame, (x, y), int(radius), (0, 255, 0), 2)
                    cv2.putText(frame, color_name, (x - 10, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        out.write(frame)
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_index += 1
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Save events to a text file
    with open(output_text_path, 'w') as f:
        for event in events:
            f.write(f"{event['time']}, {event['quadrant']}, {event['color']}, {event['event_type']}\n")

# Tkinter GUI setup
def select_files():
    global video_path_entry, output_video_path_entry, output_text_path_entry
    
    video_path = filedialog.askopenfilename(title="Select Input Video File", filetypes=(("MP4 files", ".mp4"), ("All files", ".*")))
    output_video_path = filedialog.asksaveasfilename(title="Save Processed Video As", defaultextension=".avi", filetypes=(("AVI files", ".avi"), ("All files", ".*")))
    output_text_path = filedialog.asksaveasfilename(title="Save Output Text As", defaultextension=".txt", filetypes=(("Text files", ".txt"), ("All files", ".*")))
    
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, video_path)
    output_video_path_entry.delete(0, tk.END)
    output_video_path_entry.insert(0, output_video_path)
    output_text_path_entry.delete(0, tk.END)
    output_text_path_entry.insert(0, output_text_path)
    
    show_first_frame(video_path)

def process_selected_files():
    video_path = video_path_entry.get()
    output_video_path = output_video_path_entry.get()
    output_text_path = output_text_path_entry.get()
    
    video_format = output_video_path.split('.')[-1].upper()
    
    process_video(video_path, output_video_path, output_text_path, video_format)
    messagebox.showinfo("Processing Complete", "Video processing completed successfully!")

root = tk.Tk()
root.title("Video Processing")

root.geometry('600x500')

tk.Label(root, text="Input Video File:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_files).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Output Video File:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
output_video_path_entry = tk.Entry(root, width=50)
output_video_path_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Output Text File:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
output_text_path_entry = tk.Entry(root, width=50)
output_text_path_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Button(root, text="Process Video", command=process_selected_files).grid(row=3, column=1, pady=20)

root.mainloop()