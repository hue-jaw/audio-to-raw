import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import random

def apply_glitch(data, glitch_percent):
    """Applique un effet glitch en mélangeant/inversant des segments aléatoires."""
    if glitch_percent <= 0:
        return data
    num_segments = int(len(data) * glitch_percent / 100 / 100)  # nombre de petits segments à glitcher
    segment_len = 50  # longueur d’un segment en octets
    for _ in range(num_segments):
        start = random.randint(0, len(data)-segment_len-1)
        end = start + segment_len
        seg = data[start:end]
        # Choix aléatoire : inversion ou répétition
        if random.random() < 0.5:
            seg = seg[::-1]  # inversion
        else:
            seg = seg * 2  # répétition
            seg = seg[:segment_len]
        data[start:end] = seg
    return data

def convert_to_raw(input_file, output_folder, output_name, sample_rate, volume, highpass, corruption, glitch):
    if not os.path.isfile(input_file):
        messagebox.showerror("Erreur", f"Fichier source introuvable : {input_file}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(output_folder, output_name)
    
    # FFmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-ac", "1",
        "-ar", str(sample_rate),
        "-filter:a", f"volume={volume},highpass=f={highpass}",
        "-f", "u8",
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)

        # Lire le RAW pour corruption/glitch
        with open(output_file, "rb") as f:
            data = bytearray(f.read())

        # Appliquer corruption
        if corruption > 0:
            num_corrupt = int(len(data) * corruption / 100)
            for _ in range(num_corrupt):
                index = random.randint(0, len(data)-1)
                data[index] = random.randint(0, 255)

        # Appliquer glitch
        if glitch > 0:
            data = apply_glitch(data, glitch)

        # Réécrire le fichier RAW
        with open(output_file, "wb") as f:
            f.write(data)

        messagebox.showinfo("Succès", f"Conversion terminée !\nFichier RAW : {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"La conversion a échoué.\nDétails : {e}")

# --- GUI ---
root = tk.Tk()
root.title("Convertisseur Audio → RAW 8-bit (Corrupt & Glitch)")

# Source
tk.Label(root, text="Fichier source :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
source_entry = tk.Entry(root, width=50)
source_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Parcourir", command=lambda: source_entry.delete(0, tk.END) or source_entry.insert(0, filedialog.askopenfilename(title="Choisir le fichier source"))).grid(row=0, column=2, padx=5, pady=5)

# Dossier de sortie
tk.Label(root, text="Dossier de sortie :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Parcourir", command=lambda: output_folder_entry.delete(0, tk.END) or output_folder_entry.insert(0, filedialog.askdirectory(title="Choisir le dossier de sortie"))).grid(row=1, column=2, padx=5, pady=5)

# Nom fichier RAW
tk.Label(root, text="Nom du fichier RAW :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
output_name_entry = tk.Entry(root, width=50)
output_name_entry.insert(0, "output.raw")
output_name_entry.grid(row=2, column=1, padx=5, pady=5)

# Sample rate
tk.Label(root, text="Sample rate (Hz) :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
sample_entry = tk.Entry(root, width=20)
sample_entry.insert(0, "8000")
sample_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Volume
tk.Label(root, text="Volume (boost) :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
volume_entry = tk.Entry(root, width=20)
volume_entry.insert(0, "1.5")
volume_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

# High-pass
tk.Label(root, text="High-pass (Hz) :").grid(row=5, column=0, padx=5, pady=5, sticky="e")
highpass_entry = tk.Entry(root, width=20)
highpass_entry.insert(0, "200")
highpass_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# Corruption slider
tk.Label(root, text="Corruption (%) :").grid(row=6, column=0, padx=5, pady=5, sticky="e")
corruption_slider = tk.Scale(root, from_=0, to=50, orient=tk.HORIZONTAL)
corruption_slider.grid(row=6, column=1, padx=5, pady=5, sticky="w")

# Glitch slider
tk.Label(root, text="Glitch (%) :").grid(row=7, column=0, padx=5, pady=5, sticky="e")
glitch_slider = tk.Scale(root, from_=0, to=50, orient=tk.HORIZONTAL)
glitch_slider.grid(row=7, column=1, padx=5, pady=5, sticky="w")

# Convertir
def start_conversion():
    input_file = source_entry.get()
    output_folder = output_folder_entry.get()
    output_name = output_name_entry.get()
    if not input_file or not output_folder or not output_name:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        return
    try:
        sample_rate = int(sample_entry.get())
        volume = float(volume_entry.get())
        highpass = float(highpass_entry.get())
        corruption = int(corruption_slider.get())
        glitch = int(glitch_slider.get())
    except ValueError:
        messagebox.showerror("Erreur", "Vérifie que les valeurs sont valides.")
        return
    convert_to_raw(input_file, output_folder, output_name, sample_rate, volume, highpass, corruption, glitch)

tk.Button(root, text="Convertir", command=start_conversion, bg="lightgreen").grid(row=8, column=1, pady=15)

root.mainloop()