import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np
import os

class RoundedFrame(tk.Frame):
    def __init__(self, parent, radius=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.radius = radius
        
class PlotterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Anycubic I3 Mega S Plotter")
        self.root.state('zoomed')
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        self.image_path = None
        self.processed_image = None
        self.preview_image = None
        self.max_width = 200
        self.max_height = 200
        self.max_depth = 180
        
        # Position and scaling variables
        self.start_x = 0
        self.start_y = 0
        self.current_width = 100
        self.current_height = 100
        self.aspect_ratio = 1.0
        self.maintain_aspect = True
        
        # Canvas variables for bed preview
        self.bed_canvas_width = 400
        self.bed_canvas_height = 400
        self.bed_scale = 2.0  # pixels per mm
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.image_rect = None
        
        self.setup_ui()
        
    def create_rounded_frame(self, parent, bg_color='#2d2d2d', border_color='#404040'):
        frame = tk.Frame(parent, bg=bg_color, relief=tk.FLAT, bd=0)
        frame.configure(highlightbackground=border_color, highlightcolor=border_color, highlightthickness=2)
        return frame
        
    def create_rounded_button(self, parent, text, command, bg_color='#3498db', fg_color='white', **kwargs):
        btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color,
                       font=('Arial', 11, 'bold'), relief=tk.FLAT, bd=0, cursor='hand2',
                       padx=20, pady=12, **kwargs)
        btn.configure(activebackground=self.lighten_color(bg_color), activeforeground=fg_color)
        return btn
        
    def lighten_color(self, color):
        color_map = {'#3498db': '#4fa8e0', '#27ae60': '#32c86f', '#e74c3c': '#eb6551', '#f39c12': '#f5a623'}
        return color_map.get(color, color)
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        scrollable_frame = tk.Frame(main_frame, bg='#1a1a1a')
        scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scrollable_frame, bg='#1a1a1a', highlightthickness=0)
        
        # Scrollbar deutlich vergrößert
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar", 
                       background='#404040',
                       troughcolor='#2d2d2d',
                       bordercolor='#404040',
                       arrowcolor='#ffffff',
                       darkcolor='#404040',
                       lightcolor='#404040',
                       width=30)
        
        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_content = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mausrad-Scrolling hinzufügen
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        content_frame = scrollable_content
        
        title_label = tk.Label(content_frame, text="Anycubic I3 Mega S Plotter", 
                              font=('Arial', 26, 'bold'), fg='#ffffff', bg='#1a1a1a')
        title_label.pack(pady=(0, 25))
        
        # Upload Section
        upload_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        upload_section.pack(fill=tk.X, pady=(0, 20))
        
        upload_header = tk.Label(upload_section, text="📁 Image Upload", 
                                font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        upload_header.pack(pady=(20, 15))
        
        upload_btn = self.create_rounded_button(upload_section, "Choose PNG File", self.upload_image, '#3498db')
        upload_btn.pack(pady=(0, 10))
        
        self.image_label = tk.Label(upload_section, text="No image selected", 
                                   fg='#888888', bg='#2d2d2d', font=('Arial', 10))
        self.image_label.pack(pady=(0, 20))
        
        # NEW: Position and Size Section
        position_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        position_section.pack(fill=tk.X, pady=(0, 20))
        
        pos_header = tk.Label(position_section, text="🎯 Position & Size", 
                             font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        pos_header.pack(pady=(20, 15))
        
        # Position controls
        pos_frame = tk.Frame(position_section, bg='#2d2d2d')
        pos_frame.pack(pady=(0, 10))
        
        tk.Label(pos_frame, text="Start X (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.start_x_var = tk.StringVar(value="0")
        self.start_x_var.trace('w', self.on_position_change)
        start_x_entry = tk.Entry(pos_frame, textvariable=self.start_x_var, width=12, font=('Arial', 11), 
                                bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        start_x_entry.grid(row=0, column=1, padx=(0, 30))
        
        tk.Label(pos_frame, text="Start Y (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.start_y_var = tk.StringVar(value="0")
        self.start_y_var.trace('w', self.on_position_change)
        start_y_entry = tk.Entry(pos_frame, textvariable=self.start_y_var, width=12, font=('Arial', 11),
                                bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        start_y_entry.grid(row=0, column=3)
        
        # Size controls with aspect ratio lock
        size_frame = tk.Frame(position_section, bg='#2d2d2d')
        size_frame.pack(pady=(10, 0))
        
        tk.Label(size_frame, text="Width (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.width_var = tk.StringVar(value="100")
        self.width_var.trace('w', self.on_width_change)
        width_entry = tk.Entry(size_frame, textvariable=self.width_var, width=12, font=('Arial', 11), 
                              bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        width_entry.grid(row=0, column=1, padx=(0, 30))
        
        tk.Label(size_frame, text="Height (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.height_var = tk.StringVar(value="100")
        self.height_var.trace('w', self.on_height_change)
        height_entry = tk.Entry(size_frame, textvariable=self.height_var, width=12, font=('Arial', 11),
                               bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        height_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Aspect ratio lock checkbox
        self.aspect_lock_var = tk.BooleanVar(value=True)
        aspect_check = tk.Checkbutton(size_frame, text="🔒 Lock Aspect", variable=self.aspect_lock_var, 
                                     fg='#ffffff', bg='#2d2d2d', selectcolor='#3498db', 
                                     activebackground='#2d2d2d', activeforeground='#ffffff',
                                     font=('Arial', 10), command=self.toggle_aspect_lock)
        aspect_check.grid(row=0, column=4, padx=(10, 0))
        
        # Bed preview canvas
        bed_frame = tk.Frame(position_section, bg='#2d2d2d')
        bed_frame.pack(pady=(15, 0))
        
        tk.Label(bed_frame, text="Printer Bed Preview (drag to position):", 
                fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).pack(pady=(0, 10))
        
        self.bed_canvas = tk.Canvas(bed_frame, width=self.bed_canvas_width, height=self.bed_canvas_height, 
                                   bg='#f0f0f0', relief=tk.FLAT, bd=2, highlightthickness=1, highlightbackground='#666666')
        self.bed_canvas.pack(pady=(0, 20))
        
        # Bind mouse events for dragging
        self.bed_canvas.bind("<Button-1>", self.on_bed_click)
        self.bed_canvas.bind("<B1-Motion>", self.on_bed_drag)
        self.bed_canvas.bind("<ButtonRelease-1>", self.on_bed_release)
        
        self.draw_bed_preview()
        
        limit_label = tk.Label(position_section, text=f"Max bed size: {self.max_width}x{self.max_height}mm", 
                              fg='#888888', bg='#2d2d2d', font=('Arial', 9))
        limit_label.pack(pady=(0, 20))
        
        # Quality Section
        quality_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        quality_section.pack(fill=tk.X, pady=(0, 20))
        
        quality_header = tk.Label(quality_section, text="⚙️ Quality Settings", 
                                 font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        quality_header.pack(pady=(20, 15))
        
        quality_frame = tk.Frame(quality_section, bg='#2d2d2d')
        quality_frame.pack(pady=(0, 10))
        
        tk.Label(quality_frame, text="Resolution:", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.resolution_var = tk.StringVar(value="Medium")
        resolution_combo = ttk.Combobox(quality_frame, textvariable=self.resolution_var, width=15,
                                       values=["Low", "Medium", "High", "Very High", "Extreme"], state="readonly")
        resolution_combo.grid(row=0, column=1, padx=(0, 30))
        
        tk.Label(quality_frame, text="Speed (mm/s):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.speed_var = tk.StringVar(value="250")
        speed_entry = tk.Entry(quality_frame, textvariable=self.speed_var, width=12, font=('Arial', 11),
                              bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        speed_entry.grid(row=0, column=3)
        
        options_row = tk.Frame(quality_section, bg='#2d2d2d')
        options_row.pack(pady=(5, 20))
        
        self.invert_var = tk.BooleanVar()
        invert_check = tk.Checkbutton(options_row, text="Invert Colors", variable=self.invert_var, 
                                     fg='#ffffff', bg='#2d2d2d', selectcolor='#3498db', 
                                     activebackground='#2d2d2d', activeforeground='#ffffff',
                                     font=('Arial', 11))
        invert_check.pack(side=tk.LEFT, padx=(0, 30))
        
        generate_btn = self.create_rounded_button(options_row, "🔄 GENERATE PREVIEW", self.generate_preview, '#27ae60')
        generate_btn.configure(font=('Arial', 13, 'bold'), padx=30, pady=15)
        generate_btn.pack(side=tk.RIGHT)
        
        # Pen Settings Section
        pen_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        pen_section.pack(fill=tk.X, pady=(0, 20))
        
        pen_header = tk.Label(pen_section, text="✏️ Pen Settings", 
                             font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        pen_header.pack(pady=(20, 15))
        
        pen_frame = tk.Frame(pen_section, bg='#2d2d2d')
        pen_frame.pack(pady=(0, 20))
        
        tk.Label(pen_frame, text="Pen Down (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.pen_down_var = tk.StringVar(value="0")
        pen_down_entry = tk.Entry(pen_frame, textvariable=self.pen_down_var, width=12, font=('Arial', 11),
                                 bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        pen_down_entry.grid(row=0, column=1, padx=(0, 30))
        
        tk.Label(pen_frame, text="Pen Up (mm):", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.pen_up_var = tk.StringVar(value="3.5")
        pen_up_entry = tk.Entry(pen_frame, textvariable=self.pen_up_var, width=12, font=('Arial', 11),
                               bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        pen_up_entry.grid(row=0, column=3)
        
        # Preview Section
        preview_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        preview_section.pack(fill=tk.X, pady=(0, 20))
        
        preview_header = tk.Label(preview_section, text="👁️ Preview", 
                                 font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        preview_header.pack(pady=(20, 15))
        
        self.preview_canvas = tk.Canvas(preview_section, width=500, height=500, bg='#ffffff', 
                                       relief=tk.FLAT, bd=0, highlightthickness=0)
        self.preview_canvas.pack(pady=(0, 20), expand=True)
        
        # Export Section
        export_section = self.create_rounded_frame(content_frame, '#2d2d2d', '#404040')
        export_section.pack(fill=tk.X, pady=(0, 20))
        
        export_header = tk.Label(export_section, text="💾 Export G-Code", 
                                font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2d2d2d')
        export_header.pack(pady=(20, 15))
        
        filename_frame = tk.Frame(export_section, bg='#2d2d2d')
        filename_frame.pack(pady=(0, 15))
        
        tk.Label(filename_frame, text="Filename:", fg='#ffffff', bg='#2d2d2d', font=('Arial', 11)).pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value="my_plot")
        filename_entry = tk.Entry(filename_frame, textvariable=self.filename_var, width=25, font=('Arial', 11),
                                 bg='#3a3a3a', fg='#ffffff', relief=tk.FLAT, bd=5)
        filename_entry.pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(filename_frame, text=".gcode", fg='#888888', bg='#2d2d2d', font=('Arial', 11)).pack(side=tk.LEFT)
        
        export_btn = self.create_rounded_button(export_section, "📤 EXPORT G-CODE FILE", self.export_gcode, '#e74c3c')
        export_btn.configure(font=('Arial', 14, 'bold'), padx=40, pady=18)
        export_btn.pack(pady=(0, 20))
        
        credit_label = tk.Label(content_frame, text="by HIGHVOLTAGEBEE", 
                               font=('Arial', 8), fg='#666666', bg='#1a1a1a')
        credit_label.pack(side=tk.BOTTOM, anchor=tk.SE, pady=(20, 0))
    
    def toggle_aspect_lock(self):
        self.maintain_aspect = self.aspect_lock_var.get()
        if self.maintain_aspect and self.image_path:
            self.calculate_aspect_ratio()
    
    def calculate_aspect_ratio(self):
        if not self.image_path:
            return
        try:
            img = Image.open(self.image_path)
            img_width, img_height = img.size
            self.aspect_ratio = img_width / img_height
        except:
            self.aspect_ratio = 1.0
    
    def on_width_change(self, *args):
        if self.maintain_aspect and not hasattr(self, '_updating_height'):
            try:
                self._updating_height = True
                width = float(self.width_var.get())
                height = width / self.aspect_ratio
                self.height_var.set(f"{height:.1f}")
                self.current_width = width
                self.current_height = height
                self.draw_bed_preview()
            except:
                pass
            finally:
                if hasattr(self, '_updating_height'):
                    delattr(self, '_updating_height')
    
    def on_height_change(self, *args):
        if self.maintain_aspect and not hasattr(self, '_updating_width'):
            try:
                self._updating_width = True
                height = float(self.height_var.get())
                width = height * self.aspect_ratio
                self.width_var.set(f"{width:.1f}")
                self.current_width = width
                self.current_height = height
                self.draw_bed_preview()
            except:
                pass
            finally:
                if hasattr(self, '_updating_width'):
                    delattr(self, '_updating_width')
    
    def on_position_change(self, *args):
        try:
            self.start_x = float(self.start_x_var.get())
            self.start_y = float(self.start_y_var.get())
            self.draw_bed_preview()
        except:
            pass
    
    def draw_bed_preview(self):
        self.bed_canvas.delete("all")
        
        # Draw bed outline
        bed_width_px = self.max_width * self.bed_scale
        bed_height_px = self.max_height * self.bed_scale
        
        # Center the bed in the canvas
        bed_x = (self.bed_canvas_width - bed_width_px) / 2
        bed_y = (self.bed_canvas_height - bed_height_px) / 2
        
        # Draw bed rectangle
        self.bed_canvas.create_rectangle(bed_x, bed_y, bed_x + bed_width_px, bed_y + bed_height_px, 
                                        outline='#333333', width=2, fill='#ffffff')
        
        # Draw grid lines
        for i in range(1, int(self.max_width // 20)):
            x = bed_x + i * 20 * self.bed_scale
            self.bed_canvas.create_line(x, bed_y, x, bed_y + bed_height_px, fill='#dddddd', width=1)
        
        for i in range(1, int(self.max_height // 20)):
            y = bed_y + i * 20 * self.bed_scale
            self.bed_canvas.create_line(bed_x, y, bed_x + bed_width_px, y, fill='#dddddd', width=1)
        
        # Draw origin marker
        origin_x = bed_x + self.start_x * self.bed_scale
        origin_y = bed_y + self.start_y * self.bed_scale
        self.bed_canvas.create_oval(origin_x - 3, origin_y - 3, origin_x + 3, origin_y + 3, 
                                   fill='#e74c3c', outline='#c0392b', width=2)
        
        # Draw image rectangle
        try:
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            
            img_x = bed_x + self.start_x * self.bed_scale
            img_y = bed_y + self.start_y * self.bed_scale
            img_width = width * self.bed_scale
            img_height = height * self.bed_scale
            
            # Check if image fits within bed
            if (self.start_x + width <= self.max_width and 
                self.start_y + height <= self.max_height and
                self.start_x >= 0 and self.start_y >= 0):
                color = '#27ae60'  # Green if fits
                alpha_fill = '#27ae6040'
            else:
                color = '#e74c3c'  # Red if doesn't fit
                alpha_fill = '#e74c3c40'
            
            self.image_rect = self.bed_canvas.create_rectangle(
                img_x, img_y, img_x + img_width, img_y + img_height,
                outline=color, width=2, fill=alpha_fill, stipple='gray50'
            )
            
            # Add dimension labels
            self.bed_canvas.create_text(img_x + img_width/2, img_y - 10, 
                                       text=f"{width:.1f}mm", fill='#333333', font=('Arial', 9))
            self.bed_canvas.create_text(img_x - 15, img_y + img_height/2, 
                                       text=f"{height:.1f}mm", fill='#333333', font=('Arial', 9), angle=90)
            
        except:
            pass
        
        # Add coordinate labels
        self.bed_canvas.create_text(bed_x - 10, bed_y - 10, text="(0,0)", fill='#666666', font=('Arial', 9))
        self.bed_canvas.create_text(bed_x + bed_width_px + 10, bed_y + bed_height_px + 10, 
                                   text=f"({self.max_width},{self.max_height})", fill='#666666', font=('Arial', 9))
    
    def on_bed_click(self, event):
        if self.image_rect:
            # Check if click is on the image rectangle
            coords = self.bed_canvas.coords(self.image_rect)
            if (coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]):
                self.is_dragging = True
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.bed_canvas.configure(cursor="fleur")
    
    def on_bed_drag(self, event):
        if self.is_dragging and self.image_rect:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            # Convert pixel movement to mm
            dx_mm = dx / self.bed_scale
            dy_mm = dy / self.bed_scale
            
            new_x = self.start_x + dx_mm
            new_y = self.start_y + dy_mm
            
            # Constrain to bed boundaries
            new_x = max(0, min(new_x, self.max_width - self.current_width))
            new_y = max(0, min(new_y, self.max_height - self.current_height))
            
            self.start_x_var.set(f"{new_x:.1f}")
            self.start_y_var.set(f"{new_y:.1f}")
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_bed_release(self, event):
        self.is_dragging = False
        self.bed_canvas.configure(cursor="")
        
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=f"✓ {os.path.basename(file_path)}", fg='#27ae60')
            self.auto_adjust_dimensions()
    
    def auto_adjust_dimensions(self):
        if not self.image_path:
            return
        
        try:
            img = Image.open(self.image_path)
            img_width, img_height = img.size
            
            self.aspect_ratio = img_width / img_height
            
            if self.aspect_ratio > 1:
                new_width = min(100, self.max_width)
                new_height = new_width / self.aspect_ratio
                if new_height > self.max_height:
                    new_height = self.max_height
                    new_width = new_height * self.aspect_ratio
            else:
                new_height = min(100, self.max_height)
                new_width = new_height * self.aspect_ratio
                if new_width > self.max_width:
                    new_width = self.max_width
                    new_height = new_width / self.aspect_ratio
            
            self.width_var.set(f"{new_width:.1f}")
            self.height_var.set(f"{new_height:.1f}")
            self.current_width = new_width
            self.current_height = new_height
            
            self.draw_bed_preview()
            
        except Exception as e:
            pass
    
    def get_resolution_pixels_per_mm(self):
        resolution_map = {"Low": 1, "Medium": 2, "High": 4, "Very High": 6, "Extreme": 8}
        return resolution_map[self.resolution_var.get()]
    
    def generate_preview(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return
        
        try:
            width_mm = float(self.width_var.get())
            height_mm = float(self.height_var.get())
            
            if width_mm > self.max_width or height_mm > self.max_height:
                messagebox.showerror("Error", f"Dimensions exceed printer limits!\nMax: {self.max_width}x{self.max_height}mm")
                return
            
            pixels_per_mm = self.get_resolution_pixels_per_mm()
            
            target_width = int(width_mm * pixels_per_mm)
            target_height = int(height_mm * pixels_per_mm)
            
            img = Image.open(self.image_path)
            img = img.convert('L')
            img = img.resize((target_width, target_height), Image.LANCZOS)
            
            if self.invert_var.get():
                img = ImageOps.invert(img)
            
            img_array = np.array(img)
            binary_array = (img_array > 128).astype(np.uint8) * 255
            self.processed_image = Image.fromarray(binary_array)
            
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
    
    def update_preview(self):
        if self.processed_image:
            preview_size = 500
            preview_img = self.processed_image.copy()
            preview_img.thumbnail((preview_size, preview_size), Image.LANCZOS)
            
            self.preview_image = ImageTk.PhotoImage(preview_img)
            self.preview_canvas.delete("all")
            
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            img_width = preview_img.width
            img_height = preview_img.height
            
            x = (canvas_width - img_width) // 2
            y = (canvas_height - img_height) // 2
            
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
    
    def export_gcode(self):
        if not self.processed_image:
            messagebox.showwarning("Warning", "Please generate a preview first!")
            return
        
        try:
            filename = self.filename_var.get()
            if not filename:
                filename = "my_plot"
            if not filename.endswith('.gcode'):
                filename += '.gcode'
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".gcode",
                filetypes=[("G-code files", "*.gcode")],
                initialfile=filename
            )
            
            if file_path:
                self.generate_gcode(file_path)
                messagebox.showinfo("Success", f"G-code exported successfully!\n{os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export G-code: {str(e)}")
    
    def generate_gcode(self, file_path):
        width_mm = float(self.width_var.get())
        height_mm = float(self.height_var.get())
        start_x_mm = float(self.start_x_var.get())
        start_y_mm = float(self.start_y_var.get())
        speed = float(self.speed_var.get()) * 60  # Convert mm/s to mm/min
        pen_down = float(self.pen_down_var.get())
        pen_up = float(self.pen_up_var.get())
        
        img_array = np.array(self.processed_image)
        height, width = img_array.shape
        
        x_scale = width_mm / width
        y_scale = height_mm / height
        
        with open(file_path, 'w') as f:
            # G-code header
            f.write("; Generated by Anycubic I3 Mega S Plotter\n")
            f.write("; Image dimensions: {:.1f}x{:.1f}mm\n".format(width_mm, height_mm))
            f.write("; Start position: X{:.1f} Y{:.1f}\n".format(start_x_mm, start_y_mm))
            f.write("; Resolution: {}x{} pixels\n".format(width, height))
            f.write("; Speed: {} mm/min\n".format(speed))
            f.write("\n")
            
            f.write("G21 ; Set units to millimeters\n")
            f.write("G90 ; Use absolute coordinates\n")
            f.write("G28 X Y ; Home X and Y axes\n")
            f.write(f"G1 Z{pen_up} F1000 ; Lift pen\n")
            f.write("G28 X Y ; Home again\n")
            f.write("M117 Starting plot...\n")
            f.write(f"G1 X{start_x_mm} Y{start_y_mm} F{speed} ; Move to start position\n")
            f.write("\n")
            
            pen_is_down = False
            
            for y in range(height):
                row = img_array[y, :]
                # Alternate direction for each row (boustrophedon)
                if y % 2 == 1:
                    row = row[::-1]
                
                for x in range(width):
                    if y % 2 == 1:
                        real_x = width - 1 - x
                    else:
                        real_x = x
                    
                    # Apply offset for start position
                    pixel_x = start_x_mm + real_x * x_scale
                    pixel_y = start_y_mm + y * y_scale
                    
                    # Black pixels (0) = pen down, white pixels (255) = pen up
                    if row[x] == 0:  # Black pixel - draw
                        if not pen_is_down:
                            f.write(f"G1 X{pixel_x:.3f} Y{pixel_y:.3f} F{speed}\n")
                            f.write(f"G1 Z{pen_down} F1000\n")
                            pen_is_down = True
                        else:
                            f.write(f"G1 X{pixel_x:.3f} Y{pixel_y:.3f} F{speed}\n")
                    else:  # White pixel - don't draw
                        if pen_is_down:
                            f.write(f"G1 Z{pen_up} F1000\n")
                            pen_is_down = False
                        f.write(f"G1 X{pixel_x:.3f} Y{pixel_y:.3f} F{speed}\n")
            
            # G-code footer
            f.write(f"\nG1 Z{pen_up} F1000 ; Final pen up\n")
            f.write("G1 Z150 F1000 ; Move Z to safe height\n")
            f.write("G1 Y200 F3000 ; Move bed forward\n")
            f.write("M117 Plot complete!\n")
            f.write("M84 ; Disable motors\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotterGUI(root)
    root.mainloop()