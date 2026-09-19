import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os
import json
import io
from PIL import Image, ImageTk, ImageOps, ImageDraw

class ComicReader:
    def __init__(self, root):
        self.root = root
        self.root.title("GhostCBZ - Elite Edition")
        self.root.geometry("950x750")
        self.root.configure(bg="#121212")
        self.root.minsize(600, 600)

        # Core Variables
        self.archive_path = None
        self.image_list = []
        self.current_index = 0
        self.current_image = None
        self.history_file = "reader_history.json"
        self.history_data = self.load_all_history()
        
        # Features States
        self.is_fullscreen = False
        self.is_double_page = False
        self.is_night_mode = False
        
        # User Preferences (Toggles)
        self.shortcuts_enabled = True
        self.history_enabled = True
        
        # Magnifier (Lens) Variables
        self.magnifier_item = None
        self.drawn_width = 0
        self.drawn_height = 0
        self.x_offset = 0
        self.y_offset = 0

        self.setup_modern_ui()
        self.bind_keys()
        self.show_home_screen()

    def load_all_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {}

    def setup_modern_ui(self):
        self.top_bar = tk.Frame(self.root, bg="#1e1e1e", height=50)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        self.top_bar.pack_propagate(False)

        btn_style = {
            "bg": "#3498db", "fg": "white", "activebackground": "#2980b9", 
            "activeforeground": "white", "bd": 0, "cursor": "hand2",
            "font": ("Segoe UI", 9, "bold"), "padx": 15, "pady": 5
        }

        self.btn_open = tk.Button(self.top_bar, text="📂 Open File", command=self.open_file, **btn_style)
        self.btn_open.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Toggle Shortcuts Button
        self.btn_shortcuts = tk.Button(self.top_bar, text="⚡ Shortcuts: ON", command=self.toggle_shortcuts,
                                      bg="#1e1e1e", fg="white", bd=0, activebackground="#333333", activeforeground="white", cursor="hand2")
        self.btn_shortcuts.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Toggle History Button
        self.btn_history = tk.Button(self.top_bar, text="🕒 History: ON", command=self.toggle_history,
                                      bg="#1e1e1e", fg="white", bd=0, activebackground="#333333", activeforeground="white", cursor="hand2")
        self.btn_history.pack(side=tk.LEFT, padx=5, pady=10)

        # English Hints Text
        self.hints_text = "[M] Double Page | [N] Night Mode | [F] Fullscreen | [Right-Click] Lens"
        self.lbl_hints = tk.Label(self.top_bar, text=self.hints_text, bg="#1e1e1e", fg="#7f8c8d", font=("Segoe UI", 9))
        self.lbl_hints.pack(side=tk.LEFT, padx=15, pady=10)

        self.lbl_page = tk.Label(self.top_bar, text="", bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 10))
        self.lbl_page.pack(side=tk.RIGHT, padx=15, pady=10)

        self.canvas_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#0d0d0d", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.home_frame = tk.Frame(self.canvas_frame, bg="#0d0d0d")

    def toggle_shortcuts(self):
        self.shortcuts_enabled = not self.shortcuts_enabled
        if self.shortcuts_enabled:
            self.btn_shortcuts.config(text="⚡ Shortcuts: ON", fg="white")
            self.lbl_hints.config(text=self.hints_text)
        else:
            self.btn_shortcuts.config(text="⚡ Shortcuts: OFF", fg="#7f8c8d")
            self.lbl_hints.config(text="")
            self.hide_magnifier(None)

    def toggle_history(self):
        self.history_enabled = not self.history_enabled
        if self.history_enabled:
            self.btn_history.config(text="🕒 History: ON", fg="white")
            self.save_history() # Geçmişi tekrar açınca mevcut durumu kaydet
        else:
            self.btn_history.config(text="🕒 History: OFF", fg="#7f8c8d")
            
            # 1. Hafızadaki geçmiş verisini tamamen temizle
            self.history_data.clear()
            
            # 2. Eğer diskte 'reader_history.json' dosyası varsa kalıcı olarak sil
            if os.path.exists(self.history_file):
                try:
                    os.remove(self.history_file)
                except Exception as e:
                    print(f"Failed to delete history file: {e}")
            
            # 3. Eğer şu an ana ekrandaysak, ekranı güncelle (kitap listesi anında yok olsun)
            if not self.archive_path:
                self.show_home_screen()

    def show_home_screen(self):
        self.canvas.pack_forget()
        self.home_frame.place(relwidth=1, relheight=1)
        for widget in self.home_frame.winfo_children(): widget.destroy()
            
        tk.Label(self.home_frame, text="GhostCBZ", bg="#0d0d0d", fg="white", font=("Segoe UI", 28, "bold")).pack(pady=(80, 5))
        tk.Label(self.home_frame, text="Zero Traces. Maximum Speed.", bg="#0d0d0d", fg="#3498db", font=("Segoe UI", 12)).pack(pady=(0, 30))
        
        if self.history_data and self.history_enabled:
            tk.Label(self.home_frame, text="Continue Reading:", bg="#0d0d0d", fg="#aaaaaa", font=("Segoe UI", 11)).pack(pady=10)
            recent_files = list(self.history_data.items())[-5:]
            recent_files.reverse()
            for path, page in recent_files:
                if os.path.exists(path):
                    btn = tk.Button(self.home_frame, text=f"📖 {os.path.basename(path)} (Page {page+1})", 
                                    bg="#1e1e1e", fg="#e0e0e0", activebackground="#2c3e50", activeforeground="white",
                                    bd=0, font=("Segoe UI", 10), cursor="hand2", pady=8, command=lambda p=path: self.open_specific_file(p))
                    btn.pack(pady=4, fill=tk.X, padx=150)
        else:
            status_text = "No reading history yet. Open an archive from the top menu."
            if not self.history_enabled:
                status_text = "Incognito Mode is ON. History is disabled and deleted."
                
            tk.Label(self.home_frame, text=status_text, bg="#0d0d0d", fg="#555555", font=("Segoe UI", 10)).pack(pady=20)

    def bind_keys(self):
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<d>", lambda e: self.next_page())
        self.root.bind("<space>", lambda e: self.next_page())
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<a>", lambda e: self.prev_page())
        self.canvas.bind("<Button-1>", self.mouse_click)
        
        self.root.bind("<m>", self.toggle_double_page)
        self.root.bind("<n>", self.toggle_night_mode)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-3>", self.update_magnifier)
        self.canvas.bind("<B3-Motion>", self.update_magnifier)
        self.canvas.bind("<ButtonRelease-3>", self.hide_magnifier)

    def toggle_double_page(self, event=None):
        if not self.shortcuts_enabled or not self.image_list: return
        self.is_double_page = not self.is_double_page
        self.show_image()

    def toggle_night_mode(self, event=None):
        if not self.shortcuts_enabled or not self.image_list: return
        self.is_night_mode = not self.is_night_mode
        self.show_image()

    def update_magnifier(self, event):
        if not self.shortcuts_enabled or not self.current_image or self.drawn_width == 0: return
        cx, cy = event.x, event.y
        ratio = self.drawn_width / self.current_image.width
        ix = (cx - self.x_offset) / ratio
        iy = (cy - self.y_offset) / ratio
        
        crop_size = 100
        box = (ix - crop_size, iy - crop_size, ix + crop_size, iy + crop_size)
        
        try:
            cropped = self.current_image.crop(box)
            mag_size = int(crop_size * 2 * 1.5)
            cropped = cropped.resize((mag_size, mag_size), Image.Resampling.NEAREST)
            
            draw = ImageDraw.Draw(cropped)
            draw.rectangle([0, 0, mag_size-1, mag_size-1], outline="white", width=4)
            
            self.mag_photo = ImageTk.PhotoImage(cropped)
            if self.magnifier_item: self.canvas.delete(self.magnifier_item)
            self.magnifier_item = self.canvas.create_image(cx, cy, image=self.mag_photo)
        except: pass

    def hide_magnifier(self, event):
        if self.magnifier_item:
            self.canvas.delete(self.magnifier_item)
            self.magnifier_item = None

    def toggle_fullscreen(self, event=None):
        if not self.shortcuts_enabled: return
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def mouse_click(self, event):
        if not self.archive_path: return
        if event.x > self.canvas.winfo_width() / 2: self.next_page()
        else: self.prev_page()

    def open_file(self):
        filepath = filedialog.askopenfilename(title="Select Comic Book (.cbz, .zip)", filetypes=(("Archives", "*.cbz *.zip"), ("All Files", "*.*")))
        if filepath: self.open_specific_file(filepath)

    def open_specific_file(self, filepath):
        self.archive_path = filepath
        self.home_frame.place_forget()
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.load_archive()

    def load_archive(self):
        try:
            with zipfile.ZipFile(self.archive_path, 'r') as z:
                valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
                self.image_list = sorted([f for f in z.namelist() if f.lower().endswith(valid_exts) and not f.startswith('__MACOSX')])
            if not self.image_list: return
            
            if self.history_enabled:
                self.current_index = self.history_data.get(self.archive_path, 0)
            else:
                self.current_index = 0
                
            if self.current_index >= len(self.image_list): self.current_index = 0
            self.show_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_history(self):
        if not self.archive_path or not self.history_enabled: return
        
        self.history_data[self.archive_path] = self.current_index
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history_data, f, ensure_ascii=False)

    def show_image(self):
        if not self.image_list: return
        
        with zipfile.ZipFile(self.archive_path, 'r') as z:
            img_data1 = z.read(self.image_list[self.current_index])
            img1 = Image.open(io.BytesIO(img_data1))
            
            if self.is_double_page and self.current_index + 1 < len(self.image_list):
                img_data2 = z.read(self.image_list[self.current_index + 1])
                img2 = Image.open(io.BytesIO(img_data2))
                
                w = img1.width + img2.width
                h = max(img1.height, img2.height)
                combined = Image.new('RGB', (w, h))
                combined.paste(img1, (0, 0))
                combined.paste(img2, (img1.width, 0))
                self.current_image = combined
                self.lbl_page.config(text=f"Page: {self.current_index + 1}-{self.current_index + 2} / {len(self.image_list)}")
            else:
                self.current_image = img1
                self.lbl_page.config(text=f"Page: {self.current_index + 1} / {len(self.image_list)}")

        if self.is_night_mode:
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            self.current_image = ImageOps.invert(self.current_image)

        self.render_image()
        self.save_history()

    def render_image(self):
        if not self.current_image: return
        c_width, c_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if c_width < 10 or c_height < 10: return
        
        i_width, i_height = self.current_image.size
        ratio = min(c_width / i_width, c_height / i_height)
        
        self.drawn_width = int(i_width * ratio)
        self.drawn_height = int(i_height * ratio)
        self.x_offset = (c_width - self.drawn_width) // 2
        self.y_offset = (c_height - self.drawn_height) // 2
        
        new_size = (self.drawn_width, self.drawn_height)
        self.tk_image = ImageTk.PhotoImage(self.current_image.resize(new_size, Image.Resampling.LANCZOS))
        
        self.canvas.delete("all")
        self.canvas.create_image(c_width // 2, c_height // 2, anchor=tk.CENTER, image=self.tk_image)

    def next_page(self):
        step = 2 if self.is_double_page else 1
        if self.image_list and self.current_index + step < len(self.image_list):
            self.current_index += step
            self.show_image()
        elif self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image()

    def prev_page(self):
        step = 2 if self.is_double_page else 1
        if self.image_list and self.current_index - step >= 0:
            self.current_index -= step
            self.show_image()
        elif self.image_list and self.current_index > 0:
            self.current_index = 0
            self.show_image()

    def on_resize(self, event):
        self.render_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicReader(root)
    root.mainloop()