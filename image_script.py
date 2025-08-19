from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- colors and settings ---
palette = [(0, 0, 0), (138, 58, 29), (255, 107, 53)]  # black, brown, orange
TARGET_HEIGHT = 500  # for pixelation

# --- image stuff ---
def load_image(path):
    return Image.open(path).convert("L")  # grayscale

def posterize(img):
    def posterize3(val):
        if val < 85: return 0
        elif val < 170: return 128
        else: return 255
    return img.point(posterize3)

def map_to_palette(img):
    out = Image.new("RGB", img.size)
    pix = img.load()
    pix_out = out.load()
    for y in range(img.height):
        for x in range(img.width):
            v = pix[x, y]
            if v == 0: pix_out[x, y] = palette[0]
            elif v == 128: pix_out[x, y] = palette[1]
            else: pix_out[x, y] = palette[2]
    return out

def pixelate(img):
    w, h = img.size
    nh = TARGET_HEIGHT
    nw = int(w * nh / h)
    tmp = img.resize((nw, nh), Image.NEAREST)
    return tmp.resize((w, h), Image.NEAREST)

def save_image(img, path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    base, _ = os.path.splitext(os.path.basename(path))
    img.save(os.path.join(output_folder, f"{base}_orange.png"))

def process_image(path, output_folder):
    img = load_image(path)
    img = posterize(img)
    img = map_to_palette(img)
    img = pixelate(img)
    save_image(img, path, output_folder)

# --- GUI stuff ---
root = tk.Tk()
root.title("Orange Terminal Batch Processor")
root.configure(bg="#2b2b2b")

script_dir = os.path.dirname(os.path.abspath(__file__))
default_output = os.path.join(script_dir, "output_images")
last_folder = script_dir
output_var = tk.StringVar(value=default_output)
selected_files = []

# --- variables for styling ---
FONT_BOLD = ("Arial", 11, "bold")
FONT_NORMAL = ("Arial", 10)
BUTTON_COLOR = "#ff6b35"
ENTRY_WIDTH = 45
THUMB_SIZE = 90

# --- thumbnails ---
thumb_frame = tk.Frame(root, bg="#2b2b2b")
thumb_frame.grid(row=5, column=0, columnspan=3, pady=15)

def show_file_previews(files):
    for w in thumb_frame.winfo_children():
        w.destroy()
    cols = 6
    for i, f in enumerate(files):
        row, col = divmod(i, cols)
        frame = tk.Frame(thumb_frame, bg="#3a3a3a", bd=1, relief="solid")
        img = Image.open(f)
        img.thumbnail((THUMB_SIZE, THUMB_SIZE))
        img_tk = ImageTk.PhotoImage(img)
        lbl = tk.Label(frame, image=img_tk, bg="#3a3a3a")
        lbl.image = img_tk
        lbl.pack(padx=5, pady=5)
        frame.grid(row=row, column=col, padx=5, pady=5)

# --- file selection ---
def select_input_files():
    global selected_files, last_folder
    files = filedialog.askopenfilenames(
        title="Select Images",
        initialdir=last_folder,
        filetypes=[("Image files", "*.png *.jpg *.jpeg")]
    )
    if files:
        last_folder = os.path.dirname(files[0])
        for f in files:
            if f not in selected_files:
                selected_files.append(f)
        files_selected_label.config(text=f"{len(selected_files)} files selected")
        show_file_previews(selected_files)

def select_output_folder():
    folder = filedialog.askdirectory(initialdir=default_output)
    if folder:
        output_var.set(folder)

def run_processing():
    if not selected_files:
        messagebox.showerror("Error", "No images selected!")
        return
    out_folder = output_var.get() or default_output
    for f in selected_files:
        process_image(f, out_folder)
    messagebox.showinfo("Done", f"Processed {len(selected_files)} images!")
    show_file_previews(selected_files)

# --- layout ---
pad_y = 8
pad_x = 10

# output folder stuff
tk.Label(root, text="Output Folder:", bg="#2b2b2b", fg="white", font=FONT_NORMAL).grid(row=0, column=0, sticky="e", pady=pad_y)
tk.Entry(root, textvariable=output_var, width=ENTRY_WIDTH, font=FONT_NORMAL).grid(row=0, column=1, pady=pad_y)
tk.Button(root, text="Browse", command=select_output_folder,
          bg=BUTTON_COLOR, fg="white", font=FONT_NORMAL).grid(row=0, column=2, pady=pad_y, padx=pad_x)

# select images
tk.Button(root, text="Select Images", command=select_input_files,
          bg=BUTTON_COLOR, fg="white", font=FONT_BOLD).grid(row=1, column=0, columnspan=3, pady=pad_y*2, sticky="ew", padx=pad_x)

# process button
tk.Button(root, text="Process Images", command=run_processing,
          bg=BUTTON_COLOR, fg="white", font=FONT_BOLD).grid(row=2, column=0, pady=pad_y*2, padx=pad_x, sticky="ew", columnspan=3)

# file count
files_selected_label = tk.Label(root, text="No files selected", bg="#2b2b2b", fg="white", font=FONT_NORMAL)
files_selected_label.grid(row=3, column=0, columnspan=3, pady=pad_y)

# center columns
for i in range(3):
    root.grid_columnconfigure(i, weight=1)

root.mainloop()
