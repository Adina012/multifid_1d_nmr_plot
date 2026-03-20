"""
NMR Spectra Plotter - Main Application
A GUI-based tool for plotting 1D NMR spectra with customizable options.

Author: Adina
Date: December 2025
"""
import tkinter as tk
from nmr_gui import NMRPlotterGUI

def main():
    """Launch the NMR Plotter GUI application."""
    root = tk.Tk()
    app = NMRPlotterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
