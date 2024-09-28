import tkinter as tk
from PIL import Image, ImageTk

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.path = path
        self.frames = []
        self.load_frames()
        self.current_frame = 0
        self.show_frame()

    def load_frames(self):
        try:
            image = Image.open(self.path)
            for frame in range(image.n_frames):
                image.seek(frame)
                frame_image = ImageTk.PhotoImage(image.copy())
                self.frames.append(frame_image)
        except Exception as e:
            print(f"Error loading GIF frames: {e}")

    def show_frame(self):
        if self.frames:
            frame = self.frames[self.current_frame]
            self.config(image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(100, self.show_frame)  # Adjust the delay for your GIF's frame rate

def display_gif(root,gif_path):
    try : 
        gif_label = AnimatedGIF(root, gif_path)
        gif_label.pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        print(f"Error loading animated GIF: {e}")

    root.mainloop()

