from tkinterdnd2 import TkinterDnD
from main_window import FullscreenOverlayApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FullscreenOverlayApp(root)
    root.mainloop()
