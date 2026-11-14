import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps, ImageTk
import os
import sys
# import numpy as np

class PNGToGCodeConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PNG to G-Code Converter - Anycubic i3 Mega S")
        self.root.geometry("800x900")
        self.root.resizable(False, False)
        
        # Dark theme colors
        self.bg_color = "#1e1e1e"
        self.secondary_bg = "#2d2d2d"
        self.accent_color = "#404040"
        self.text_color = "#ffffff"
        self.secondary_text = "#b0b0b0"
        self.success_color = "#4caf50"
        self.error_color = "#f44336"
        self.warning_color = "#ff9800"
        self.primary_color = "#2196f3"
        
        # Configure root
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.input_file = ""
        self.output_file = ""
        self.original_image = None
        self.preview_image = None
        self.processed_image = None
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for dark theme
        style.configure('Dark.TFrame', background=self.bg_color, relief='flat')
        style.configure('Card.TFrame', background=self.secondary_bg, relief='flat', borderwidth=1)
        style.configure('Dark.TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('Card.TLabel', background=self.secondary_bg, foreground=self.text_color)
        style.configure('Secondary.TLabel', background=self.secondary_bg, foreground=self.secondary_text)
        style.configure('Success.TLabel', background=self.bg_color, foreground=self.success_color)
        style.configure('Error.TLabel', background=self.bg_color, foreground=self.error_color)
        style.configure('Warning.TLabel', background=self.bg_color, foreground=self.warning_color)
        
        style.configure('Dark.TButton', 
                       background=self.primary_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat')
        style.map('Dark.TButton',
                 background=[('active', '#1976d2'), ('pressed', '#0d47a1')])
        
        style.configure('Secondary.TButton',
                       background=self.accent_color,
                       foreground=self.text_color,
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat')
        style.map('Secondary.TButton',
                 background=[('active', '#505050'), ('pressed', '#303030')])
        
        style.configure('Dark.TEntry',
                       background=self.accent_color,
                       foreground=self.text_color,
                       borderwidth=0,
                       insertcolor=self.text_color,
                       relief='flat')
        style.map('Dark.TEntry',
                 focuscolor=[('!focus', self.accent_color)])
        
        style.configure('Dark.TCombobox',
                       background=self.accent_color,
                       foreground=self.text_color,
                       borderwidth=0,
                       arrowcolor=self.text_color,
                       relief='flat')
        
        style.configure('Dark.TCheckbutton',
                       background=self.secondary_bg,
                       foreground=self.text_color,
                       focuscolor='none')
        
        style.configure('Dark.TScale',
                       background=self.secondary_bg,
                       troughcolor=self.accent_color,
                       slidercolor=self.primary_color,
                       borderwidth=0)
        
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.primary_color,
                       troughcolor=self.accent_color,
                       borderwidth=0,
                       relief='flat')
        
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_container, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="PNG to G-Code Converter", 
                              font=("Segoe UI", 18, "bold"),
                              bg=self.bg_color, fg=self.text_color)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Anycubic i3 Mega S Pen Plotter Mode", 
                                 font=("Segoe UI", 10),
                                 bg=self.bg_color, fg=self.secondary_text)
        subtitle_label.pack()
        
        # Create scrollable frame
        canvas = tk.Canvas(main_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # File selection card
        self.create_file_card(scrollable_frame)
        
        # Preview card
        self.create_preview_card(scrollable_frame)
        
        # Settings cards
        self.create_size_card(scrollable_frame)
        self.create_quality_card(scrollable_frame)
        self.create_speed_card(scrollable_frame)
        self.create_image_options_card(scrollable_frame)
        self.create_printer_card(scrollable_frame)
        
        # Convert button
        self.create_convert_section(scrollable_frame)
        
        # Footer
        self.create_footer(scrollable_frame)
        
        # Pack scrollable area
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind aspect ratio
        self.width_var.trace('w', self.on_width_change)
        self.height_var.trace('w', self.on_height_change)
        
    def create_card(self, parent, title, pady=(0, 15)):
        card_frame = tk.Frame(parent, bg=self.secondary_bg, relief='flat', bd=1)
        card_frame.pack(fill=tk.X, pady=pady)
        
        # Add rounded corners effect with padding
        content_frame = tk.Frame(card_frame, bg=self.secondary_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        if title:
            title_label = tk.Label(content_frame, text=title, 
                                  font=("Segoe UI", 12, "bold"),
                                  bg=self.secondary_bg, fg=self.text_color)
            title_label.pack(anchor=tk.W, pady=(0, 10))
        
        return content_frame
    
    def create_file_card(self, parent):
        content = self.create_card(parent, "File Selection")
        
        # Input file
        input_frame = tk.Frame(content, bg=self.secondary_bg)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_label = tk.Label(input_frame, text="PNG File:", 
                              font=("Segoe UI", 9),
                              bg=self.secondary_bg, fg=self.text_color)
        input_label.pack(anchor=tk.W)
        
        file_select_frame = tk.Frame(input_frame, bg=self.secondary_bg)
        file_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_label = tk.Label(file_select_frame, text="No file selected", 
                                   font=("Segoe UI", 9),
                                   bg=self.secondary_bg, fg=self.secondary_text)
        self.input_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(file_select_frame, text="Browse...", 
                              command=self.select_input_file,
                              bg=self.accent_color, fg=self.text_color,
                              font=("Segoe UI", 9), bd=0, relief='flat',
                              padx=20, pady=5)
        browse_btn.pack(side=tk.RIGHT)
        
        # Output file
        output_frame = tk.Frame(content, bg=self.secondary_bg)
        output_frame.pack(fill=tk.X)
        
        output_label = tk.Label(output_frame, text="G-Code Output:", 
                               font=("Segoe UI", 9),
                               bg=self.secondary_bg, fg=self.text_color)
        output_label.pack(anchor=tk.W)
        
        self.output_label = tk.Label(output_frame, text="Will be generated automatically", 
                                    font=("Segoe UI", 9),
                                    bg=self.secondary_bg, fg=self.secondary_text)
        self.output_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_preview_card(self, parent):
        content = self.create_card(parent, "Preview")
        
        # Preview canvas
        preview_frame = tk.Frame(content, bg=self.accent_color, relief='flat', bd=1)
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_canvas = tk.Canvas(preview_frame, width=200, height=200, 
                                       bg=self.accent_color, highlightthickness=0)
        self.preview_canvas.pack(padx=10, pady=10)
        
        # Preview controls
        controls_frame = tk.Frame(content, bg=self.secondary_bg)
        controls_frame.pack(fill=tk.X)
        
        refresh_btn = tk.Button(controls_frame, text="Refresh Preview", 
                               command=self.update_preview,
                               bg=self.accent_color, fg=self.text_color,
                               font=("Segoe UI", 9), bd=0, relief='flat',
                               padx=15, pady=5)
        refresh_btn.pack(side=tk.LEFT)
        
        self.preview_info = tk.Label(controls_frame, text="Select an image to see preview", 
                                    font=("Segoe UI", 9),
                                    bg=self.secondary_bg, fg=self.secondary_text)
        self.preview_info.pack(side=tk.RIGHT)
    
    def create_size_card(self, parent):
        content = self.create_card(parent, "Image Size (mm)")
        
        size_frame = tk.Frame(content, bg=self.secondary_bg)
        size_frame.pack(fill=tk.X)
        
        # Width
        width_frame = tk.Frame(size_frame, bg=self.secondary_bg)
        width_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(width_frame, text="Width:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        width_input_frame = tk.Frame(width_frame, bg=self.secondary_bg)
        width_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.width_var = tk.StringVar(value="180")
        width_entry = tk.Entry(width_input_frame, textvariable=self.width_var, 
                              bg=self.accent_color, fg=self.text_color,
                              font=("Segoe UI", 9), bd=0, relief='flat')
        width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(width_input_frame, text="mm", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Height
        height_frame = tk.Frame(size_frame, bg=self.secondary_bg)
        height_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(height_frame, text="Height:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        height_input_frame = tk.Frame(height_frame, bg=self.secondary_bg)
        height_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.height_var = tk.StringVar(value="180")
        height_entry = tk.Entry(height_input_frame, textvariable=self.height_var, 
                               bg=self.accent_color, fg=self.text_color,
                               font=("Segoe UI", 9), bd=0, relief='flat')
        height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(height_input_frame, text="mm", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Keep aspect ratio
        self.keep_aspect_var = tk.BooleanVar(value=True)
        aspect_check = tk.Checkbutton(content, text="Keep aspect ratio", 
                                     variable=self.keep_aspect_var,
                                     command=self.on_aspect_change,
                                     bg=self.secondary_bg, fg=self.text_color,
                                     font=("Segoe UI", 9), bd=0,
                                     selectcolor=self.accent_color,
                                     activebackground=self.secondary_bg,
                                     activeforeground=self.text_color)
        aspect_check.pack(anchor=tk.W, pady=(15, 0))
    
    def create_quality_card(self, parent):
        content = self.create_card(parent, "Quality & Resolution")
        
        quality_frame = tk.Frame(content, bg=self.secondary_bg)
        quality_frame.pack(fill=tk.X)
        
        # Quality preset
        quality_preset_frame = tk.Frame(quality_frame, bg=self.secondary_bg)
        quality_preset_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(quality_preset_frame, text="Quality Preset:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        self.quality_var = tk.StringVar(value="Standard (1)")
        quality_combo = ttk.Combobox(quality_preset_frame, textvariable=self.quality_var,
                                    values=["Low (0.5)", "Standard (1)", "High (2)", "Very High (3)"],
                                    state="readonly", font=("Segoe UI", 9),
                                    style='Dark.TCombobox')
        quality_combo.pack(fill=tk.X, pady=(5, 0))
        quality_combo.bind("<<ComboboxSelected>>", self.on_quality_change)
        
        # Resolution
        resolution_frame = tk.Frame(quality_frame, bg=self.secondary_bg)
        resolution_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(resolution_frame, text="Pixels per mm:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        self.resolution_var = tk.StringVar(value="1")
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var,
                                       values=["0.2", "0.4", "0.6", "0.8","1.0", "1.2", "1.4", "1.6", "1.8", "2"],
                                       state="readonly", font=("Segoe UI", 9),
                                       style='Dark.TCombobox')
        resolution_combo.pack(fill=tk.X, pady=(5, 0))
    
    def create_speed_card(self, parent):
        content = self.create_card(parent, "Speed Settings (mm/s)")
        
        speed_frame = tk.Frame(content, bg=self.secondary_bg)
        speed_frame.pack(fill=tk.X)
        
        # Draw speed
        draw_frame = tk.Frame(speed_frame, bg=self.secondary_bg)
        draw_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(draw_frame, text="Draw Speed:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        draw_input_frame = tk.Frame(draw_frame, bg=self.secondary_bg)
        draw_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.draw_speed_var = tk.StringVar(value="33")  # 2000mm/min = 33mm/s
        draw_entry = tk.Entry(draw_input_frame, textvariable=self.draw_speed_var,
                             bg=self.accent_color, fg=self.text_color,
                             font=("Segoe UI", 9), bd=0, relief='flat')
        draw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(draw_input_frame, text="mm/s", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Travel speed
        travel_frame = tk.Frame(speed_frame, bg=self.secondary_bg)
        travel_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(travel_frame, text="Travel Speed:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        travel_input_frame = tk.Frame(travel_frame, bg=self.secondary_bg)
        travel_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.travel_speed_var = tk.StringVar(value="200")  # Minimum 200mm/s
        travel_entry = tk.Entry(travel_input_frame, textvariable=self.travel_speed_var,
                               bg=self.accent_color, fg=self.text_color,
                               font=("Segoe UI", 9), bd=0, relief='flat')
        travel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(travel_input_frame, text="mm/s", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_image_options_card(self, parent):
        content = self.create_card(parent, "Image Options")
        
        # Invert colors
        self.invert_var = tk.BooleanVar(value=False)
        invert_check = tk.Checkbutton(content, text="Invert colors (Black ↔ White)", 
                                     variable=self.invert_var,
                                     command=self.update_preview,
                                     bg=self.secondary_bg, fg=self.text_color,
                                     font=("Segoe UI", 9), bd=0,
                                     selectcolor=self.accent_color,
                                     activebackground=self.secondary_bg,
                                     activeforeground=self.text_color)
        invert_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Threshold
        threshold_frame = tk.Frame(content, bg=self.secondary_bg)
        threshold_frame.pack(fill=tk.X)
        
        tk.Label(threshold_frame, text="Threshold:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        threshold_control_frame = tk.Frame(threshold_frame, bg=self.secondary_bg)
        threshold_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.threshold_var = tk.IntVar(value=128)
        threshold_scale = tk.Scale(threshold_control_frame, from_=0, to=255, 
                                  variable=self.threshold_var, orient="horizontal",
                                  bg=self.secondary_bg, fg=self.text_color,
                                  activebackground=self.primary_color,
                                  troughcolor=self.accent_color,
                                  font=("Segoe UI", 9), bd=0,
                                  command=self.update_threshold_label)
        threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.threshold_label = tk.Label(threshold_control_frame, text="128", 
                                       font=("Segoe UI", 9),
                                       bg=self.secondary_bg, fg=self.text_color,
                                       width=4)
        self.threshold_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_printer_card(self, parent):
        content = self.create_card(parent, "Printer Settings")
        
        # Printer info
        info_frame = tk.Frame(content, bg=self.secondary_bg)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(info_frame, text="Printer: Anycubic i3 Mega S", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        tk.Label(info_frame, text="Mode: Pen Plotter", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(anchor=tk.W)
        
        # Pen heights
        pen_frame = tk.Frame(content, bg=self.secondary_bg)
        pen_frame.pack(fill=tk.X)
        
        # Pen down
        pen_down_frame = tk.Frame(pen_frame, bg=self.secondary_bg)
        pen_down_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(pen_down_frame, text="Pen Down Height:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        pen_down_input_frame = tk.Frame(pen_down_frame, bg=self.secondary_bg)
        pen_down_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.pen_down_var = tk.StringVar(value="0.5")
        pen_down_entry = tk.Entry(pen_down_input_frame, textvariable=self.pen_down_var,
                                 bg=self.accent_color, fg=self.text_color,
                                 font=("Segoe UI", 9), bd=0, relief='flat')
        pen_down_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(pen_down_input_frame, text="mm", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Pen up
        pen_up_frame = tk.Frame(pen_frame, bg=self.secondary_bg)
        pen_up_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(pen_up_frame, text="Pen Up Height:", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor=tk.W)
        
        pen_up_input_frame = tk.Frame(pen_up_frame, bg=self.secondary_bg)
        pen_up_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.pen_up_var = tk.StringVar(value="5")
        pen_up_entry = tk.Entry(pen_up_input_frame, textvariable=self.pen_up_var,
                               bg=self.accent_color, fg=self.text_color,
                               font=("Segoe UI", 9), bd=0, relief='flat')
        pen_up_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        tk.Label(pen_up_input_frame, text="mm", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.secondary_text).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_convert_section(self, parent):
        convert_frame = tk.Frame(parent, bg=self.bg_color)
        convert_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Convert button
        self.convert_button = tk.Button(convert_frame, text="Convert to G-Code", 
                                       command=self.convert_to_gcode,
                                       bg=self.primary_color, fg="white",
                                       font=("Segoe UI", 12, "bold"), bd=0, relief='flat',
                                       padx=40, pady=15, state="disabled")
        self.convert_button.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(convert_frame, mode='indeterminate', 
                                       style='Dark.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        self.status_label = tk.Label(convert_frame, text="Ready", 
                                    font=("Segoe UI", 10),
                                    bg=self.bg_color, fg=self.success_color)
        self.status_label.pack()
    
    def create_footer(self, parent):
        footer_frame = tk.Frame(parent, bg=self.bg_color)
        footer_frame.pack(fill=tk.X, pady=(30, 0))
        
        footer_label = tk.Label(footer_frame, text="by HIGHVOLTAGEBEE", 
                               font=("Segoe UI", 8),
                               bg=self.bg_color, fg=self.secondary_text)
        footer_label.pack(side=tk.RIGHT)
    
    def on_quality_change(self, event=None):
        quality_map = {
            "Low (0.5)": "0.5",
            "Standard (1)": "1",
            "High (2)": "2",
            "Very High (3)": "3"
        }
        self.resolution_var.set(quality_map[self.quality_var.get()])
        self.update_preview()
    
    def update_threshold_label(self, value):
        self.threshold_label.config(text=str(int(float(value))))
        self.update_preview()
    
    def on_aspect_change(self):
        if self.keep_aspect_var.get() and self.original_image:
            self.maintain_aspect_ratio()
    
    def on_width_change(self, *args):
        if self.keep_aspect_var.get() and self.original_image:
            try:
                width = float(self.width_var.get())
                if width > 0:
                    aspect_ratio = self.original_image.width / self.original_image.height
                    new_height = width / aspect_ratio
                    self.height_var.set(str(round(new_height, 1)))
                    self.update_preview()
            except (ValueError, ZeroDivisionError):
                pass
    
    def on_height_change(self, *args):
        if self.keep_aspect_var.get() and self.original_image:
            try:
                height = float(self.height_var.get())
                if height > 0:
                    aspect_ratio = self.original_image.width / self.original_image.height
                    new_width = height * aspect_ratio
                    self.width_var.set(str(round(new_width, 1)))
                    self.update_preview()
            except (ValueError, ZeroDivisionError):
                pass
    
    def maintain_aspect_ratio(self):
        if self.original_image:
            try:
                width = float(self.width_var.get())
                aspect_ratio = self.original_image.width / self.original_image.height
                new_height = width / aspect_ratio
                self.height_var.set(str(round(new_height, 1)))
            except (ValueError, ZeroDivisionError):
                pass
    
    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select PNG File",
            filetypes=[("PNG Files", "*.png"), ("JPG Files", "*.jpg"), 
                      ("JPEG Files", "*.jpeg"), ("All Images", "*.png;*.jpg;*.jpeg")]
        )
        
        if file_path:
            self.input_file = file_path
            self.input_label.config(text=os.path.basename(file_path), fg=self.text_color)
            
            # Load image for aspect ratio
            try:
                self.original_image = Image.open(file_path)
                if self.keep_aspect_var.get():
                    self.maintain_aspect_ratio()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {str(e)}")
                return
            
            # Generate output file automatically
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_file = os.path.join(os.path.dirname(file_path), f"{base_name}_drawing.gcode")
            self.output_label.config(text=os.path.basename(self.output_file), fg=self.text_color)
            
            self.convert_button.config(state="normal")
    
    def update_preview(self):
        if not self.original_image:
            return
            
        try:
            # Process image like in conversion
            img = self.original_image.copy()
            img = img.convert('L')
            
            # Get parameters
            resolution = float(self.resolution_var.get())
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            threshold = int(self.threshold_var.get())
            
            # Calculate size
            pixel_width = int(width * resolution)
            pixel_height = int(height * resolution)
            
            # Resize
            img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
            
            # Invert if needed
            if self.invert_var.get():
                img = ImageOps.invert(img)
            
            # Apply threshold
            img = img.point(lambda x: 0 if x < threshold else 255, '1')
            
            # Scale for preview (max 180px)
            preview_size = 180
            if pixel_width > pixel_height:
                preview_width = preview_size
                preview_height = int(preview_size * pixel_height / pixel_width)
            else:
                preview_height = preview_size
                preview_width = int(preview_size * pixel_width / pixel_height)
            
            preview_img = img.resize((preview_width, preview_height), Image.Resampling.NEAREST)
            
            # Convert to PhotoImage
            self.preview_image = ImageTk.PhotoImage(preview_img)
            
            # Update canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.config(width=preview_width, height=preview_height)
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)
            
            # Update info
            black_pixels = np.sum(np.array(img) == 0)
            total_pixels = img.width * img.height
            coverage = (black_pixels / total_pixels) * 100
            
            self.preview_info.config(text=f"{pixel_width}×{pixel_height}px, {coverage:.1f}% coverage")
            
        except Exception as e:
            self.preview_info.config(text="Preview error")
    
    def convert_to_gcode(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select an image file.")
            return
        
        # Validate inputs
        try:
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            resolution = float(self.resolution_var.get())
            draw_speed = float(self.draw_speed_var.get())
            travel_speed = float(self.travel_speed_var.get())
            pen_down = float(self.pen_down_var.get())
            pen_up = float(self.pen_up_var.get())
            threshold = int(self.threshold_var.get())
            
            if width <= 0 or height <= 0 or resolution <= 0:
                raise ValueError("Size and resolution must be positive")
            if draw_speed <= 0 or travel_speed <= 0:
                raise ValueError("Speeds must be positive")
            if travel_speed < 200:
                raise ValueError("Travel speed must be at least 200 mm/s")
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return
        
        self.progress.start()
        self.status_label.config(text="Converting...", fg=self.warning_color)
        self.convert_button.config(state="disabled")
        
        try:
            # Load and process image
            img = Image.open(self.input_file)
            img = img.convert('L')
            
            # Calculate size (pixels = mm * resolution)
            pixel_width = int(width * resolution)
            pixel_height = int(height * resolution)
            
            # Resize image
            img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
            
            # Invert colors if needed
            if self.invert_var.get():
                img = ImageOps.invert(img)
            
            # Convert to black and white with threshold
            img = img.point(lambda x: 0 if x < threshold else 255, '1')
            
            # Generate G-Code
            self.generate_gcode(img, width, height, resolution, draw_speed, travel_speed, pen_down, pen_up)
            
            self.progress.stop()
            self.status_label.config(text="Successfully converted!", fg=self.success_color)
            self.convert_button.config(state="normal")
            
            # Show statistics
            stats = f"G-Code created!\n\n"
            stats += f"Image size: {width}mm × {height}mm\n"
            stats += f"Resolution: {pixel_width} × {pixel_height} pixels\n"
            stats += f"Pixels per mm: {resolution}\n"
            stats += f"Draw speed: {draw_speed} mm/s\n"
            stats += f"Travel speed: {travel_speed} mm/s\n"
            stats += f"File: {self.output_file}"
            
            messagebox.showinfo("Success", stats)
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Error during conversion", fg=self.error_color)
            self.convert_button.config(state="normal")
            messagebox.showerror("Error", f"Error during conversion: {str(e)}")
    
    def generate_gcode(self, img, width, height, resolution, draw_speed, travel_speed, pen_down, pen_up):
        img_width, img_height = img.size
        
        # Convert speeds from mm/s to mm/min for G-Code
        draw_speed_min = int(draw_speed * 60)
        travel_speed_min = int(travel_speed * 60)
        
        with open(self.output_file, 'w') as f:
            # G-Code Header
            f.write("; G-Code for Anycubic i3 Mega S - Pen Mode\n")
            f.write("; Generated by PNG to G-Code Converter\n")
            f.write(f"; Original file: {os.path.basename(self.input_file)}\n")
            f.write(f"; Image size: {width}mm × {height}mm\n")
            f.write(f"; Resolution: {img_width} × {img_height} pixels ({resolution} pixels/mm)\n")
            f.write(f"; Draw speed: {draw_speed} mm/s ({draw_speed_min} mm/min)\n")
            f.write(f"; Travel speed: {travel_speed} mm/s ({travel_speed_min} mm/min)\n")
            f.write(f"; Pen down: {pen_down}mm, pen up: {pen_up}mm\n")
            f.write(f"; Colors inverted: {'Yes' if self.invert_var.get() else 'No'}\n")
            f.write(f"; Threshold: {self.threshold_var.get()}\n")
            f.write(";\n")
            
            # Initialization
            f.write("G21 ; Set units to millimeters\n")
            f.write("G90 ; Absolute positioning\n")
            f.write("M82 ; Extruder absolute positioning\n")
            f.write("G28 ; Home all axes\n")
            f.write(f"G1 Z{pen_up} F3000 ; Raise pen\n")
            f.write("G1 X10 Y10 F3000 ; Move to start position\n")
            f.write("G92 E0 ; Reset extruder\n")
            f.write("\n")
            
            # Process image
            pen_down_state = False
            pixel_size = 1.0 / resolution  # mm per pixel
            
            for y in range(img_height):
                # Alternate directions for efficient plotting
                if y % 2 == 0:
                    x_range = range(img_width)
                else:
                    x_range = range(img_width-1, -1, -1)
                
                for x in x_range:
                    pixel = img.getpixel((x, y))
                    
                    # Convert coordinates
                    real_x = 10 + (x * pixel_size)  # 10mm offset
                    real_y = 10 + (y * pixel_size)  # 10mm offset
                    
                    if pixel == 0:  # Black pixel = draw
                        if not pen_down_state:
                            f.write(f"G1 Z{pen_down} F1000 ; Lower pen\n")
                            pen_down_state = True
                        f.write(f"G1 X{real_x:.2f} Y{real_y:.2f} F{draw_speed_min}\n")
                    else:  # White pixel = don't draw
                        if pen_down_state:
                            f.write(f"G1 Z{pen_up} F3000 ; Raise pen\n")
                            pen_down_state = False
                        f.write(f"G1 X{real_x:.2f} Y{real_y:.2f} F{travel_speed_min}\n")
            
            # Finish
            f.write("\n")
            f.write(f"G1 Z{pen_up * 2} F3000 ; Raise pen high\n")
            f.write("G28 X Y ; Home X and Y\n")
            f.write("M84 ; Disable motors\n")
            f.write("; End of G-Code\n")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Check if PIL/Pillow is installed
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("PIL/Pillow or NumPy is not installed!")
        print("Install with: pip install Pillow numpy")
        input("Press Enter to exit...")
        sys.exit(1)
    
    app = PNGToGCodeConverter()
    app.run()