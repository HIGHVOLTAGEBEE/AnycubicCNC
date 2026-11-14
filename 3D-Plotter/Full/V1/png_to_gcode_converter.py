import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps
import os
import sys

class PNGToGCodeConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PNG zu G-Code Konverter - Anycubic i3 Mega S")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Variablen
        self.input_file = ""
        self.output_file = ""
        
        self.create_widgets()
        
    def create_widgets(self):
        # Hauptframe mit Scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(main_frame, text="PNG zu G-Code Konverter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Datei-Bereich
        file_frame = ttk.LabelFrame(main_frame, text="Datei-Auswahl", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(file_frame, text="PNG-Datei:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_label = ttk.Label(file_frame, text="Keine Datei ausgewählt", 
                                    foreground="gray")
        self.input_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(file_frame, text="Durchsuchen...", 
                  command=self.select_input_file).grid(row=1, column=1, sticky=tk.E, pady=5, padx=(10, 0))
        
        ttk.Label(file_frame, text="G-Code Ausgabe:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_label = ttk.Label(file_frame, text="Wird automatisch generiert", 
                                     foreground="gray")
        self.output_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Bildgröße-Einstellungen
        size_frame = ttk.LabelFrame(main_frame, text="Bildgröße (mm)", padding="10")
        size_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(size_frame, text="Breite:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="180")
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=0, column=1, padx=(5, 10), pady=5)
        ttk.Label(size_frame, text="mm").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        ttk.Label(size_frame, text="Höhe:").grid(row=0, column=3, sticky=tk.W, pady=5, padx=(20, 0))
        self.height_var = tk.StringVar(value="180")
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=0, column=4, padx=(5, 10), pady=5)
        ttk.Label(size_frame, text="mm").grid(row=0, column=5, sticky=tk.W, pady=5)
        
        # Checkbox für Seitenverhältnis beibehalten
        self.keep_aspect_var = tk.BooleanVar(value=True)
        self.keep_aspect_check = ttk.Checkbutton(size_frame, text="Seitenverhältnis beibehalten", 
                                                variable=self.keep_aspect_var,
                                                command=self.on_aspect_change)
        self.keep_aspect_check.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(10, 0))
        
        # Auflösung-Einstellungen
        resolution_frame = ttk.LabelFrame(main_frame, text="Auflösung", padding="10")
        resolution_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(resolution_frame, text="Pixel pro mm:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.resolution_var = tk.StringVar(value="1")
        self.resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, 
                                           values=["0.5", "1", "2", "3", "4", "5"], 
                                           state="readonly", width=10)
        self.resolution_combo.grid(row=0, column=1, padx=(5, 10), pady=5)
        self.resolution_combo.set("1")
        
        ttk.Label(resolution_frame, text="Qualität:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.quality_var = tk.StringVar(value="Standard")
        self.quality_combo = ttk.Combobox(resolution_frame, textvariable=self.quality_var,
                                         values=["Niedrig (0.5)", "Standard (1)", "Hoch (2)", "Sehr hoch (3)"],
                                         state="readonly", width=15)
        self.quality_combo.grid(row=0, column=3, padx=(5, 0), pady=5)
        self.quality_combo.set("Standard (1)")
        self.quality_combo.bind("<<ComboboxSelected>>", self.on_quality_change)
        
        # Geschwindigkeit-Einstellungen
        speed_frame = ttk.LabelFrame(main_frame, text="Geschwindigkeit (mm/min)", padding="10")
        speed_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(speed_frame, text="Zeichengeschwindigkeit:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.draw_speed_var = tk.StringVar(value="2000")
        self.draw_speed_entry = ttk.Entry(speed_frame, textvariable=self.draw_speed_var, width=10)
        self.draw_speed_entry.grid(row=0, column=1, padx=(5, 10), pady=5)
        ttk.Label(speed_frame, text="mm/min").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        ttk.Label(speed_frame, text="Fahrgeschwindigkeit:").grid(row=0, column=3, sticky=tk.W, pady=5, padx=(20, 0))
        self.travel_speed_var = tk.StringVar(value="3000")
        self.travel_speed_entry = ttk.Entry(speed_frame, textvariable=self.travel_speed_var, width=10)
        self.travel_speed_entry.grid(row=0, column=4, padx=(5, 10), pady=5)
        ttk.Label(speed_frame, text="mm/min").grid(row=0, column=5, sticky=tk.W, pady=5)
        
        # Bild-Optionen
        image_frame = ttk.LabelFrame(main_frame, text="Bild-Optionen", padding="10")
        image_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.invert_var = tk.BooleanVar(value=False)
        self.invert_check = ttk.Checkbutton(image_frame, text="Farben invertieren (Schwarz ↔ Weiß)", 
                                           variable=self.invert_var)
        self.invert_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(image_frame, text="Schwellenwert:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.threshold_var = tk.IntVar(value=128)
        self.threshold_scale = ttk.Scale(image_frame, from_=0, to=255, variable=self.threshold_var, 
                                        orient="horizontal", length=200)
        self.threshold_scale.grid(row=1, column=1, padx=(5, 10), pady=5)
        self.threshold_label = ttk.Label(image_frame, text="128")
        self.threshold_label.grid(row=1, column=2, sticky=tk.W, pady=5)
        self.threshold_scale.configure(command=self.update_threshold_label)
        
        # Drucker-Einstellungen
        printer_frame = ttk.LabelFrame(main_frame, text="Drucker-Einstellungen", padding="10")
        printer_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(printer_frame, text="Drucker: Anycubic i3 Mega S").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(printer_frame, text="Modus: Stift-Plotter").grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(printer_frame, text="Stift-Höhe (abgesenkt):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pen_down_var = tk.StringVar(value="0.5")
        self.pen_down_entry = ttk.Entry(printer_frame, textvariable=self.pen_down_var, width=10)
        self.pen_down_entry.grid(row=2, column=1, padx=(5, 10), pady=5)
        ttk.Label(printer_frame, text="mm").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        ttk.Label(printer_frame, text="Stift-Höhe (angehoben):").grid(row=2, column=3, sticky=tk.W, pady=5, padx=(20, 0))
        self.pen_up_var = tk.StringVar(value="5")
        self.pen_up_entry = ttk.Entry(printer_frame, textvariable=self.pen_up_var, width=10)
        self.pen_up_entry.grid(row=2, column=4, padx=(5, 10), pady=5)
        ttk.Label(printer_frame, text="mm").grid(row=2, column=5, sticky=tk.W, pady=5)
        
        # Konvertieren Button
        self.convert_button = ttk.Button(main_frame, text="Zu G-Code konvertieren", 
                                        command=self.convert_to_gcode, state="disabled")
        self.convert_button.grid(row=7, column=0, columnspan=3, pady=20)
        
        # Fortschrittsbalken
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Bereit", foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Scrollbar konfigurieren
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind width/height entries for aspect ratio
        self.width_var.trace('w', self.on_width_change)
        self.height_var.trace('w', self.on_height_change)
        
    def on_quality_change(self, event=None):
        quality_map = {
            "Niedrig (0.5)": "0.5",
            "Standard (1)": "1",
            "Hoch (2)": "2",
            "Sehr hoch (3)": "3"
        }
        self.resolution_var.set(quality_map[self.quality_var.get()])
        
    def update_threshold_label(self, value):
        self.threshold_label.config(text=str(int(float(value))))
        
    def on_aspect_change(self):
        if self.keep_aspect_var.get() and hasattr(self, 'original_image'):
            self.maintain_aspect_ratio()
            
    def on_width_change(self, *args):
        if self.keep_aspect_var.get() and hasattr(self, 'original_image'):
            try:
                width = float(self.width_var.get())
                if width > 0:
                    aspect_ratio = self.original_image.width / self.original_image.height
                    new_height = width / aspect_ratio
                    self.height_var.set(str(round(new_height, 1)))
            except (ValueError, ZeroDivisionError):
                pass
                
    def on_height_change(self, *args):
        if self.keep_aspect_var.get() and hasattr(self, 'original_image'):
            try:
                height = float(self.height_var.get())
                if height > 0:
                    aspect_ratio = self.original_image.width / self.original_image.height
                    new_width = height * aspect_ratio
                    self.width_var.set(str(round(new_width, 1)))
            except (ValueError, ZeroDivisionError):
                pass
                
    def maintain_aspect_ratio(self):
        if hasattr(self, 'original_image'):
            try:
                width = float(self.width_var.get())
                aspect_ratio = self.original_image.width / self.original_image.height
                new_height = width / aspect_ratio
                self.height_var.set(str(round(new_height, 1)))
            except (ValueError, ZeroDivisionError):
                pass
        
    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="PNG-Datei auswählen",
            filetypes=[("PNG-Dateien", "*.png"), ("JPG-Dateien", "*.jpg"), ("JPEG-Dateien", "*.jpeg"), ("Alle Bilder", "*.png;*.jpg;*.jpeg")]
        )
        
        if file_path:
            self.input_file = file_path
            self.input_label.config(text=os.path.basename(file_path), foreground="black")
            
            # Bild laden für Seitenverhältnis
            try:
                self.original_image = Image.open(file_path)
                if self.keep_aspect_var.get():
                    self.maintain_aspect_ratio()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes: {str(e)}")
                return
            
            # Ausgabedatei automatisch generieren
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_file = os.path.join(os.path.dirname(file_path), f"{base_name}_drawing.gcode")
            self.output_label.config(text=os.path.basename(self.output_file), foreground="black")
            
            self.convert_button.config(state="normal")
            
    def convert_to_gcode(self):
        if not self.input_file:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Bilddatei aus.")
            return
            
        # Eingaben validieren
        try:
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            resolution = float(self.resolution_var.get())
            draw_speed = int(self.draw_speed_var.get())
            travel_speed = int(self.travel_speed_var.get())
            pen_down = float(self.pen_down_var.get())
            pen_up = float(self.pen_up_var.get())
            threshold = int(self.threshold_var.get())
            
            if width <= 0 or height <= 0 or resolution <= 0:
                raise ValueError("Größe und Auflösung müssen positiv sein")
            if draw_speed <= 0 or travel_speed <= 0:
                raise ValueError("Geschwindigkeiten müssen positiv sein")
                
        except ValueError as e:
            messagebox.showerror("Eingabefehler", f"Ungültige Eingabe: {str(e)}")
            return
            
        self.progress.start()
        self.status_label.config(text="Konvertiere...", foreground="orange")
        self.convert_button.config(state="disabled")
        
        try:
            # Bild laden und verarbeiten
            img = Image.open(self.input_file)
            
            # Zu Graustufen konvertieren
            img = img.convert('L')
            
            # Größe berechnen (Pixel = mm * Auflösung)
            pixel_width = int(width * resolution)
            pixel_height = int(height * resolution)
            
            # Bild skalieren
            img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
            
            # Farben invertieren falls gewünscht
            if self.invert_var.get():
                img = ImageOps.invert(img)
            
            # Zu Schwarz-Weiß konvertieren mit custom threshold
            img = img.point(lambda x: 0 if x < threshold else 255, '1')
            
            # G-Code generieren
            self.generate_gcode(img, width, height, resolution, draw_speed, travel_speed, pen_down, pen_up)
            
            self.progress.stop()
            self.status_label.config(text="Erfolgreich konvertiert!", foreground="green")
            self.convert_button.config(state="normal")
            
            # Statistiken anzeigen
            stats = f"G-Code erstellt!\n\n"
            stats += f"Bildgröße: {width}mm x {height}mm\n"
            stats += f"Auflösung: {pixel_width} x {pixel_height} Pixel\n"
            stats += f"Pixel pro mm: {resolution}\n"
            stats += f"Datei: {self.output_file}"
            
            messagebox.showinfo("Erfolg", stats)
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Fehler beim Konvertieren", foreground="red")
            self.convert_button.config(state="normal")
            messagebox.showerror("Fehler", f"Fehler beim Konvertieren: {str(e)}")
            
    def generate_gcode(self, img, width, height, resolution, draw_speed, travel_speed, pen_down, pen_up):
        img_width, img_height = img.size
        
        with open(self.output_file, 'w') as f:
            # G-Code Header
            f.write("; G-Code für Anycubic i3 Mega S - Stift-Modus\n")
            f.write("; Generiert von PNG zu G-Code Konverter\n")
            f.write(f"; Originaldatei: {os.path.basename(self.input_file)}\n")
            f.write(f"; Bildgröße: {width}mm x {height}mm\n")
            f.write(f"; Auflösung: {img_width} x {img_height} Pixel ({resolution} Pixel/mm)\n")
            f.write(f"; Zeichengeschwindigkeit: {draw_speed} mm/min\n")
            f.write(f"; Fahrgeschwindigkeit: {travel_speed} mm/min\n")
            f.write(f"; Stift abgesenkt: {pen_down}mm, angehoben: {pen_up}mm\n")
            f.write(f"; Farben invertiert: {'Ja' if self.invert_var.get() else 'Nein'}\n")
            f.write(";\n")
            
            # Initialisierung
            f.write("G21 ; Millimeter\n")
            f.write("G90 ; Absolute Positionierung\n")
            f.write("M82 ; Extruder absolute Positionierung\n")
            f.write("G28 ; Home all axes\n")
            f.write(f"G1 Z{pen_up} F3000 ; Stift anheben\n")
            f.write("G1 X10 Y10 F3000 ; Zur Startposition\n")
            f.write("G92 E0 ; Extruder Reset\n")
            f.write("\n")
            
            # Bild verarbeiten
            pen_down_state = False
            pixel_size = 1.0 / resolution  # mm pro Pixel
            
            for y in range(img_height):
                # Abwechselnde Richtungen für effizienten Druck
                if y % 2 == 0:
                    x_range = range(img_width)
                else:
                    x_range = range(img_width-1, -1, -1)
                    
                for x in x_range:
                    pixel = img.getpixel((x, y))
                    
                    # Koordinaten umrechnen
                    real_x = 10 + (x * pixel_size)  # 10mm Offset
                    real_y = 10 + (y * pixel_size)  # 10mm Offset
                    
                    if pixel == 0:  # Schwarzer Pixel = zeichnen
                        if not pen_down_state:
                            f.write(f"G1 Z{pen_down} F1000 ; Stift absenken\n")
                            pen_down_state = True
                        f.write(f"G1 X{real_x:.2f} Y{real_y:.2f} F{draw_speed}\n")
                    else:  # Weißer Pixel = nicht zeichnen
                        if pen_down_state:
                            f.write(f"G1 Z{pen_up} F3000 ; Stift anheben\n")
                            pen_down_state = False
                        f.write(f"G1 X{real_x:.2f} Y{real_y:.2f} F{travel_speed}\n")
            
            # Abschluss
            f.write("\n")
            f.write(f"G1 Z{pen_up * 2} F3000 ; Stift weit anheben\n")
            f.write("G28 X Y ; Home X und Y\n")
            f.write("M84 ; Motoren ausschalten\n")
            f.write("; Ende des G-Codes\n")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Prüfen ob PIL/Pillow installiert ist
    try:
        from PIL import Image
    except ImportError:
        print("PIL/Pillow ist nicht installiert!")
        print("Installieren Sie es mit: pip install Pillow")
        input("Drücken Sie Enter zum Beenden...")
        sys.exit(1)
    
    app = PNGToGCodeConverter()
    app.run()