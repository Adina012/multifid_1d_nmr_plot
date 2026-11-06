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
import textwrap
from PIL import Image
from nmr_reader import readNMR


LITHIUM_ATOMIC_MOLAR_MASS_G_PER_MOL = 6.941


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
    if "gradient_green" not in plt.colormaps:
        plt.colormaps.register(gradient_green_cmap)

    teal_indigo_purple_pink_colors = [
        '#00695c',  # Deep teal
        '#00897b',  # Teal
        '#3949ab',  # Indigo
        '#5e35b1',  # Violet
        '#6a1b9a',  # Purple
        '#8e24aa',  # Magenta purple
        '#ad1457',  # Magenta
        '#f06292',  # Pink
    ]
    teal_indigo_purple_pink_cmap = mcolors.LinearSegmentedColormap.from_list(
        'teal_indigo_purple_pink', teal_indigo_purple_pink_colors
    )
    if "teal_indigo_purple_pink" not in plt.colormaps:
        plt.colormaps.register(teal_indigo_purple_pink_cmap)


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
        # Keep exported images publication quality even when the GUI uses
        # lightweight preview rendering.
        plt.rcParams['savefig.dpi'] = 300
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
    return tuple(curve_rgb + (1 - curve_rgb) * 0.5)


def _plot_curve(ax, x_values, y_values, color, show_area_under_curve, layer=0, **kwargs):
    """Plot a curve and optionally shade the area between it and zero."""
    curve_zorder = 3 + (layer * 2)
    if show_area_under_curve:
        ax.fill_between(
            x_values,
            0,
            y_values,
            color=_get_area_color(color),
            alpha=0.5,
            linewidth=0,
            zorder=curve_zorder,
        )
    return ax.plot(x_values, y_values, color=color, zorder=curve_zorder + 1, **kwargs)


def integrate_spectrum(x_values, y_values):
    """Return the signed area under a spectrum, independent of x-axis direction."""
    x_values = np.asarray(x_values)
    y_values = np.asarray(y_values)
    if len(x_values) < 2:
        return 0.0

    sort_order = np.argsort(x_values)
    return float(np.trapz(y_values[sort_order], x_values[sort_order]))


def quantify_integrals(file_paths, sample_amounts_mg=None, normalize=False):
    """Calculate quantification integrals directly from each raw spectrum."""
    if normalize and (
        sample_amounts_mg is None or len(sample_amounts_mg) != len(file_paths)
    ):
        raise ValueError("A positive sample mass is required for every file.")
    integrals = []
    for index, file_path in enumerate(file_paths):
        x_values, y_values = readNMR(file_path)
        integral = integrate_spectrum(x_values, y_values)
        if normalize:
            if sample_amounts_mg[index] <= 0:
                raise ValueError("Sample masses must be greater than zero.")
            integral /= sample_amounts_mg[index]
        integrals.append(integral)
    return integrals


def calculate_lithium_amounts(
    relative_integral,
    reference_concentration_mol_li_kg,
    reference_mass_mg,
    sample_mass_mg=None,
):
    """Convert a reference-scaled integral into lithium amounts.

    The reference concentration is explicitly in mol Li/kg, not mol salt/kg.
    Therefore the salt molecular weight and salt stoichiometry are not used.
    """
    reference_mass_kg = reference_mass_mg / 1_000_000
    reference_moles_li = (
        reference_concentration_mol_li_kg * reference_mass_kg
    )
    lithium_mmol = relative_integral * reference_moles_li * 1000
    lithium_mg = lithium_mmol * LITHIUM_ATOMIC_MOLAR_MASS_G_PER_MOL

    if sample_mass_mg is None:
        return lithium_mmol, lithium_mg, None
    lithium_ug_per_mg = lithium_mg * 1000 / sample_mass_mg
    return lithium_mmol, lithium_mg, lithium_ug_per_mg


