import tkinter as tk
from tkinter import PhotoImage
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
import os
import subprocess
import tkinter.messagebox as messagebox
import platform
from constants import RGB_FOLDER, TERMAL_FOLDER, THUMB_SIZE, IMG_SIZE, HELP_PDF_PATH
from image_loader import load_thumbnails_with_labels
from save_images import save_merged_images, save_canvas_snapshot

def resize_image_keep_aspect(img, max_width, max_height):
    w, h = img.size
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)



class FullscreenOverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Image Mosaic v1.0")

        script_dir = os.path.dirname(__file__)
        icon_path = os.path.join(script_dir, "icon.png")
        if os.path.exists(icon_path):
            icon = PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)

        self.tk_refs = []
        self.image_items = {}
        self.selected_item = None
        self.edit_window = None

        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Canvas View", command=lambda: save_canvas_snapshot(self.canvas, self.image_items))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Open Help", command=self.open_help_pdf)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

        self.termal_thumb_frame = tk.Frame(root, height=80)
        self.termal_thumb_frame.pack(fill=tk.X, padx=5, pady=0)

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.rgb_thumb_frame = tk.Frame(root, height=80)
        self.rgb_thumb_frame.pack(fill=tk.X, padx=5, pady=0)

        self.canvas = tk.Canvas(self.top_frame, bg="darkgray", scrollregion=(0, 0, 5000, 2000), xscrollincrement=10, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.TOP, fill=tk.X)
        self.canvas.config(xscrollcommand=self.h_scroll.set)

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', lambda e: self.on_drop_canvas(e, 'top'))

        footer = tk.Label(self.root, text="Thermal Image Mosaic v1.0 – Developed by Norbert Radics. © 2025", font=("Arial", 9), fg="gray")
        footer.pack(side=tk.BOTTOM, pady=(2, 4))

        edit_btn = tk.Button(self.root, text="Edit Selected Image", command=self.edit_selected)
        edit_btn.pack(side=tk.BOTTOM, pady=(0, 2))

        self.separator_y = self.root.winfo_screenheight() // 2
        for y in range(0, self.root.winfo_screenheight(), 100):
            self.canvas.create_line(0, y, 5000, y, fill="#444", dash=(2, 4))
        for x in range(0, 5001, 100):
            self.canvas.create_line(x, 0, x, self.root.winfo_screenheight(), fill="#444", dash=(2, 4))
            self.canvas.create_line(x, 5, x, 25, fill="black")
            self.canvas.create_text(x, 30, text=str(x), fill="black", font=("Arial", 8))

        self.root.bind("<Delete>", self.delete_selected_item)

        self.tk_refs += load_thumbnails_with_labels(TERMAL_FOLDER, self.termal_thumb_frame, THUMB_SIZE, lambda p: self.place_image(p, zone='top'))
        self.tk_refs += load_thumbnails_with_labels(RGB_FOLDER, self.rgb_thumb_frame, THUMB_SIZE, lambda p: self.place_image(p, zone='bottom'))

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Thermal Image Mosaic v1.0\n\n"
            "Developed by Norbert Radics. (2025)\n\n"
            "This tool allows users to visually align and merge RGB and thermal images into horizontal mosaics.\n"
            "Supports drag-and-drop, transparency adjustment,\n"
            "RGB channel tuning, and export.\n\n"
            "License: MIT – free for personal and academic use.\n\n"
            "Source: https://github.com/norbistopgit/ThermalImageMosaic"
        )

    def place_image(self, path, zone='top'):
        try:
            img = Image.open(path).resize(IMG_SIZE).convert("RGBA")
            tk_img = ImageTk.PhotoImage(img)
            self.tk_refs.append(tk_img)
            screen_width = self.root.winfo_screenwidth()
            x = screen_width // 2
            y = self.separator_y // 2 if zone == 'top' else self.separator_y + IMG_SIZE[1] // 2 + 30
            item = self.canvas.create_image(x, y, image=tk_img, anchor="center")
            self.image_items[item] = {
                "original": img.copy(),
                "image": img,
                "tk": tk_img,
                "alpha": 1.0,
                "r": 1.0,
                "g": 1.0,
                "b": 1.0
            }
            self.bind_drag_and_select(item)
        except Exception as e:
            print(f"Hiba kép elhelyezésnél: {e}")

    def bind_drag_and_select(self, item):
        def on_click(event, item=item):
            self.selected_item = item
            self.redraw_border(item)

        def on_drag_start(event, item=item):
            self.canvas.tag_raise(item)
            self._drag_data = {"item": item, "x": event.x, "y": event.y}

        def on_drag(event):
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], dx, dy)
            self.canvas.move(f"border_{self._drag_data['item']}", dx, dy)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

        self.canvas.tag_bind(item, "<Button-1>", on_click)
        self.canvas.tag_bind(item, "<ButtonPress-1>", on_drag_start)
        self.canvas.tag_bind(item, "<B1-Motion>", on_drag)
        self.canvas.tag_bind(item, "<ButtonPress>", lambda e, i=item: self.on_any_click(e, i))

    def redraw_border(self, item):
        for tag in self.canvas.find_withtag("border"):
            self.canvas.delete(tag)
        bbox = self.canvas.bbox(item)
        if not bbox:
            return
        x1, y1, x2, y2 = bbox
        border = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=4, tags=("border", f"border_{item}"))
        self.canvas.tag_lower(border, item)

    def on_any_click(self, event, item):
        self.selected_item = item
        self.redraw_border(item)
        if event.num == 3 or (platform.system() == "Darwin" and event.num == 1 and (event.state & 0x0004)):
            self.show_edit_window(item)

    def edit_selected(self):
        if self.selected_item and self.selected_item in self.image_items:
            self.show_edit_window(self.selected_item)
            return

        # Ha nincs kiválasztott elem, próbáljuk meg az egér alatti elemet megtalálni
        x, y = self.root.winfo_pointerx() - self.canvas.winfo_rootx(), self.root.winfo_pointery() - self.canvas.winfo_rooty()
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(overlapping):
            if item in self.image_items:
                self.selected_item = item
                self.redraw_border(item)
                self.show_edit_window(item)
                return

        messagebox.showinfo("No selection", "Please click on an image to select it first.")

    def delete_selected_item(self, event=None):
        if not self.selected_item:
            return
        self.canvas.delete(self.selected_item)
        self.canvas.delete(f"border_{self.selected_item}")
        if self.selected_item in self.image_items:
            del self.image_items[self.selected_item]
        self.selected_item = None

    def show_edit_window(self, item):
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.destroy()

        data = self.image_items[item]
        top = tk.Toplevel(self.root)
        top.title("Edit Image")
        top.transient(self.root)              # ne legyen teljes képernyős
        top.resizable(True, True)             # átméretezhető legyen
        top.overrideredirect(False)           # legyen címsora és mozgatható
        top.geometry("+%d+%d" % (self.root.winfo_pointerx(), self.root.winfo_pointery()))
        self.edit_window = top

        tk.Label(top, text="Alpha:").pack()
        alpha_slider = tk.Scale(top, from_=0, to=100, orient=tk.HORIZONTAL,
                                command=lambda val: self._update_and_refresh(item, alpha=float(val) / 100))
        alpha_slider.set(int(data["alpha"] * 100))
        alpha_slider.pack()

        labels = {"r": "Red", "g": "Green", "b": "Blue"}
        for color in ["r", "g", "b"]:
            tk.Label(top, text=f"{labels[color]}:").pack()
            slider = tk.Scale(top, from_=0, to=200, orient=tk.HORIZONTAL)
            slider.set(int(data[color] * 100))
            slider.pack()
            slider.config(command=lambda val, c=color: self._update_and_refresh(item, **{c: float(val) / 100}))

        tk.Button(top, text="Delete Image", fg="red", command=lambda: self.delete_and_close(item, top)).pack(pady=10)


    def _update_and_refresh(self, item, **kwargs):
        data = self.image_items[item]
        for k, v in kwargs.items():
            data[k] = v
        self.update_display_image(item)

    def update_display_image(self, item):
        data = self.image_items[item]
        img = data["original"].copy()
        r, g, b = data["r"], data["g"], data["b"]

        if img.mode != "RGBA":
            img = img.convert("RGBA")
        r_band, g_band, b_band, a_band = img.split()

        r_band = r_band.point(lambda i: min(255, max(0, int(i * r))))
        g_band = g_band.point(lambda i: min(255, max(0, int(i * g))))
        b_band = b_band.point(lambda i: min(255, max(0, int(i * b))))

        img = Image.merge("RGBA", (r_band, g_band, b_band, a_band))

        alpha_layer = Image.new("L", img.size, int(data["alpha"] * 255))
        img.putalpha(alpha_layer)

        tk_img = ImageTk.PhotoImage(img)
        data["tk"] = tk_img
        data["image"] = img
        self.tk_refs.append(tk_img)
        self.canvas.itemconfig(item, image=tk_img)

    def delete_and_close(self, item, window):
        self.canvas.delete(item)
        self.canvas.delete(f"border_{item}")
        if item in self.image_items:
            del self.image_items[item]
        if self.selected_item == item:
            self.selected_item = None
        window.destroy()

    def open_help_pdf(self):
        try:
            if os.path.exists(HELP_PDF_PATH):
                if platform.system() == "Windows":
                    subprocess.Popen(['start', '', HELP_PDF_PATH], shell=True)
                elif platform.system() == "Darwin":
                    subprocess.Popen(['open', HELP_PDF_PATH])
                else:
                    subprocess.Popen(['xdg-open', HELP_PDF_PATH])
            else:
                print("A PDF fájl nem található:", HELP_PDF_PATH)
        except Exception as e:
            print(f"Nem sikerült megnyitni a súgófájlt: {e}")
def on_drop_canvas(self, event, zone):
    try:
        paths = self.root.tk.splitlist(event.data)
        for path in paths:
            if os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                self.place_image(path, zone=zone)
    except Exception as e:
        print(f"Hiba a fájl behúzásakor: {e}")
