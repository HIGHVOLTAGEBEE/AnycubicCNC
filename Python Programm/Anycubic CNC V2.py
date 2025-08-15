import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import re
import math
import os

class SVGToCNCConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Anycubic CNC V2.1")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.settings = {
            'travel_speed': tk.DoubleVar(value=100),
            'feed_rate': tk.DoubleVar(value=5),
            'max_cutting_speed': tk.DoubleVar(value=10),
            'tool_diameter': tk.DoubleVar(value=2),
            'resolution': tk.DoubleVar(value=0.0001),
            'bed_zero_height': tk.DoubleVar(value=9.5),
            'material_height': tk.DoubleVar(value=3),
            'layer_depth': tk.DoubleVar(value=1),
            'bed_width': tk.DoubleVar(value=220),
            'bed_height': tk.DoubleVar(value=220),
            'margin': tk.DoubleVar(value=10),
            'safe_height': tk.DoubleVar(value=25)
        }
        
        self.svg_paths = []
        self.toolpaths = []
        self.offset_x = tk.DoubleVar(value=0)
        self.offset_y = tk.DoubleVar(value=0)
        self.scale_factor = tk.DoubleVar(value=1.0)
        self.gcode_lines = []
        self.svg_bounds = (0, 0, 0, 0)
        
        self.create_ui()
        
    def create_ui(self):

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        file_frame = ttk.LabelFrame(left_frame, text="Datei Hochladen")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="SVG laden", command=self.load_svg).pack(fill=tk.X, pady=5)
        
        settings_frame = ttk.LabelFrame(left_frame, text="Einstellungen")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_frame, text="Materialhöhe (mm):").pack(anchor=tk.W)
        ttk.Entry(settings_frame, textvariable=self.settings['material_height']).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(settings_frame, text="Tooldurchmesser (mm):").pack(anchor=tk.W)
        ttk.Entry(settings_frame, textvariable=self.settings['tool_diameter']).pack(fill=tk.X, pady=(0, 5))
        
        pos_frame = ttk.LabelFrame(left_frame, text="Position")
        pos_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pos_frame, text="X-Offset (mm):").pack(anchor=tk.W)
        ttk.Entry(pos_frame, textvariable=self.offset_x).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(pos_frame, text="Y-Offset (mm):").pack(anchor=tk.W)
        ttk.Entry(pos_frame, textvariable=self.offset_y).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(pos_frame, text="Skalierung:").pack(anchor=tk.W)
        ttk.Entry(pos_frame, textvariable=self.scale_factor).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(pos_frame, text="Auto-Skalierung", command=self.auto_scale).pack(fill=tk.X, pady=5)
        
        action_frame = ttk.LabelFrame(left_frame, text="Aktionen")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="Toolpath generieren", command=self.generate_toolpath).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="G-Code exportieren", command=self.export_gcode).pack(fill=tk.X, pady=2)
        
        info_frame = ttk.LabelFrame(left_frame, text="Info")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=10, width=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        canvas_frame = ttk.LabelFrame(right_frame, text="Vorschau")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.update_canvas()
        
    def load_svg(self):
        file_path = filedialog.askopenfilename(
            title="SVG Datei auswählen",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.parse_svg(file_path)
                self.calculate_bounds()
                self.auto_scale()
                self.update_canvas()
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"SVG geladen: {os.path.basename(file_path)}\n")
                self.info_text.insert(tk.END, f"Pfade gefunden: {len(self.svg_paths)}\n")
                self.info_text.insert(tk.END, f"Abmessungen: {self.svg_bounds[2]-self.svg_bounds[0]:.1f} x {self.svg_bounds[3]-self.svg_bounds[1]:.1f} mm\n")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der SVG: {e}")
                
    def parse_svg(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        self.svg_paths = []
        
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        for path in root.findall('.//svg:path', ns):
            d = path.get('d', '')
            if d:
                points = self.parse_path_d(d)
                if points:
                    self.svg_paths.append(points)
                    
        for line in root.findall('.//svg:line', ns):
            x1 = float(line.get('x1', 0))
            y1 = float(line.get('y1', 0))
            x2 = float(line.get('x2', 0))
            y2 = float(line.get('y2', 0))
            self.svg_paths.append([(x1, y1), (x2, y2)])
            
        for rect in root.findall('.//svg:rect', ns):
            x = float(rect.get('x', 0))
            y = float(rect.get('y', 0))
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            self.svg_paths.append([(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)])
            
        for circle in root.findall('.//svg:circle', ns):
            cx = float(circle.get('cx', 0))
            cy = float(circle.get('cy', 0))
            r = float(circle.get('r', 0))
            points = []
            for i in range(64):
                angle = 2 * math.pi * i / 64
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                points.append((x, y))
            points.append(points[0])
            self.svg_paths.append(points)
            
        for ellipse in root.findall('.//svg:ellipse', ns):
            cx = float(ellipse.get('cx', 0))
            cy = float(ellipse.get('cy', 0))
            rx = float(ellipse.get('rx', 0))
            ry = float(ellipse.get('ry', 0))
            points = []
            for i in range(64):
                angle = 2 * math.pi * i / 64
                x = cx + rx * math.cos(angle)
                y = cy + ry * math.sin(angle)
                points.append((x, y))
            points.append(points[0])
            self.svg_paths.append(points)
            
        for polyline in root.findall('.//svg:polyline', ns):
            points_str = polyline.get('points', '')
            if points_str:
                coords = re.findall(r'-?\d*\.?\d+', points_str)
                points = []
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        points.append((float(coords[i]), float(coords[i+1])))
                if points:
                    self.svg_paths.append(points)
                    
        for polygon in root.findall('.//svg:polygon', ns):
            points_str = polygon.get('points', '')
            if points_str:
                coords = re.findall(r'-?\d*\.?\d+', points_str)
                points = []
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        points.append((float(coords[i]), float(coords[i+1])))
                if points:
                    points.append(points[0])
                    self.svg_paths.append(points)
                    
    def parse_path_d(self, d):
        points = []
        commands = re.findall(r'[MmLlHhVvCcSsQqTtAaZz][^MmLlHhVvCcSsQqTtAaZz]*', d)
        
        current_x, current_y = 0, 0
        start_x, start_y = 0, 0
        
        for cmd in commands:
            cmd_type = cmd[0]
            coords = re.findall(r'-?\d*\.?\d+', cmd[1:])
            coords = [float(c) for c in coords]
            
            if cmd_type in 'Mm':
                if len(coords) >= 2:
                    if cmd_type == 'M':
                        current_x, current_y = coords[0], coords[1]
                    else:
                        current_x += coords[0]
                        current_y += coords[1]
                    start_x, start_y = current_x, current_y
                    points.append((current_x, current_y))
                    
                    for i in range(2, len(coords), 2):
                        if i + 1 < len(coords):
                            if cmd_type == 'M':
                                current_x, current_y = coords[i], coords[i+1]
                            else:
                                current_x += coords[i]
                                current_y += coords[i+1]
                            points.append((current_x, current_y))
                    
            elif cmd_type in 'Ll':
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        if cmd_type == 'L':
                            current_x, current_y = coords[i], coords[i+1]
                        else:
                            current_x += coords[i]
                            current_y += coords[i+1]
                        points.append((current_x, current_y))
                        
            elif cmd_type in 'Hh':
                for coord in coords:
                    if cmd_type == 'H':
                        current_x = coord
                    else:
                        current_x += coord
                    points.append((current_x, current_y))
                    
            elif cmd_type in 'Vv':
                for coord in coords:
                    if cmd_type == 'V':
                        current_y = coord
                    else:
                        current_y += coord
                    points.append((current_x, current_y))
                    
            elif cmd_type in 'Cc':
                for i in range(0, len(coords), 6):
                    if i + 5 < len(coords):
                        if cmd_type == 'C':
                            x1, y1 = coords[i], coords[i+1]
                            x2, y2 = coords[i+2], coords[i+3]
                            x3, y3 = coords[i+4], coords[i+5]
                        else:
                            x1, y1 = current_x + coords[i], current_y + coords[i+1]
                            x2, y2 = current_x + coords[i+2], current_y + coords[i+3]
                            x3, y3 = current_x + coords[i+4], current_y + coords[i+5]
                        
                        bezier_points = self.bezier_curve(current_x, current_y, x1, y1, x2, y2, x3, y3)
                        points.extend(bezier_points[1:])
                        current_x, current_y = x3, y3
                        
            elif cmd_type in 'Qq':
                for i in range(0, len(coords), 4):
                    if i + 3 < len(coords):
                        if cmd_type == 'Q':
                            x1, y1 = coords[i], coords[i+1]
                            x2, y2 = coords[i+2], coords[i+3]
                        else:
                            x1, y1 = current_x + coords[i], current_y + coords[i+1]
                            x2, y2 = current_x + coords[i+2], current_y + coords[i+3]
                        
                        quad_points = self.quadratic_curve(current_x, current_y, x1, y1, x2, y2)
                        points.extend(quad_points[1:])
                        current_x, current_y = x2, y2
                        
            elif cmd_type in 'Zz':
                if points and (current_x != start_x or current_y != start_y):
                    points.append((start_x, start_y))
                current_x, current_y = start_x, start_y
                
        return points
        
    def bezier_curve(self, x0, y0, x1, y1, x2, y2, x3, y3, steps=20):
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**3 * x0 + 3*(1-t)**2*t * x1 + 3*(1-t)*t**2 * x2 + t**3 * x3
            y = (1-t)**3 * y0 + 3*(1-t)**2*t * y1 + 3*(1-t)*t**2 * y2 + t**3 * y3
            points.append((x, y))
        return points
        
    def quadratic_curve(self, x0, y0, x1, y1, x2, y2, steps=15):
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**2 * x0 + 2*(1-t)*t * x1 + t**2 * x2
            y = (1-t)**2 * y0 + 2*(1-t)*t * y1 + t**2 * y2
            points.append((x, y))
        return points
        
    def calculate_bounds(self):
        if not self.svg_paths:
            self.svg_bounds = (0, 0, 0, 0)
            return
            
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for path in self.svg_paths:
            for x, y in path:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                
        self.svg_bounds = (min_x, min_y, max_x, max_y)
        
    def auto_scale(self):
        if not self.svg_paths:
            return
            
        min_x, min_y, max_x, max_y = self.svg_bounds
        svg_width = max_x - min_x
        svg_height = max_y - min_y
        
        if svg_width <= 0 or svg_height <= 0:
            return
            
        bed_width = self.settings['bed_width'].get()
        bed_height = self.settings['bed_height'].get()
        margin = self.settings['margin'].get()
        
        work_width = bed_width - 2 * margin
        work_height = bed_height - 2 * margin
        
        scale_x = work_width / svg_width
        scale_y = work_height / svg_height
        scale = round(min(scale_x, scale_y) * 0.9, 3)
        
        self.scale_factor.set(scale)
        
        scaled_width = svg_width * scale
        scaled_height = svg_height * scale
        
        center_x = (work_width - scaled_width) / 2
        center_y = (work_height - scaled_height) / 2
        
        self.offset_x.set(round(center_x - min_x * scale, 2))
        self.offset_y.set(round(center_x - min_x * scale, 2))
        
        self.update_canvas()

    def _is_closed(self, pts, tol=1e-6):
        if len(pts) < 3:
            return False
        return math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < tol

    def _unit(self, dx, dy):
        l = math.hypot(dx, dy)
        if l < 1e-12:
            return (0.0, 0.0)
        return (dx / l, dy / l)

    def _offset_path(self, pts, r):
        if r <= 0 or len(pts) < 2:
            return pts[:]
        closed = self._is_closed(pts)
        work = pts[:-1] if closed else pts[:]
        if len(work) < 2:
            return pts[:]
        if not closed:
            return pts[:]  # Offene Linien nicht verschieben

        side = -1.0  # -1 = rechts von Fahrtrichtung
        out = []
        n = len(work)
        for i in range(n):
            p_prev = work[(i - 1) % n]
            p_curr = work[i]
            p_next = work[(i + 1) % n]

            t1 = self._unit(p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
            t2 = self._unit(p_next[0] - p_curr[0], p_next[1] - p_curr[1])
            if t1 == (0.0, 0.0):
                t1 = t2
            if t2 == (0.0, 0.0):
                t2 = t1

            n1 = (-t1[1] * side, t1[0] * side)
            n2 = (-t2[1] * side, t2[0] * side)

            bx = n1[0] + n2[0]
            by = n1[1] + n2[1]
            bl = math.hypot(bx, by)

            if bl < 1e-9:
                ox = p_curr[0] + n1[0] * r
                oy = p_curr[1] + n1[1] * r
            else:
                bx /= bl
                by /= bl
                denom = bx * n1[0] + by * n1[1]
                if abs(denom) < 1e-9:
                    m = r
                else:
                    m = r / denom
                miter_limit = 6.0 * r
                if m > miter_limit:
                    m = miter_limit
                if m < -miter_limit:
                    m = -miter_limit
                ox = p_curr[0] + bx * m
                oy = p_curr[1] + by * m
            out.append((ox, oy))

        out.append(out[0])
        return out

        
    def generate_toolpath(self):
        if not self.svg_paths:
            messagebox.showwarning("Warnung", "Bitte laden Sie zuerst eine SVG-Datei")
            return
            
        self.toolpaths = []
        
        bed_width = self.settings['bed_width'].get()
        bed_height = self.settings['bed_height'].get()
        margin = self.settings['margin'].get()
        
        work_area_width = bed_width - 2 * margin
        work_area_height = bed_height - 2 * margin
        
        for path in self.svg_paths:
            if len(path) < 2:
                continue
                
            optimized_path = self.optimize_path(path)
            scaled_path = []
            
            # 1) Skalieren/verschieben in Maschinenkoordinaten
            scaled_path = []
            for x, y in optimized_path:
                sx = x * self.scale_factor.get() + self.offset_x.get()
                sy = y * self.scale_factor.get() + self.offset_y.get()
                scaled_path.append((sx, sy))

            # 2) Werkzeugradius-Kompensation (Ecken/Kanten stabil via Miter)
            tool_radius = max(0.0, float(self.settings['tool_diameter'].get()) / 2.0)
            compensated = self._offset_path(scaled_path, tool_radius)

            # 3) Auf Arbeitsbereich begrenzen
            clamped_path = []
            for x, y in compensated:
                nx = max(0.0, min(work_area_width, x))
                ny = max(0.0, min(work_area_height, y))
                clamped_path.append((nx, ny))

            if len(clamped_path) >= 2:
                self.toolpaths.append(clamped_path)
                
        self.toolpaths = self.sort_paths_by_distance(self.toolpaths)
        self.generate_gcode()
        self.update_canvas()
        
        total_length = sum(self.path_length(path) for path in self.toolpaths)
        layers = max(1, int(math.ceil(self.settings['material_height'].get() / self.settings['layer_depth'].get())))

        # Endmaße berechnen
        all_x = [p[0] for path in self.toolpaths for p in path]
        all_y = [p[1] for path in self.toolpaths for p in path]

        if all_x and all_y:
          part_width = max(all_x) - min(all_x)
          part_height = max(all_y) - min(all_y)
        else:
           part_width = 0
           part_height = 0
        
        self.info_text.delete(1.0, tk.END)

        self.info_text.insert(tk.END, "G-CODE:\n")
        self.info_text.insert(tk.END, f"Toolpaths generiert: {len(self.toolpaths)}\n")
        self.info_text.insert(tk.END, f"Gesamtlänge: {total_length:.2f} mm\n")
        self.info_text.insert(tk.END, f"Zeilen: {len(self.gcode_lines)}\n")

        self.info_text.insert(tk.END, "\n")
        self.info_text.insert(tk.END, "Generell:\n")
        estimated_time = (total_length / self.settings['feed_rate'].get() * layers) * 2 + 20
        self.info_text.insert(tk.END, f"Schichten: {layers}\n")
        self.info_text.insert(tk.END, f"Geschätzte Zeit: {estimated_time:.1f} Sek.\n")

        self.info_text.insert(tk.END, "\n")
        self.info_text.insert(tk.END, "Maße:\n")
        self.info_text.insert(tk.END, f"X/Y: {part_width:.2f} mm x {part_height:.2f} mm\n")
        self.info_text.insert(tk.END, f"Skalierung: {self.scale_factor.get():.2f}\n")

        self.info_text.insert(tk.END, "\n")
        self.info_text.insert(tk.END, "Anycubic CNC V2.1\n")
        self.info_text.insert(tk.END, "by HIGHVOLTAGEBEE\n")

        
    def optimize_path(self, path):
        if len(path) < 3:
            return path
            
        optimized = [path[0]]
        resolution = self.settings['resolution'].get()
        
        for i in range(1, len(path)):
            last_point = optimized[-1]
            current_point = path[i]
            
            dist = math.sqrt((current_point[0] - last_point[0])**2 + (current_point[1] - last_point[1])**2)
            
            if dist > resolution:
                optimized.append(current_point)
                
        return optimized
        
    def sort_paths_by_distance(self, paths):
        if len(paths) <= 1:
            return paths
            
        sorted_paths = [paths[0]]
        remaining = paths[1:]
        
        while remaining:
            last_end = sorted_paths[-1][-1]
            
            min_dist = float('inf')
            next_path_idx = 0
            reverse = False
            
            for i, path in enumerate(remaining):
                dist_start = math.sqrt((path[0][0] - last_end[0])**2 + (path[0][1] - last_end[1])**2)
                dist_end = math.sqrt((path[-1][0] - last_end[0])**2 + (path[-1][1] - last_end[1])**2)
                
                if dist_start < min_dist:
                    min_dist = dist_start
                    next_path_idx = i
                    reverse = False
                    
                if dist_end < min_dist:
                    min_dist = dist_end
                    next_path_idx = i
                    reverse = True
                    
            next_path = remaining.pop(next_path_idx)
            if reverse:
                next_path = list(reversed(next_path))
            sorted_paths.append(next_path)
            
        return sorted_paths
        
    def path_length(self, path):
        length = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            length += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return length
        
    def generate_gcode(self):
        self.gcode_lines = []
        
        self.gcode_lines.extend([
            "G21",
            "G90",
            "G28 Y",
            "G28 X",
            f"G1 Z{self.settings['safe_height'].get()} F{self.settings['travel_speed'].get() * 60}",
            "G28 Z",
            f"G1 Z{self.settings['safe_height'].get()} F{self.settings['travel_speed'].get() * 60}",
            ""
        ])
        
        bed_zero_height = self.settings['bed_zero_height'].get()
        material_height = self.settings['material_height'].get()
        layer_depth = self.settings['layer_depth'].get()
        margin = self.settings['margin'].get()
        
        layers = max(1, int(math.ceil(material_height / layer_depth)))
        
        for layer in range(layers):
            current_depth = min((layer + 1) * layer_depth, material_height)
            z_pos = bed_zero_height - current_depth
            
            self.gcode_lines.append(f"; Layer {layer + 1}/{layers}, depth {current_depth:.2f}mm")
            
            for path in self.toolpaths:
                if len(path) < 2:
                    continue
                    
                start_x = path[0][0] + margin
                start_y = path[0][1] + margin
                
                self.gcode_lines.append(f"G1 Z{self.settings['safe_height'].get()} F{self.settings['travel_speed'].get() * 60}")
                self.gcode_lines.append(f"G1 X{start_x:.3f} Y{start_y:.3f} F{self.settings['travel_speed'].get() * 60}")
                self.gcode_lines.append(f"G1 Z{z_pos:.3f} F{self.settings['feed_rate'].get() * 60}")
                
                for i in range(1, len(path)):
                    x = path[i][0] + margin
                    y = path[i][1] + margin
                    self.gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{self.settings['feed_rate'].get() * 60}")
                    
                self.gcode_lines.append("")
                
        self.gcode_lines.extend([
            "G91",
            "G1 Z50 F3000",
            "G90",
            "G1 X0 Y200 F3000",
            "M140 S0",
            "M30"
        ])
        
    def export_gcode(self):
        if not self.gcode_lines:
            messagebox.showwarning("Warnung", "Bitte generieren Sie zuerst einen Toolpath")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="G-Code speichern",
            defaultextension=".gcode",
            filetypes=[("G-Code files", "*.gcode"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(self.gcode_lines))
                messagebox.showinfo("Erfolg", f"G-Code gespeichert: {file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
                    
    def update_canvas(self):
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.update_canvas)
            return

        bed_width = self.settings['bed_width'].get()
        bed_height = self.settings['bed_height'].get()
        margin = self.settings['margin'].get()

        scale_x = canvas_width / bed_width
        scale_y = canvas_height / bed_height
        scale = min(scale_x, scale_y) * 0.9

        offset_x = (canvas_width - bed_width * scale) / 2
        offset_y = (canvas_height - bed_height * scale) / 2

        # Bett und Arbeitsbereich
        self.canvas.create_rectangle(
            offset_x, offset_y,
            offset_x + bed_width * scale,
            offset_y + bed_height * scale,
            outline='black', width=2
        )
        self.canvas.create_rectangle(
            offset_x + margin * scale, offset_y + margin * scale,
            offset_x + (bed_width - margin) * scale,
            offset_y + (bed_height - margin) * scale,
            outline='blue', width=1, fill='lightblue', stipple='gray50'
        )

        # Original-SVG-Pfade (Endergebnis)
        for path in self.svg_paths:
            if len(path) < 2:
                continue
            for j in range(len(path) - 1):
                x1 = offset_x + (path[j][0] * self.scale_factor.get() + self.offset_x.get() + margin) * scale
                y1 = offset_y + (path[j][1] * self.scale_factor.get() + self.offset_y.get() + margin) * scale
                x2 = offset_x + (path[j+1][0] * self.scale_factor.get() + self.offset_x.get() + margin) * scale
                y2 = offset_y + (path[j+1][1] * self.scale_factor.get() + self.offset_y.get() + margin) * scale
                self.canvas.create_line(x1, y1, x2, y2, fill='black', width=1)

        # Toolpaths (rot)
        for i, path in enumerate(self.toolpaths):
            if len(path) < 2:
                continue
            color = 'red' if i == 0 else 'darkred'
            for j in range(len(path) - 1):
                x1 = offset_x + (path[j][0] + margin) * scale
                y1 = offset_y + (path[j][1] + margin) * scale
                x2 = offset_x + (path[j+1][0] + margin) * scale
                y2 = offset_y + (path[j+1][1] + margin) * scale
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
            if path:
                x = offset_x + (path[0][0] + margin) * scale
                y = offset_y + (path[0][1] + margin) * scale
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='green', outline='darkgreen')

        self.canvas.create_text(offset_x + 5, offset_y + bed_height * scale - 5, 
                               text="(0,0)", anchor=tk.SW, fill='black')
        self.canvas.create_text(offset_x + bed_width * scale - 5, offset_y + 5, 
                               text=f"({bed_width:.0f},{bed_height:.0f})", anchor=tk.NE, fill='black')

        
    def on_canvas_click(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def on_canvas_drag(self, event):
        if self.svg_paths:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            bed_width = self.settings['bed_width'].get()
            bed_height = self.settings['bed_height'].get()
            
            scale_x = canvas_width / bed_width
            scale_y = canvas_height / bed_height
            scale = min(scale_x, scale_y) * 0.9
            
            dx_mm = dx / scale
            dy_mm = dy / scale
            
            self.offset_x.set(self.offset_x.get() + dx_mm)
            self.offset_y.set(self.offset_y.get() + dy_mm)
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            self.update_canvas()

if __name__ == "__main__":
    root = tk.Tk()
    app = SVGToCNCConverter(root)
    root.mainloop()