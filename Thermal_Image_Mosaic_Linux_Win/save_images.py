from PIL import Image
from tkinter import filedialog
import datetime
import os

def save_merged_images(canvas, image_items, separator_y, zone):
    items = [
        (canvas.bbox(item), image_items[item]["image"], canvas.coords(item))
        for item in image_items
        if (canvas.coords(item)[1] < separator_y if zone == 'termal' else canvas.coords(item)[1] > separator_y)
    ]
    if not items:
        return

    items.sort(key=lambda i: i[2][0])  # x koordináta szerint

    min_y = min(b[1] for b, _, _ in items)
    max_y = max(b[3] for b, _, _ in items)
    width = sum(b[2] - b[0] for b, _, _ in items)
    height = max_y - min_y

    merged = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x_offset = 0
    for bbox, img, _ in items:
        merged.alpha_composite(img, (x_offset, bbox[1] - min_y))
        x_offset += img.width

    filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes, initialfile=f"{zone}_{now}")
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.bmp']:
            background = Image.new("RGB", merged.size, (255, 255, 255))
            background.paste(merged, mask=merged.split()[3])
            background.save(filename)
        else:
            merged.save(filename)


def save_canvas_snapshot(canvas, image_items):
    """
    Elmenti a canvas aktuális vizuális állapotát: átfedéssel, eltolással együtt.
    """
    from PIL import Image

    positioned_images = []
    for item_id, data in image_items.items():
        coords = canvas.coords(item_id)
        if not coords:
            continue
        x, y = map(int, coords)
        img = data["image"]
        positioned_images.append((img, x - img.width // 2, y - img.height // 2))

    if not positioned_images:
        return

    min_x = min(x for _, x, _ in positioned_images)
    min_y = min(y for _, _, y in positioned_images)
    max_x = max(x + img.width for img, x, _ in positioned_images)
    max_y = max(y + img.height for img, _, y in positioned_images)

    width = max_x - min_x
    height = max_y - min_y

    merged = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    for img, x, y in positioned_images:
        merged.alpha_composite(img, (x - min_x, y - min_y))

    filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes, initialfile=f"canvas_snapshot_{now}")
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.bmp']:
            background = Image.new("RGB", merged.size, (255, 255, 255))
            background.paste(merged, mask=merged.split()[3])
            background.save(filename)
        else:
            merged.save(filename)
