"""
NMR GUI Module
Provides the graphical user interface for NMR plotting.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from nmr_plotter import set_plot_quality, plot_nmr_data


class NMRPlotterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NMR Spectra Plotter")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # Set purple theme colors
        self.bg_color = "#F0E6FF"  # Light purple background
        self.accent_color = "#9370DB"  # Medium purple
        self.dark_purple = "#663399"  # Dark purple
        
        self.root.configure(bg=self.bg_color)
        
        self.file_paths = []
        self.setup_style()
        self.create_widgets()

        # Ensure mousewheel bindings are cleaned up on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_style(self):
        """Configure ttk styles for purple theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.dark_purple, font=("Helvetica", 10))
        style.configure('TLabelframe', background=self.bg_color, foreground=self.dark_purple)
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.dark_purple, 
                       font=("Helvetica", 11, "bold"))
        style.configure('TButton', background=self.accent_color, foreground='white', 
                       font=("Helvetica", 10), padding=8)
        style.map('TButton', background=[('active', self.dark_purple)])
        style.configure('TRadiobutton', background=self.bg_color, foreground=self.dark_purple, 
                       font=("Helvetica", 10))
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.dark_purple, 
                       font=("Helvetica", 10))
        style.configure('TEntry', fieldbackground='white', foreground=self.dark_purple)
        
    def create_widgets(self):
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Keep canvas/scrollregion synced with content size
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel bindings only while cursor is over canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel_events)
        self.canvas.bind("<Leave>", self._unbind_mousewheel_events)
        
        # Main frame inside scrollable area
        main_frame = ttk.Frame(self.scrollable_frame, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.scrollable_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, text="NMR Spectra Plotter", 
                              font=("Helvetica", 18, "bold"),
                              bg=self.bg_color, fg=self.dark_purple)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="15")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select Files (Replace)", command=self.select_files, width=20).grid(row=0, column=0, padx=5, pady=5)
        self.file_count_label = ttk.Label(file_frame, text="No files selected", font=("Helvetica", 10, "italic"))
        self.file_count_label.grid(row=0, column=1, padx=10, sticky=tk.W)

        ttk.Button(file_frame, text="Add Files", command=self.add_files, width=12).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(file_frame, text="Clear Files", command=self.clear_files, width=12).grid(row=0, column=3, padx=5, pady=5)
        
        # File list
        self.file_listbox = tk.Listbox(file_frame, height=8, width=75, 
                                       bg='white', fg=self.dark_purple,
                                       selectbackground=self.accent_color,
                                       font=("Helvetica", 9))
        self.file_listbox.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky=(tk.W, tk.E))
        file_scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        file_scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        # Plot Mode Section
        mode_frame = ttk.LabelFrame(main_frame, text="Plot Mode", padding="15")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.plot_mode = tk.StringVar(value="multiple")
        ttk.Radiobutton(mode_frame, text="Multiple spectra on same figure", 
                       variable=self.plot_mode, value="multiple").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="One spectrum per figure", 
                       variable=self.plot_mode, value="single").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="Stacked subplots (each spectrum in its own row)",
                   variable=self.plot_mode, value="stacked").grid(row=2, column=0, sticky=tk.W, pady=5)
        stacked_help = ttk.Label(mode_frame, text="Stacked: aligns spectra vertically, shared x-axis",
                     font=("Helvetica", 8, "italic"))
        stacked_help.grid(row=3, column=0, sticky=tk.W, pady=(0, 6))
        
        # Quality Mode Section
        quality_frame = ttk.LabelFrame(main_frame, text="Plot Quality", padding="15")
        quality_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.quality_mode = tk.StringVar(value="publication")
        ttk.Radiobutton(quality_frame, text="Publication quality (300 DPI)", 
                       variable=self.quality_mode, value="publication").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(quality_frame, text="Preview quality (100 DPI)", 
                       variable=self.quality_mode, value="preview").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Color Theme Section
        theme_frame = ttk.LabelFrame(main_frame, text="Color Theme", padding="15")
        theme_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.color_theme = tk.StringVar(value="viridis")
        ttk.Radiobutton(theme_frame, text="Viridis (purple-yellow)", 
                       variable=self.color_theme, value="viridis").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(theme_frame, text="Plasma (purple-pink-orange)", 
                       variable=self.color_theme, value="plasma").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(theme_frame, text="Inferno (black-purple-yellow)", 
                       variable=self.color_theme, value="inferno").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(theme_frame, text="Magma (black-purple-white)", 
                       variable=self.color_theme, value="magma").grid(row=0, column=1, sticky=tk.W, padx=(30, 0), pady=5)
        ttk.Radiobutton(theme_frame, text="Muted (soft tones)", 
                       variable=self.color_theme, value="tab10").grid(row=1, column=1, sticky=tk.W, padx=(30, 0), pady=5)
        ttk.Radiobutton(theme_frame, text="Spring Pastels (soft colors)", 
                       variable=self.color_theme, value="Set2").grid(row=2, column=1, sticky=tk.W, padx=(30, 0), pady=5)
        
        # Custom Legend Section
        legend_frame = ttk.LabelFrame(main_frame, text="Custom Legend Labels", padding="15")
        legend_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.use_custom_legend = tk.BooleanVar(value=False)
        ttk.Checkbutton(legend_frame, text="Use custom labels (leave unchecked for filenames)", 
                       variable=self.use_custom_legend, 
                       command=self.toggle_legend).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)
        
        ttk.Label(legend_frame, text="Labels (comma-separated):").grid(row=1, column=0, sticky=tk.W, padx=(25, 10), pady=8)
        self.legend_entry = ttk.Entry(legend_frame, width=60, state="disabled")
        self.legend_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=8)
        
        help_legend = ttk.Label(legend_frame, text="💡 Tip: Enter labels in same order as files, e.g., 'Sample A, Sample B, Control'", 
                              font=("Helvetica", 8, "italic"))
        help_legend.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=(25, 0), pady=(5, 0))

        # Normalization Section
        norm_frame = ttk.LabelFrame(main_frame, text="Intensity Normalization", padding="15")
        norm_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        self.use_normalization = tk.BooleanVar(value=False)
        ttk.Checkbutton(norm_frame, text="Normalize intensity by sample amount in tube (mg)",
                variable=self.use_normalization,
                command=self.toggle_normalization).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)

        ttk.Label(norm_frame, text="Amounts (mg, comma-separated):").grid(row=1, column=0, sticky=tk.W, padx=(25, 10), pady=8)
        self.sample_amounts_entry = ttk.Entry(norm_frame, width=60, state="disabled")
        self.sample_amounts_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=8)

        help_norm = ttk.Label(norm_frame,
                      text="💡 Tip: Enter one positive value per file in mg, e.g., '2.5, 3.0, 1.8'",
                      font=("Helvetica", 8, "italic"))
        help_norm.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=(25, 0), pady=(5, 0))
        
        # X-Axis Limits Section
        xlim_frame = ttk.LabelFrame(main_frame, text="X-Axis Limits (ppm) - Zoom to Region", padding="15")
        xlim_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.use_custom_limits = tk.BooleanVar(value=False)
        ttk.Checkbutton(xlim_frame, text="Enable zoom (only plot selected region)", 
                       variable=self.use_custom_limits, 
                       command=self.toggle_limits).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)
        
        ttk.Label(xlim_frame, text="From (high ppm):").grid(row=1, column=0, sticky=tk.W, padx=(25, 10), pady=8)
        self.x_max_entry = ttk.Entry(xlim_frame, width=15, state="disabled")
        self.x_max_entry.grid(row=1, column=1, sticky=tk.W, pady=8)
        self.x_max_entry.insert(0, "200")
        
        ttk.Label(xlim_frame, text="To (low ppm):").grid(row=2, column=0, sticky=tk.W, padx=(25, 10), pady=8)
        self.x_min_entry = ttk.Entry(xlim_frame, width=15, state="disabled")
        self.x_min_entry.grid(row=2, column=1, sticky=tk.W, pady=8)
        self.x_min_entry.insert(0, "-100")
        
        # Help text
        help_label = ttk.Label(xlim_frame, text="💡 Tip: Only data within this range will be plotted", 
                              font=("Helvetica", 8, "italic"))
        help_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=(25, 0), pady=(5, 0))
        
        # Plot Button
        plot_button = ttk.Button(main_frame, text="📊 Plot Spectra", command=self.plot_spectra, width=35)
        plot_button.grid(row=8, column=0, columnspan=3, pady=25)
        
    def select_files(self):
        # Temporarily unbind wheel events while native dialog is open
        self._unbind_mousewheel_events()
        file_paths = filedialog.askopenfilenames(
            parent=self.root,
            title="Select NMR Data Files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_paths:
            self.file_paths = list(file_paths)
            self.update_file_list()

    def add_files(self):
        # Temporarily unbind wheel events while native dialog is open
        self._unbind_mousewheel_events()
        file_paths = filedialog.askopenfilenames(
            parent=self.root,
            title="Add NMR Data Files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_paths:
            existing = set(self.file_paths)
            new_files = [path for path in file_paths if path not in existing]
            self.file_paths.extend(new_files)
            self.update_file_list()

    def _on_frame_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, _event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, _event):
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel_events(self, _event=None):
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _unbind_mousewheel_events(self, _event=None):
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")

    def on_close(self):
        self._unbind_mousewheel_events()
        self.root.destroy()
    
    def clear_files(self):
        self.file_paths = []
        self.update_file_list()
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file_path in self.file_paths:
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
        
        count = len(self.file_paths)
        self.file_count_label.config(text=f"{count} file(s) selected")
    
    def toggle_limits(self):
        state = "normal" if self.use_custom_limits.get() else "disabled"
        self.x_max_entry.config(state=state)
        self.x_min_entry.config(state=state)
    
    def toggle_legend(self):
        state = "normal" if self.use_custom_legend.get() else "disabled"
        self.legend_entry.config(state=state)

    def toggle_normalization(self):
        state = "normal" if self.use_normalization.get() else "disabled"
        self.sample_amounts_entry.config(state=state)

    def _parse_csv_strings(self, raw_text):
        return [value.strip() for value in raw_text.split(',') if value.strip()]

    def _parse_csv_floats(self, raw_text):
        return [float(value.strip()) for value in raw_text.split(',') if value.strip()]

    def plot_spectra(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select at least one NMR data file.")
            return
        
        try:
            # Get settings
            quality = self.quality_mode.get()
            plot_mode = self.plot_mode.get()
            color_theme = self.color_theme.get()
            
            # Get custom legend labels if enabled
            custom_labels = None
            if self.use_custom_legend.get():
                labels_text = self.legend_entry.get().strip()
                if labels_text:
                    custom_labels = self._parse_csv_strings(labels_text)
                    if len(custom_labels) != len(self.file_paths):
                        messagebox.showerror(
                            "Input Mismatch",
                            f"You selected {len(self.file_paths)} file(s), so please enter {len(self.file_paths)} custom label(s)."
                        )
                        return

            # Get normalization amounts if enabled
            sample_amounts_mg = None
            if self.use_normalization.get():
                amounts_text = self.sample_amounts_entry.get().strip()
                if not amounts_text:
                    messagebox.showerror("Missing Input", "Please enter sample amounts in mg for all files.")
                    return

                try:
                    sample_amounts_mg = self._parse_csv_floats(amounts_text)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Sample amounts must be numeric values (decimals allowed) in mg, separated by commas.")
                    return

                if len(sample_amounts_mg) != len(self.file_paths):
                    messagebox.showerror(
                        "Input Mismatch",
                        f"You selected {len(self.file_paths)} file(s), so please enter {len(self.file_paths)} amount(s)."
                    )
                    return

                if any(value <= 0 for value in sample_amounts_mg):
                    messagebox.showerror("Invalid Input", "All sample amounts must be greater than 0 mg.")
                    return
            
            # Get x-axis limits if enabled
            x_limits = None
            if self.use_custom_limits.get():
                try:
                    x_max = float(self.x_max_entry.get())
                    x_min = float(self.x_min_entry.get())
                    x_limits = (x_max, x_min)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers for x-axis limits.")
                    return
            
            # Set plot quality
            set_plot_quality(quality)
            
            # Plot (pass quality so plotter can adjust legend sizing)
            plot_nmr_data(
                self.file_paths,
                plot_mode,
                x_limits=x_limits,
                color_theme=color_theme,
                custom_labels=custom_labels,
                quality=quality,
                sample_amounts_mg=sample_amounts_mg,
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
