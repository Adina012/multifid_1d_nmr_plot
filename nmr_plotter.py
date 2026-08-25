"""
NMR Plotter Module
Handles plotting of NMR spectra data.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
import os
import io
from PIL import Image
from nmr_reader import readNMR


# Register custom colormaps
def register_custom_colormaps():
    """Register custom color schemes for plotting."""
    # Gradient Green color scheme
    gradient_green_colors = [
        '#c5e1a5',  # Mint green
        '#aed581',  # Very pale green
        '#9ccc65',  # Pale green
        '#8BC34A',  # Lighter green
        '#7CB342',  # Light green
        '#689F38',  # Green
        '#558B2F',  # Forest green
        '#33691E',  # Dark green
    ]
    gradient_green_cmap = mcolors.LinearSegmentedColormap.from_list(
        'gradient_green', gradient_green_colors
    )
    plt.colormaps.register(gradient_green_cmap)


# Register custom colormaps when module is imported
register_custom_colormaps()


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
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
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
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['lines.linewidth'] = 0.8
        plt.rcParams['xtick.major.width'] = 0.6
        plt.rcParams['ytick.major.width'] = 0.6
        plt.rcParams['xtick.minor.width'] = 0.4
        plt.rcParams['ytick.minor.width'] = 0.4


def _get_area_color(color):
    """Return a lighter version of a curve color for area shading."""
    curve_rgb = np.asarray(mcolors.to_rgb(color))
    return tuple(curve_rgb + (1 - curve_rgb) * 0.35)


def _plot_curve(ax, x_values, y_values, color, show_area_under_curve, **kwargs):
    """Plot a curve and optionally shade the area between it and zero."""
    if show_area_under_curve:
        ax.fill_between(
            x_values,
            0,
            y_values,
            color=_get_area_color(color),
            alpha=0.9,
            linewidth=0,
        )
    return ax.plot(x_values, y_values, color=color, **kwargs)


def plot_nmr_data(
    file_paths,
    plot_mode,
    x_limits=None,
    color_theme='viridis',
    custom_labels=None,
    quality='publication',
    sample_amounts_mg=None,
    x_axis_label=None,
    y_axis_label=None,
    show_area_under_curve=False,
    show_legends=True,
    use_small_legends=False,
):
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
    color_theme : str, optional
        Matplotlib colormap name (default: 'viridis'). Options: 'viridis', 'plasma', 
        'inferno', 'magma', 'cool', 'rainbow', etc.
    custom_labels : list of str, optional
        Custom legend labels. If None, uses filenames. Should match number of files.
    sample_amounts_mg : list of float, optional
        Sample amounts in mg for each file. If provided, intensity is normalized
        as y_normalized = y / amount_mg for each corresponding file.
    x_axis_label : str, optional
        Custom x-axis label. Defaults to ``ppm`` when empty or omitted.
    y_axis_label : str, optional
        Custom y-axis label. Defaults to ``Intensity (a.u.)`` when empty or omitted.
    show_area_under_curve : bool, optional
        Shade the area between each curve and the zero-intensity baseline.
    show_legends : bool, optional
        Display legends for plot modes that support them.
    use_small_legends : bool, optional
        Use a smaller legend font.
    """
    num_files = len(file_paths)
    formatter = ticker.ScalarFormatter(useMathText=True)
    x_axis_label = x_axis_label.strip() if x_axis_label and x_axis_label.strip() else "ppm"
    y_axis_label = y_axis_label.strip() if y_axis_label and y_axis_label.strip() else "Intensity (a.u.)"
    
    # Determine legend font sizes based on quality (preview should be slightly larger)
    if quality == 'preview':
        # Make legends noticeably larger in preview mode for readability
        legend_font = 8 if use_small_legends else 10
        stacked_legend_font = 8 if use_small_legends else 10
    else:
        legend_font = 8 if use_small_legends else 10
        stacked_legend_font = 8 if use_small_legends else 10

    if plot_mode == "multiple":
        # Plot all spectra on the same figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate color gradient using selected theme
        colors = plt.cm.get_cmap(color_theme)(np.linspace(0, 1, num_files))
        
        for idx, (color, file_path) in enumerate(zip(colors, file_paths)):
            try:
                # Pass x_limits to readNMR so it filters the data
                x_values, y_values = readNMR(file_path, x_limits=x_limits)
                
                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]

                if sample_amounts_mg is not None and idx < len(sample_amounts_mg):
                    y_values = y_values / sample_amounts_mg[idx]
                
                filename = os.path.basename(file_path)
                # Use custom label if provided, otherwise use filename
                label = custom_labels[idx] if custom_labels and idx < len(custom_labels) else filename
                _plot_curve(
                    ax, x_values, y_values, color, show_area_under_curve,
                    linewidth=0.8, label=label,
                )
            
            except ValueError as e:
                print(f"Warning: {e}")
        
        ax.set_xlabel(x_axis_label, fontsize=11)
        ax.set_ylabel(y_axis_label, fontsize=11)
        # Place a compact legend in the upper-right corner inside the axes
        # Use a smaller font so it covers less of the data
        if show_legends:
            ax.legend(fontsize=legend_font, frameon=False, loc='upper right')
        # NMR convention: high ppm (positive) on left, low ppm (negative) on right
        ax.invert_xaxis()
        
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.yaxis.get_offset_text().set_fontsize(9)
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # No figure title
        # Add margins to ensure axis labels are visible
        plt.tight_layout(rect=[0.08, 0.12, 0.98, 0.98])
        
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

        # Color map using selected theme
        colors = plt.cm.get_cmap(color_theme)(np.linspace(0, 1, num_files))

        for idx, (ax, color, file_path) in enumerate(zip(axes, colors, file_paths)):
            try:
                x_values, y_values = readNMR(file_path, x_limits=x_limits)

                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]

                if sample_amounts_mg is not None and idx < len(sample_amounts_mg):
                    y_values = y_values / sample_amounts_mg[idx]

                filename = os.path.basename(file_path)
                # Use custom label if provided, otherwise use filename
                label = custom_labels[idx] if custom_labels and idx < len(custom_labels) else filename
                # Plot with label for legend
                _plot_curve(
                    ax, x_values, y_values, color, show_area_under_curve,
                    linewidth=0.8, label=label,
                )
                ax.set_ylabel(y_axis_label, fontsize=11)
                # No subplot title - filenames will appear in legend only

                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                ax.yaxis.get_offset_text().set_fontsize(9)
                ax.tick_params(axis='both', which='major', labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            except ValueError as e:
                print(f"Warning: {e}")

        # Label x-axis on the bottom subplot only
        axes[-1].set_xlabel(x_axis_label, fontsize=11)
        
        # NMR convention: high ppm on left, low ppm on right (invert once for shared x-axis)
        axes[0].invert_xaxis()

        # No figure title
        # Add margins to ensure axis labels are visible
        plt.tight_layout(rect=[0.08, 0.12, 0.98, 0.98])

        # Build a single compact legend for the stacked figure in the top-right
        # corner of the figure (collect labels from each subplot)
        handles = []
        labels = []
        for ax in axes:
            h, l = ax.get_legend_handles_labels()
            if h:
                handles.extend(h)
                labels.extend(l)

        if show_legends and handles:
            fig.legend(handles, labels, loc='upper right', fontsize=stacked_legend_font, frameon=False,
                       bbox_to_anchor=(0.98, 0.98))

        # Add clipboard copy handler
        def on_key_stack(event):
            if event.key == 'c':
                copy_figure_to_clipboard(fig)

        fig.canvas.mpl_connect('key_press_event', on_key_stack)
        plt.show()
    
    else:  # single mode
        # Plot each spectrum in a separate figure
        for idx, file_path in enumerate(file_paths):
            try:
                # Pass x_limits to readNMR so it filters the data
                x_values, y_values = readNMR(file_path, x_limits=x_limits)
                
                # Reverse if needed to ensure decreasing order (NMR standard)
                if len(x_values) > 0 and x_values[0] < x_values[-1]:
                    x_values = x_values[::-1]
                    y_values = y_values[::-1]

                if sample_amounts_mg is not None and idx < len(sample_amounts_mg):
                    y_values = y_values / sample_amounts_mg[idx]
                
                filename = os.path.basename(file_path)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                curve_color = '#1f77b4'
                _plot_curve(
                    ax, x_values, y_values, curve_color, show_area_under_curve,
                    linewidth=0.8,
                )
                
                ax.set_xlabel(x_axis_label, fontsize=11)
                ax.set_ylabel(y_axis_label, fontsize=11)
                ax.set_title(filename, fontsize=12)
                # NMR convention: high ppm on left, low ppm on right
                ax.invert_xaxis()
                
                ax.yaxis.set_major_formatter(formatter)
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                ax.yaxis.get_offset_text().set_fontsize(9)
                ax.tick_params(axis='both', which='major', labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Add margins to ensure axis labels are visible
                plt.tight_layout(rect=[0.08, 0.12, 0.98, 0.98])
                
                # Add key press event handler for clipboard copy
                def on_key(event):
                    if event.key == 'c':
                        copy_figure_to_clipboard(fig)
                
                fig.canvas.mpl_connect('key_press_event', on_key)
                plt.show()
            
            except ValueError as e:
                print(f"Warning: {e}")
