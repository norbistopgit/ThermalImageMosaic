# image_loader.py

from PIL import Image, ImageTk
import os
import tkinter as tk

def load_thumbnails_with_labels(folder_path, thumb_frame, thumb_size, callback):
    tk_refs = []
    if not os.path.isdir(folder_path):
        return tk_refs

    files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    x_offset = 10

    for idx, file in enumerate(files):
        path = os.path.join(folder_path, file)
        try:
            img = Image.open(path).resize(thumb_size)
            tk_img = ImageTk.PhotoImage(img)

            label_frame = tk.Frame(thumb_frame)
            label_frame.place(x=x_offset, y=0, width=thumb_size[0], height=thumb_size[1]+20)

            img_label = tk.Label(label_frame, image=tk_img, cursor="hand2")
            img_label.image = tk_img
            img_label.pack()

            text_label = tk.Label(label_frame, text=str(idx+1), font=("Arial", 8))
            text_label.pack()

            img_label.bind("<Button-1>", lambda e, p=path: callback(p))
            img_label.bind("<B1-Motion>", lambda e, p=path: callback(p))

            tk_refs.append(tk_img)
            x_offset += thumb_size[0] + 10
        except Exception as e:
            print(f"Hiba miniatűrnél: {e}")

    return tk_refs
