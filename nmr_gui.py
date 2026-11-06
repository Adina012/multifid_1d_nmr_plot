"""
NMR GUI Module
Provides the graphical user interface for NMR plotting.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nmr_plotter import (
    quantify_integrals,
    set_plot_quality,
    plot_nmr_data,
    show_integral_table,
)


class NMRPlotterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NMR Spectra Plotter")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(
            f"{min(1400, screen_width - 40)}x{min(900, screen_height - 80)}"
        )
        self.root.resizable(True, True)
        
        # Set purple theme colors
        self.bg_color = "#F0E6FF"  # Light purple background
        self.accent_color = "#9370DB"  # Medium purple
        self.dark_purple = "#663399"  # Dark purple
        
        self.root.configure(bg=self.bg_color)
        
        self.file_paths = []
        self.embedded_canvases = []
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
                       font=("Helvetica", 9), padding=4)
        style.map('TButton', background=[('active', self.dark_purple)])
        style.configure('TRadiobutton', background=self.bg_color, foreground=self.dark_purple, 
                       font=("Helvetica", 9))
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.dark_purple, 
                       font=("Helvetica", 9))
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
        main_frame = ttk.Frame(self.scrollable_frame, padding="8")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.scrollable_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(3, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, text="NMR Spectra Plotter", 
                              font=("Helvetica", 15, "bold"),
                              bg=self.bg_color, fg=self.dark_purple)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 8))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="6")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select Files (Replace)", command=self.select_files, width=20).grid(row=0, column=0, padx=5, pady=5)
        self.file_count_label = ttk.Label(file_frame, text="No files selected", font=("Helvetica", 10, "italic"))
        self.file_count_label.grid(row=0, column=1, padx=10, sticky=tk.W)

        ttk.Button(file_frame, text="Add Files", command=self.add_files, width=12).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(file_frame, text="Clear Files", command=self.clear_files, width=12).grid(row=0, column=3, padx=5, pady=5)
        
        # File list
        self.file_listbox = tk.Listbox(file_frame, height=4, width=75,
                                       bg='white', fg=self.dark_purple,
                                       selectbackground=self.accent_color,
                                       font=("Helvetica", 9))
        self.file_listbox.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky=(tk.W, tk.E))
        file_scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        file_scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

        ttk.Label(file_frame, text="Sample masses (mg, comma-separated):").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=(6, 2)
        )
        self.sample_amounts_entry = ttk.Entry(file_frame, width=60)
        self.sample_amounts_entry.grid(
            row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=(6, 2)
        )
        ttk.Label(
            file_frame,
            text="Enter one mass per selected file; the selected reference file uses its mass here too.",
            font=("Helvetica", 8, "italic"),
        ).grid(row=3, column=0, columnspan=5, sticky=tk.W, padx=5, pady=(0, 3))
        
        # Plot Mode Section
        mode_frame = ttk.LabelFrame(main_frame, text="Plot Mode", padding="6")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        
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
        
        # Color Theme Section
        theme_frame = ttk.LabelFrame(main_frame, text="Color Theme", padding="6")
        theme_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        
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
        ttk.Radiobutton(theme_frame, text="Gradient Green (dark to mint)", 
                       variable=self.color_theme, value="gradient_green").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(theme_frame, text="Teal-Indigo-Purple-Pink Gradient",
                       variable=self.color_theme, value="teal_indigo_purple_pink").grid(row=3, column=1,
                                                  sticky=tk.W,
                                                  padx=(30, 0), pady=5)

        self.show_area_under_curve = tk.BooleanVar(value=False)
        ttk.Checkbutton(theme_frame, text="Shade area under curves",
                   variable=self.show_area_under_curve).grid(row=4, column=0, columnspan=2,
                                      sticky=tk.W, pady=(8, 0))
        self.calculate_integrals = tk.BooleanVar(value=False)
        ttk.Checkbutton(theme_frame, text="Quantify from raw spectra",
                   variable=self.calculate_integrals).grid(row=5, column=0, columnspan=2,
                                      sticky=tk.W, pady=(4, 0))
        ttk.Label(theme_frame, text="Relative integral reference:").grid(
            row=7, column=0, sticky=tk.W, pady=(8, 0)
        )
        self.reference_file = tk.StringVar()
        self.reference_file_combo = ttk.Combobox(
            theme_frame, textvariable=self.reference_file, state="readonly", width=45
        )
        self.reference_file_combo.grid(row=7, column=1, sticky=tk.W, padx=(30, 0), pady=(8, 0))
        ttk.Label(theme_frame, text="Reference salt:").grid(
            row=8, column=0, sticky=tk.W, pady=(8, 0)
        )
        self.reference_salt = tk.StringVar(value="LiCl")
        self.reference_salt_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.reference_salt,
            values=("LiCl", "LiFSI", "Other"),
            state="readonly",
            width=15,
        )
        self.reference_salt_combo.grid(row=8, column=1, sticky=tk.W, padx=(30, 0), pady=(8, 0))
        ttk.Label(theme_frame, text="Reference concentration (mol Li/kg):").grid(
            row=9, column=0, sticky=tk.W, pady=(4, 0)
        )
        self.reference_concentration_entry = ttk.Entry(theme_frame, width=18)
        self.reference_concentration_entry.grid(row=9, column=1, sticky=tk.W, padx=(30, 0), pady=(4, 0))
        ttk.Label(
            theme_frame,
            text="This is lithium concentration; the salt molecular weight is not used.",
            font=("Helvetica", 8, "italic"),
        ).grid(row=10, column=0, columnspan=2, sticky=tk.W, padx=(30, 0), pady=(0, 3))
        
        # Custom Legend Section
        legend_frame = ttk.LabelFrame(main_frame, text="Custom Legend Labels", padding="6")
        legend_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        
        self.use_custom_legend = tk.BooleanVar(value=False)
        ttk.Checkbutton(legend_frame, text="Use custom labels (leave unchecked for filenames)", 
                       variable=self.use_custom_legend, 
                       command=self.toggle_legend).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)

        self.show_legends = tk.BooleanVar(value=True)
        ttk.Checkbutton(legend_frame, text="Show legends",
                   variable=self.show_legends).grid(row=1, column=0, sticky=tk.W,
                                padx=(25, 0), pady=4)
        self.use_small_legends = tk.BooleanVar(value=False)
        ttk.Checkbutton(legend_frame, text="Use smaller legends",
                   variable=self.use_small_legends).grid(row=1, column=1, columnspan=2,
                                     sticky=tk.W, pady=4)
        
        ttk.Label(legend_frame, text="Labels (comma-separated):").grid(row=2, column=0, sticky=tk.W, padx=(25, 10), pady=8)
        self.legend_entry = ttk.Entry(legend_frame, width=60, state="disabled")
        self.legend_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=8)
        
        help_legend = ttk.Label(legend_frame, text="💡 Tip: Enter labels in same order as files, e.g., 'Sample A, Sample B, Control'", 
                              font=("Helvetica", 8, "italic"))
        help_legend.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=(25, 0), pady=(5, 0))

        # Normalization Section
        norm_frame = ttk.LabelFrame(main_frame, text="Intensity Normalization", padding="6")
        norm_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))

        self.use_normalization = tk.BooleanVar(value=False)
        ttk.Checkbutton(norm_frame, text="Normalize intensity and Li result by sample amount (mg)",
                variable=self.use_normalization).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)
        self.normalize_integrals = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            norm_frame,
            text="Normalize integral values by sample amount (mg)",
            variable=self.normalize_integrals,
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=4)

        # X-Axis Limits Section
        xlim_frame = ttk.LabelFrame(main_frame, text="X-Axis Limits (ppm) - Zoom to Region", padding="6")
        xlim_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        
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

        # Axis Labels Section
        axis_label_frame = ttk.LabelFrame(main_frame, text="Axis Labels", padding="6")
        axis_label_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 6))
        axis_label_frame.columnconfigure(1, weight=1)

        ttk.Label(axis_label_frame, text="X-axis label:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.x_axis_label_entry = ttk.Entry(axis_label_frame, width=50)
        self.x_axis_label_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.x_axis_label_entry.insert(0, "ppm")

        ttk.Label(axis_label_frame, text="Y-axis label:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.y_axis_label_entry = ttk.Entry(axis_label_frame, width=50)
        self.y_axis_label_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.y_axis_label_entry.insert(0, "Intensity (a.u.)")
        
        # Plot Button
        plot_button = ttk.Button(main_frame, text="📊 Plot Spectra", command=self.plot_spectra, width=35)
        plot_button.grid(row=8, column=0, columnspan=3, pady=10)

        self.results_frame = ttk.LabelFrame(
            main_frame, text="Results", padding="10"
        )
        self.results_frame.grid(
            row=0, column=3, rowspan=10, sticky=(tk.N, tk.S, tk.E, tk.W),
            padx=(12, 0), pady=(0, 6)
        )
        self.results_frame.columnconfigure(0, weight=1)
        
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
        del _event
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, _event):
        del _event
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, _event):
        del _event
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel_events(self, *_args):
        del _args
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _unbind_mousewheel_events(self, *_args):
        del _args
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")

    def on_close(self):
        self._unbind_mousewheel_events()
        self._clear_results()
        self.root.destroy()

    def _clear_results(self):
        for canvas in self.embedded_canvases:
            canvas.get_tk_widget().destroy()
            canvas.figure.clear()
        self.embedded_canvases.clear()

    def _display_figure(self, figure):
        width, height = figure.get_size_inches()
        scale = min(6.0 / width, 2.8 / height, 1.0)
        figure.set_size_inches(width * scale, height * scale, forward=True)
        canvas = FigureCanvasTkAgg(figure, master=self.results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.embedded_canvases.append(canvas)
    
    def clear_files(self):
        self.file_paths = []
        self.update_file_list()
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file_path in self.file_paths:
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
        
        count = len(self.file_paths)
        self.file_count_label.config(text=f"{count} file(s) selected")
        file_names = [os.path.basename(path) for path in self.file_paths]
        self.reference_file_combo["values"] = file_names
        if file_names and self.reference_file.get() not in file_names:
            self.reference_file.set(file_names[0])
        elif not file_names:
            self.reference_file.set("")

    
    def toggle_limits(self):
        state = "normal" if self.use_custom_limits.get() else "disabled"
        self.x_max_entry.config(state=state)
        self.x_min_entry.config(state=state)
    
    def toggle_legend(self):
        state = "normal" if self.use_custom_legend.get() else "disabled"
        self.legend_entry.config(state=state)

    def _parse_csv_strings(self, raw_text):
        return [value.strip() for value in raw_text.split(',') if value.strip()]

    def _parse_csv_floats(self, raw_text):
        values = [float(value.strip()) for value in raw_text.split(",") if value.strip()]
        if any(value != value or value in (float("inf"), float("-inf")) for value in values):
            raise ValueError("Values must be finite numbers.")
        return values

    def plot_spectra(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select at least one NMR data file.")
            return
        
        try:
            # Get settings
            quality = "preview"
            plot_mode = self.plot_mode.get()
            color_theme = self.color_theme.get()
            show_area_under_curve = self.show_area_under_curve.get()
            calculate_integrals = self.calculate_integrals.get()
            show_legends = self.show_legends.get()
            use_small_legends = self.use_small_legends.get()
            x_axis_label = self.x_axis_label_entry.get().strip()
            y_axis_label = self.y_axis_label_entry.get().strip()
            reference_concentration_mol_li_kg = None
            reference_mass_mg = None
            reference_description = None
            reference_path = next(
                (
                    path for path in self.file_paths
                    if os.path.basename(path) == self.reference_file.get()
                ),
                None,
            )
            if reference_path is None:
                messagebox.showerror("Invalid Reference", "Please select a reference file.")
                return
            reference_index = self.file_paths.index(reference_path)
            
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
            if (
                self.use_normalization.get()
                or self.normalize_integrals.get()
                or calculate_integrals
            ):
                amounts_text = self.sample_amounts_entry.get().strip()
                if not amounts_text:
                    messagebox.showerror(
                        "Missing Sample Masses",
                        "Please enter one sample mass in mg for every selected file.",
                    )
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

            if calculate_integrals:
                try:
                    reference_concentration_mol_li_kg = float(
                        self.reference_concentration_entry.get()
                    )
                except ValueError:
                    messagebox.showerror(
                        "Invalid Reference",
                        "Reference concentration must be numeric.",
                    )
                    return
                if reference_concentration_mol_li_kg <= 0:
                    messagebox.showerror(
                        "Invalid Reference",
                        "Reference concentration must be greater than zero.",
                    )
                    return
                reference_mass_mg = sample_amounts_mg[reference_index]
                reference_description = (
                    f"{self.reference_salt.get()}, "
                    f"{reference_concentration_mol_li_kg:g} mol Li/kg, "
                    f"{reference_mass_mg:g} mg"
                )
            # Get x-axis limits if enabled
            x_limits = None
            if self.use_custom_limits.get():
                try:
                    x_max = float(self.x_max_entry.get())
                    x_min = float(self.x_min_entry.get())
                    if not (x_max > x_min):
                        raise ValueError
                    x_limits = (x_max, x_min)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers for x-axis limits.")
                    return
            
            # Set plot quality
            set_plot_quality(quality)

            plot_file_paths = [
                path for path in self.file_paths if path != reference_path
            ]
            if not plot_file_paths:
                messagebox.showwarning(
                    "No Spectra to Plot",
                    "The reference file is used for quantification and is not plotted.",
                )
                if not calculate_integrals:
                    return
            plot_labels = (
                [
                    label for index, label in enumerate(custom_labels)
                    if self.file_paths[index] != reference_path
                ]
                if custom_labels is not None
                else None
            )
            plot_sample_amounts_mg = (
                [
                    amount for index, amount in enumerate(sample_amounts_mg)
                    if self.file_paths[index] != reference_path
                ]
                if sample_amounts_mg is not None
                else None
            )
            
            # Plot (pass quality so plotter can adjust legend sizing)
            # The reference remains in quantification but is never sent to plotting.
            self._clear_results()
            if plot_file_paths:
                plot_figures = plot_nmr_data(
                    plot_file_paths,
                    plot_mode,
                    x_limits=x_limits,
                    color_theme=color_theme,
                    show_area_under_curve=show_area_under_curve,
                    show_legends=show_legends,
                    use_small_legends=use_small_legends,
                    custom_labels=plot_labels,
                    quality=quality,
                    sample_amounts_mg=plot_sample_amounts_mg,
                    x_axis_label=x_axis_label,
                    y_axis_label=y_axis_label,
                    show=False,
                    return_figures=True,
                )
                for figure in plot_figures:
                    self._display_figure(figure)

            if calculate_integrals:
                quantification_integrals = quantify_integrals(
                    self.file_paths,
                    sample_amounts_mg=sample_amounts_mg,
                    normalize=self.normalize_integrals.get(),
                )
                table_figure = show_integral_table(
                    self.file_paths,
                    {"quantification": quantification_integrals},
                    reference_index=reference_index,
                    reference_concentration_mol_li_kg=reference_concentration_mol_li_kg,
                    reference_mass_mg=reference_mass_mg,
                    sample_amounts_mg=sample_amounts_mg,
                    reference_description=reference_description,
                    show=False,
                )
                self._display_figure(table_figure)
            
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
