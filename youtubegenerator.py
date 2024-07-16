import tkinter as tk
from tkinter import ttk
import pygame
import random
import math
import moviepy.editor as mpy
import numpy as np
import tempfile
import wave
from threading import Thread

pygame.init()

note_frequencies = {
    'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20, 'F1': 43.65, 'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
    'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
    'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53,
    'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02, 'E7': 2637.02, 'F7': 2793.83, 'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'A#7': 3729.31, 'B7': 3951.07,
    'C8': 4186.01, 'C#8': 4434.92, 'D8': 4698.63, 'D#8': 4978.03, 'E8': 5274.04, 'F8': 5587.65, 'F#8': 5919.91, 'G8': 6271.93, 'G#8': 6644.88, 'A8': 7040.00, 'A#8': 7458.62, 'B8': 7902.13
}

def generate_tone_wav(frequency, duration=0.2, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = (0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with wave.open(temp_wav.name, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((wave_data * 32767).astype(np.int16).tobytes())
    return temp_wav.name

def create_video(options, progress_var, video_index):
    width, height = 720, 1280
    center = (width // 2, height // 2)
    size = 250
    ring_thickness = 20
    ball_color = (255, 255, 255)
    initial_radius = options['ball_size']
    radius = initial_radius
    speed = options['speed'] / 10
    gravity = 0.1 if options['gravity'] else 0
    shape = options['shape']
    show_counter = options['show_counter']
    draw_lines = options['draw_lines']
    top_text = options['top_text']
    bottom_text = options['bottom_text']
    notes_sequence = options['notes_sequence'].split()
    size_mode = options['size_mode']
    speed_mode = options['speed_mode']
    collision_based = options['collision_based']
    
    note_index = 0

    num_frames = 59 * 30
    frames = []
    collision_points = []
    audio_clips = []

    x, y = center
    angle = random.uniform(0, 2 * math.pi)
    dx = speed * math.cos(angle)
    dy = speed * math.sin(angle)
    collision_count = 0

    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

    def draw_pentagon(surface, color, center, size, thickness):
        points = []
        for i in range(5):
            angle = math.radians(72 * i - 90)
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surface, color, points, thickness)
        return points

    def point_line_distance(px, py, x1, y1, x2, y2):
        num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        den = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        return num / den

    for frame_count in range(num_frames):
        screen = pygame.Surface((width, height))
        screen.fill((0, 0, 0))

        if show_counter:
            collision_text = font.render(f"Collisions: {collision_count}", True, (255, 255, 255))
            screen.blit(collision_text, (10, 10))

        top_text_render = large_font.render(top_text, True, (255, 255, 255))
        bottom_text_render = large_font.render(bottom_text, True, (255, 255, 255))
        screen.blit(top_text_render, (center[0] - top_text_render.get_width() // 2, center[1] - size - 60))
        screen.blit(bottom_text_render, (center[0] - bottom_text_render.get_width() // 2, center[1] + size + 40))

        if shape == 'circle':
            pygame.draw.circle(screen, (255, 0, 0), center, size, ring_thickness)
        elif shape == 'square':
            pygame.draw.rect(screen, (255, 0, 0), (center[0] - size, center[1] - size, size * 2, size * 2), ring_thickness)
        elif shape == 'rectangle':
            rect_width, rect_height = size * 2, size
            pygame.draw.rect(screen, (255, 0, 0), (center[0] - rect_width // 2, center[1] - rect_height // 2, rect_width, rect_height), ring_thickness)
        elif shape == 'pentagon':
            pentagon_points = draw_pentagon(screen, (255, 0, 0), center, size, ring_thickness)

        pygame.draw.circle(screen, ball_color, (int(x), int(y)), int(radius))

        x += dx
        y += dy
        dy += gravity

        if not collision_based:
            if size_mode == 'sizes_down':
                radius = initial_radius * (1 - (frame_count / num_frames) * 0.02)
            elif size_mode == 'sizes_up':
                radius = initial_radius * (1 + (frame_count / num_frames) * 0.02)

            if speed_mode == 'slows_down':
                speed_multiplier = 1 - (frame_count / num_frames) * 0.02
                dx *= speed_multiplier
                dy *= speed_multiplier
            elif speed_mode == 'speeds_up':
                speed_multiplier = 1 + (frame_count / num_frames) * 0.02
                dx *= speed_multiplier
                dy *= speed_multiplier

        dx += random.uniform(-0.05, 0.05)
        dy += random.uniform(-0.05, 0.05)

        collision_happened = False

        if shape == 'circle':
            dist = math.hypot(x - center[0], y - center[1])
            if dist >= size - radius:
                normal_x = (x - center[0]) / dist
                normal_y = (y - center[1]) / dist
                dot_product = dx * normal_x + dy * normal_y
                dx = dx - 2 * dot_product * normal_x
                dy = dy - 2 * dot_product * normal_y

                collision_happened = True

                overlap = dist - (size - radius)
                x -= overlap * normal_x
                y -= overlap * normal_y

        elif shape in ['square', 'rectangle', 'pentagon']:
            if shape == 'square':
                rect_width, rect_height = size * 2, size * 2
                edges = [((center[0] - size, center[1] - size), (center[0] + size, center[1] - size)),
                         ((center[0] + size, center[1] - size), (center[0] + size, center[1] + size)),
                         ((center[0] + size, center[1] + size), (center[0] - size, center[1] + size)),
                         ((center[0] - size, center[1] + size), (center[0] - size, center[1] - size))]
            elif shape == 'rectangle':
                rect_width, rect_height = size * 2, size
                edges = [((center[0] - rect_width // 2, center[1] - rect_height // 2), (center[0] + rect_width // 2, center[1] - rect_height // 2)),
                         ((center[0] + rect_width // 2, center[1] - rect_height // 2), (center[0] + rect_width // 2, center[1] + rect_height // 2)),
                         ((center[0] + rect_width // 2, center[1] + rect_height // 2), (center[0] - rect_width // 2, center[1] + rect_height // 2)),
                         ((center[0] - rect_width // 2, center[1] + rect_height // 2), (center[0] - rect_width // 2, center[1] - rect_height // 2))]
            elif shape == 'pentagon':
                edges = [(pentagon_points[i], pentagon_points[(i + 1) % 5]) for i in range(5)]

            for edge in edges:
                (x1, y1), (x2, y2) = edge
                if point_line_distance(x, y, x1, y1, x2, y2) <= radius:
                    collision_happened = True
                    edge_vec = (x2 - x1, y2 - y1)
                    edge_len = math.hypot(edge_vec[0], edge_vec[1])
                    edge_unit_vec = (edge_vec[0] / edge_len, edge_vec[1] / edge_len)
                    normal_vec = (-edge_unit_vec[1], edge_unit_vec[0])
                    dot_product = dx * normal_vec[0] + dy * normal_vec[1]
                    dx -= 2 * dot_product * normal_vec[0]
                    dy -= 2 * dot_product * normal_vec[1]

                    overlap = radius - point_line_distance(x, y, x1, y1, x2, y2)
                    x -= overlap * normal_vec[0]
                    y -= overlap * normal_vec[1]

                    break

        if collision_happened:
            collision_count += 1
            note = notes_sequence[note_index]
            frequency = note_frequencies[note]
            temp_wav_path = generate_tone_wav(frequency, 0.2)
            audio_clip = mpy.AudioFileClip(temp_wav_path).set_start(frame_count / 30)
            audio_clips.append(audio_clip)
            note_index = (note_index + 1) % len(notes_sequence)

            if collision_based:
                if size_mode == 'sizes_down':
                    radius *= 0.95
                elif size_mode == 'sizes_up':
                    radius *= 1.05

                if speed_mode == 'slows_down':
                    dx *= 0.95
                    dy *= 0.95
                elif speed_mode == 'speeds_up':
                    dx *= 1.05
                    dy *= 1.05

            collision_points.append((int(x), int(y)))

        if draw_lines:
            for point in collision_points:
                pygame.draw.line(screen, (255, 255, 255), point, (int(x), int(y)))

        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1, 0, 2))
        frames.append(frame)

        progress_var.set((frame_count + 1) / num_frames * 100)

    clip = mpy.ImageSequenceClip(frames, fps=30)
    audio = mpy.CompositeAudioClip(audio_clips)
    clip = clip.set_audio(audio)
    clip.write_videofile(f"bouncing_ball{video_index}.mp4", codec="libx264")

def start_simulation():
    options = {
        'shape': shape_var.get(),
        'gravity': gravity_var.get(),
        'speed': speed_slider.get(),
        'ball_size': ball_size_slider.get(),
        'show_counter': show_counter_var.get(),
        'draw_lines': draw_lines_var.get(),
        'top_text': top_text_var.get(),
        'bottom_text': bottom_text_var.get(),
        'notes_sequence': notes_sequence_var.get(),
        'size_mode': size_mode_var.get(),
        'speed_mode': speed_mode_var.get(),
        'collision_based': collision_based_var.get()
    }
    progress_var.set(0)
    Thread(target=create_video, args=(options, progress_var, 1)).start()

root = tk.Tk()
root.title("Video Generator")

shape_var = tk.StringVar(value="circle")
gravity_var = tk.BooleanVar(value=False)
draw_lines_var = tk.BooleanVar(value=False)
show_counter_var = tk.BooleanVar(value=False)
collision_based_var = tk.BooleanVar(value=False)
top_text_var = tk.StringVar(value="")
bottom_text_var = tk.StringVar(value="")
notes_sequence_var = tk.StringVar(value="C4 D4 E4 F4 G4 A4 B4 C5")
size_mode_var = tk.StringVar(value="constant")
speed_mode_var = tk.StringVar(value="constant")
progress_var = tk.DoubleVar()

ttk.Label(root, text="Select Shape:").grid(column=0, row=0)
ttk.Radiobutton(root, text="Circle", variable=shape_var, value="circle").grid(column=1, row=0)
ttk.Radiobutton(root, text="Square", variable=shape_var, value="square").grid(column=2, row=0)
ttk.Radiobutton(root, text="Rectangle", variable=shape_var, value="rectangle").grid(column=3, row=0)
ttk.Radiobutton(root, text="Pentagon", variable=shape_var, value="pentagon").grid(column=4, row=0)

ttk.Checkbutton(root, text="Affected by Gravity", variable=gravity_var).grid(column=0, row=1)
ttk.Checkbutton(root, text="Draw Lines", variable=draw_lines_var).grid(column=1, row=1)
ttk.Checkbutton(root, text="Show Collision Counter", variable=show_counter_var).grid(column=2, row=1)
ttk.Checkbutton(root, text="Adjust on Collision", variable=collision_based_var).grid(column=3, row=1)

ttk.Label(root, text="Speed:").grid(column=0, row=2)
speed_slider = tk.Scale(root, from_=1, to=500, orient='horizontal')
speed_slider.set(50)
speed_slider.grid(column=1, row=2, columnspan=3)

ttk.Label(root, text="Ball Size:").grid(column=0, row=3)
ball_size_slider = tk.Scale(root, from_=10, to=100, orient='horizontal')
ball_size_slider.set(50)
ball_size_slider.grid(column=1, row=3, columnspan=3)

ttk.Label(root, text="Top Text:").grid(column=0, row=4)
top_text_entry = ttk.Entry(root, textvariable=top_text_var).grid(column=1, row=4, columnspan=3)

ttk.Label(root, text="Bottom Text:").grid(column=0, row=5)
bottom_text_entry = ttk.Entry(root, textvariable=bottom_text_var).grid(column=1, row=5, columnspan=3)

ttk.Label(root, text="Notes Sequence:").grid(column=0, row=6)
notes_sequence_entry = ttk.Entry(root, textvariable=notes_sequence_var).grid(column=1, row=6, columnspan=3)

ttk.Label(root, text="Size Mode:").grid(column=0, row=7)
ttk.Radiobutton(root, text="Sizes Down", variable=size_mode_var, value="sizes_down").grid(column=1, row=7)
ttk.Radiobutton(root, text="Constant", variable=size_mode_var, value="constant").grid(column=2, row=7)
ttk.Radiobutton(root, text="Sizes Up", variable=size_mode_var, value="sizes_up").grid(column=3, row=7)

ttk.Label(root, text="Speed Mode:").grid(column=0, row=8)
ttk.Radiobutton(root, text="Slows Down", variable=speed_mode_var, value="slows_down").grid(column=1, row=8)
ttk.Radiobutton(root, text="Constant", variable=speed_mode_var, value="constant").grid(column=2, row=8)
ttk.Radiobutton(root, text="Speeds Up", variable=speed_mode_var, value="speeds_up").grid(column=3, row=8)

ttk.Button(root, text="Start Simulation", command=start_simulation).grid(column=0, row=9, columnspan=4)

ttk.Label(root, text="Progress:").grid(column=0, row=10)
ttk.Progressbar(root, variable=progress_var, maximum=100).grid(column=1, row=10, columnspan=3, sticky='we')

root.mainloop()