def show_integral_table(
    file_paths,
    integrated_intensities,
    reference_index=0,
    reference_concentration_mol_li_kg=None,
    reference_mass_mg=None,
    sample_amounts_mg=None,
    reference_description=None,
    show=True,
):
    """Display integrated intensities and relative values in a table figure."""
    quantification = integrated_intensities.get("quantification", [])
    has_quantification = bool(quantification)
    row_count = len(file_paths)

    def relative_values(values):
        if not values:
            return []
        reference_value = values[reference_index]
        if reference_value == 0:
            return [None] * len(values)
        return [value / reference_value for value in values]

    quantification_relative = relative_values(quantification)
    columns = ["File"]
    if has_quantification:
        columns.extend(["Quantification integral", "Relative"])
    if (
        reference_concentration_mol_li_kg is not None
        and reference_mass_mg is not None
    ):
        columns.extend(["Li amount (mmol)", "Li amount (mg)"])
        if sample_amounts_mg is not None:
            columns.append("Li (ug/mg sample)")

    rows = []
    file_name_width = 28
    for index, file_path in enumerate(file_paths):
        row = [textwrap.fill(
            os.path.basename(file_path),
            width=file_name_width,
            break_long_words=True,
            break_on_hyphens=False,
        )]
        if has_quantification:
            row.extend([
                f"{quantification[index]:.6g}",
                "undefined" if quantification_relative[index] is None else f"{quantification_relative[index]:.6g}",
            ])
        if (
            reference_concentration_mol_li_kg is not None
            and reference_mass_mg is not None
        ):
            relative_value = quantification_relative[index]
            lithium_mmol = lithium_mg = lithium_ug_per_mg = None
            if relative_value is not None:
                (
                    lithium_mmol,
                    lithium_mg,
                    lithium_ug_per_mg,
                ) = calculate_lithium_amounts(
                    relative_value,
                    reference_concentration_mol_li_kg,
                    reference_mass_mg,
                    sample_amounts_mg[index]
                    if sample_amounts_mg is not None
                    else None,
                )
            row.extend([
                "undefined" if lithium_mmol is None else f"{lithium_mmol:.6g}",
                "undefined" if lithium_mg is None else f"{lithium_mg:.6g}",
            ])
            if sample_amounts_mg is not None:
                row.append(
                    "undefined"
                    if lithium_ug_per_mg is None
                    else f"{lithium_ug_per_mg:.6g}"
                )
        rows.append(row)

    column_count = len(columns)
    max_file_lines = max(
        cell.count("\n") + 1 for cell in (row[0] for row in rows)
    )
    row_height = max(0.34, max_file_lines * 0.22)
    figure_width = max(8, column_count * 1.45)
    figure_height = max(3, (row_count + 1) * row_height + 1.8)
    fig, ax = plt.subplots(figsize=(figure_width, figure_height))
    ax.axis("off")
    title = f"Integrated intensities (reference: {os.path.basename(file_paths[reference_index])})"
    if reference_description:
        title += f"\nLithium quantification reference: {reference_description}"
    ax.set_title(title, pad=18)
    table = ax.table(
        cellText=rows,
        colLabels=columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(max(7, min(10, 11 - column_count * 0.5)))
    table.auto_set_column_width(col=list(range(column_count)))
    for cell in table.get_celld().values():
        cell.set_height(row_height / figure_height)
        cell.get_text().set_wrap(True)
        cell.get_text().set_verticalalignment("center")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.82, bottom=0.05)
    if show:
        plt.show()
    return fig


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
    show=True,
    return_figures=False,
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
    Returns:
    --------
    list of matplotlib.figure.Figure
        Figures created for the requested plot mode when ``return_figures`` is
        true. Otherwise, figures are shown and ``None`` is returned.
    """
    if not file_paths:
        raise ValueError("At least one spectrum is required for plotting.")
    if sample_amounts_mg is not None and len(sample_amounts_mg) != len(file_paths):
        raise ValueError("A sample mass is required for every plotted spectrum.")
    if sample_amounts_mg is not None and any(mass <= 0 for mass in sample_amounts_mg):
        raise ValueError("Sample masses must be greater than zero.")
    if custom_labels is not None and len(custom_labels) != len(file_paths):
        raise ValueError("A custom label is required for every plotted spectrum.")
    if x_limits is not None and x_limits[0] <= x_limits[1]:
        raise ValueError("x_limits must be provided as (high_ppm, low_ppm).")

    num_files = len(file_paths)
    figures = []
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
                    layer=idx, linewidth=0.8, label=label,
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
        figures.append(fig)
        if show:
            plt.show()
    
    elif plot_mode == "stacked":
        # Stack each file in its own subplot (vertical layout) within one figure
        # Useful to compare spectra aligned vertically while keeping x-axis shared
        if num_files == 0:
            print("No files to plot.")
            return figures if return_figures else None

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
                    layer=idx, linewidth=0.8, label=label,
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
        figures.append(fig)
        if show:
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
                figures.append(fig)
                if show:
                    plt.show()

            except ValueError as e:
                print(f"Warning: {e}")

    return figures if return_figures else None
