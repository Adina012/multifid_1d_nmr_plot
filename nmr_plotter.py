"""
NMR Plotter Module
Handles plotting of NMR spectra data.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import io
from PIL import Image
from nmr_reader import readNMR


def copy_figure_to_clipboard(fig):
    """
    Copy the current figure to clipboard.
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to copy to clipboard
    """
    try:
        # Save figure to a BytesIO buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        
        # Load image from buffer and copy to clipboard
        img = Image.open(buf)
        
        # Copy to clipboard using PIL
        import platform
        if platform.system() == 'Darwin':  # macOS
            import subprocess
            # Save to temporary file and use pbcopy
            temp_path = '/tmp/nmr_plot_temp.png'
            img.save(temp_path, 'PNG')
            subprocess.run(['osascript', '-e', f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'], check=True)
            os.remove(temp_path)
            print("Figure copied to clipboard!")
        elif platform.system() == 'Windows':
            try:
                import win32clipboard  # type: ignore
                from io import BytesIO
                output = BytesIO()
                img.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]  # Remove BMP header
                output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                print("Figure copied to clipboard!")
            except ImportError:
                print("Windows clipboard support requires: pip install pywin32")
        else:  # Linux
            import subprocess
            temp_path = '/tmp/nmr_plot_temp.png'
            img.save(temp_path, 'PNG')
            subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', temp_path], check=True)
            os.remove(temp_path)
            print("Figure copied to clipboard!")
        
        buf.close()
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        print("You may need to install additional dependencies:")
        print("  macOS: No additional dependencies needed")
        print("  Windows: pip install pywin32")
        print("  Linux: sudo apt-get install xclip (or xsel)")


def set_plot_quality(quality='publication'):
    """Sets matplotlib parameters based on quality mode."""
    if quality == 'publication':
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['lines.linewidth'] = 1.0
        plt.rcParams['xtick.major.width'] = 0.8
        plt.rcParams['ytick.major.width'] = 0.8
        plt.rcParams['xtick.minor.width'] = 0.5
        plt.rcParams['ytick.minor.width'] = 0.5
    else:  # preview
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 100
        plt.rcParams['font.size'] = 9
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['lines.linewidth'] = 0.8
        plt.rcParams['xtick.major.width'] = 0.6
        plt.rcParams['ytick.major.width'] = 0.6
        plt.rcParams['xtick.minor.width'] = 0.4
        plt.rcParams['ytick.minor.width'] = 0.4


def plot_nmr_data(file_paths, plot_mode, x_limits=None):
    """
    Plot NMR data according to specified parameters.
    
    Parameters:
    -----------
    file_paths : list of str
        Paths to NMR data files
    plot_mode : str
        'multiple' for all spectra on same figure, 'single' for separate figures
    x_limits : tuple of (float, float), optional
        X-axis limits as (x_max, x_min) in ppm. Data will be filtered to this range.
    """
    num_files = len(file_paths)
    formatter = ticker.ScalarFormatter(useMathText=True)
    
    if plot_mode == "multiple":
        # Plot all spectra on the same figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate color gradient
        colors = plt.cm.viridis(np.linspace(0, 1, num_files))
        
        for idx, (color, file_path) in enumerate(zip(colors, file_paths)):
            try:
                # Pass x_limits to readNMR so it filters the data
                x_values, y_values = readNMR(file_path, x_limits=x_limits)
                
                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]
                
                filename = os.path.basename(file_path)
                ax.plot(x_values, y_values, linewidth=0.8, label=filename, color=color)
            
            except ValueError as e:
                print(f"Warning: {e}")
        
        ax.set_xlabel("ppm", fontsize=10)
        ax.set_ylabel("Intensity", fontsize=10)
        # Place a compact legend in the upper-right corner inside the axes
        # Use a smaller font so it covers less of the data
        ax.legend(fontsize=7, frameon=False, loc='upper right')
        # Standard NMR convention: positive ppm on right, negative on left
        
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # No figure title
        plt.tight_layout()
        
        # Add key press event handler for clipboard copy
        def on_key(event):
            if event.key == 'c':
                copy_figure_to_clipboard(fig)
        
        fig.canvas.mpl_connect('key_press_event', on_key)
        plt.show()
    
    elif plot_mode == "stacked":
        # Stack each file in its own subplot (vertical layout) within one figure
        # Useful to compare spectra aligned vertically while keeping x-axis shared
        if num_files == 0:
            print("No files to plot.")
            return

        # Create one subplot per file, share x-axis
        fig, axes = plt.subplots(num_files, 1, sharex=True, figsize=(10, max(3 * num_files, 6)))
        # Ensure axes is iterable
        if num_files == 1:
            axes = [axes]

        # Color map for consistent coloring across subplots
        colors = plt.cm.viridis(np.linspace(0, 1, num_files))

        for ax, color, file_path in zip(axes, colors, file_paths):
            try:
                x_values, y_values = readNMR(file_path, x_limits=x_limits)

                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]

                filename = os.path.basename(file_path)
                # Plot with label for legend
                ax.plot(x_values, y_values, linewidth=0.8, color=color, label=filename)
                ax.set_ylabel('Intensity', fontsize=9)
                # No subplot title - filenames will appear in legend only
                # Standard NMR convention: positive ppm on right, negative on left

                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                ax.tick_params(axis='both', which='major', labelsize=8)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            except ValueError as e:
                print(f"Warning: {e}")

        # Label x-axis on the bottom subplot only
        axes[-1].set_xlabel('ppm', fontsize=10)

        # No figure title
        plt.tight_layout()

        # Build a single compact legend for the stacked figure in the top-right
        # corner of the figure (collect labels from each subplot)
        handles = []
        labels = []
        for ax in axes:
            h, l = ax.get_legend_handles_labels()
            if h:
                handles.extend(h)
                labels.extend(l)

        if handles:
            fig.legend(handles, labels, loc='upper right', fontsize=7, frameon=False,
                       bbox_to_anchor=(0.98, 0.98))

        # Add clipboard copy handler
        def on_key_stack(event):
            if event.key == 'c':
                copy_figure_to_clipboard(fig)

        fig.canvas.mpl_connect('key_press_event', on_key_stack)
        plt.show()
    
    else:  # single mode
        # Plot each spectrum in a separate figure
        for file_path in file_paths:
            try:
                # Pass x_limits to readNMR so it filters the data
                x_values, y_values = readNMR(file_path, x_limits=x_limits)
                
                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]
                
                filename = os.path.basename(file_path)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x_values, y_values, linewidth=0.8, color='#1f77b4')
                
                ax.set_xlabel("ppm", fontsize=10)
                ax.set_ylabel("Intensity", fontsize=10)
                ax.set_title(filename, fontsize=12)
                # Standard NMR convention: positive ppm on right, negative on left
                
                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                ax.tick_params(axis='both', which='major', labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                plt.tight_layout()
                
                # Add key press event handler for clipboard copy
                def on_key(event):
                    if event.key == 'c':
                        copy_figure_to_clipboard(fig)
                
                fig.canvas.mpl_connect('key_press_event', on_key)
                plt.show()
            
            except ValueError as e:
                print(f"Warning: {e}")
