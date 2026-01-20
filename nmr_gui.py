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
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Set purple theme colors
        self.bg_color = "#F0E6FF"  # Light purple background
        self.accent_color = "#9370DB"  # Medium purple
        self.dark_purple = "#663399"  # Dark purple
        
        self.root.configure(bg=self.bg_color)
        
        self.file_paths = []
        self.setup_style()
        self.create_widgets()
    
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
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
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
        
        ttk.Button(file_frame, text="Select Files", command=self.select_files, width=20).grid(row=0, column=0, padx=5, pady=5)
        self.file_count_label = ttk.Label(file_frame, text="No files selected", font=("Helvetica", 10, "italic"))
        self.file_count_label.grid(row=0, column=1, padx=10, sticky=tk.W)
        
        ttk.Button(file_frame, text="Clear Files", command=self.clear_files, width=15).grid(row=0, column=2, padx=5, pady=5)
        
        # File list
        self.file_listbox = tk.Listbox(file_frame, height=8, width=75, 
                                       bg='white', fg=self.dark_purple,
                                       selectbackground=self.accent_color,
                                       font=("Helvetica", 9))
        self.file_listbox.grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
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
        
        # X-Axis Limits Section
        xlim_frame = ttk.LabelFrame(main_frame, text="X-Axis Limits (ppm) - Zoom to Region", padding="15")
        xlim_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
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
        plot_button.grid(row=5, column=0, columnspan=3, pady=25)
        
    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select NMR Data Files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_paths:
            self.file_paths = list(file_paths)
            self.update_file_list()
    
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
    
    def plot_spectra(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select at least one NMR data file.")
            return
        
        try:
            # Get settings
            quality = self.quality_mode.get()
            plot_mode = self.plot_mode.get()
            
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
            
            # Plot
            plot_nmr_data(self.file_paths, plot_mode, x_limits)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
