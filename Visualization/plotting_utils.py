"""
Plotting Utilities Service
==========================
Provides publication-quality plotting utilities and configuration for matplotlib.
Sets default styles, colors, and formatting for consistent visualizations.

Author: Materials Database Team
Date: February 2026
"""

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PUBLICATION-QUALITY DEFAULTS
# =============================================================================

# Use non-GUI backend for server environments (can be changed if needed)
# matplotlib.use('Agg')  # Uncomment if running without display

# Set publication-quality rcParams
PUBLICATION_PARAMS = {
    # Figure settings
    'figure.figsize': (10, 7),          # Default figure size (width, height) in inches
    'figure.dpi': 300,                   # High DPI for publication quality
    'figure.facecolor': 'white',         # White background
    'figure.edgecolor': 'white',
    'figure.autolayout': True,           # Automatic tight layout
    
    # Font settings
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'Liberation Sans'],
    'font.size': 12,                     # Base font size
    'font.weight': 'normal',
    
    # Axes settings
    'axes.titlesize': 14,                # Title font size
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,                # Axis label font size
    'axes.labelweight': 'bold',
    'axes.linewidth': 1.5,               # Axes border width
    'axes.grid': True,                   # Enable grid by default
    'axes.grid.axis': 'both',
    'axes.axisbelow': True,              # Grid below plot elements
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.spines.top': False,            # Hide top spine
    'axes.spines.right': False,          # Hide right spine
    
    # Grid settings
    'grid.alpha': 0.3,                   # Grid transparency
    'grid.linewidth': 0.8,
    'grid.linestyle': '--',
    'grid.color': 'gray',
    
    # Line settings
    'lines.linewidth': 2.0,              # Default line width
    'lines.markersize': 8,               # Default marker size
    'lines.markeredgewidth': 1.5,
    
    # Scatter plot settings
    'scatter.marker': 'o',
    'scatter.edgecolors': 'black',
    
    # Legend settings
    'legend.fontsize': 11,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.facecolor': 'white',
    'legend.edgecolor': 'black',
    'legend.fancybox': True,
    'legend.shadow': False,
    'legend.loc': 'best',
    
    # Tick settings
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.minor.size': 3,
    'ytick.minor.size': 3,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'xtick.minor.width': 1.0,
    'ytick.minor.width': 1.0,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    
    # Save settings
    'savefig.dpi': 300,                  # DPI for saved figures
    'savefig.format': 'png',             # Default save format
    'savefig.bbox': 'tight',             # Tight bounding box
    'savefig.pad_inches': 0.1,           # Padding around figure
    'savefig.transparent': False,
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'white',
}

# Color palettes for different plot types
COLOR_PALETTES = {
    'default': sns.color_palette('deep', 10),
    'materials': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'sequential': sns.color_palette('viridis', 10),
    'diverging': sns.color_palette('RdBu_r', 10),
    'categorical': sns.color_palette('Set2', 8),
    'pastel': sns.color_palette('pastel', 10),
}

# Material-specific colors (can be extended)
MATERIAL_COLORS = {
    'Aluminum': '#1f77b4',
    'Copper': '#ff7f0e',
    'Steel': '#2ca02c',
    'Titanium': '#d62728',
    'Iron': '#9467bd',
    'Nickel': '#8c564b',
    'Gold': '#FFD700',
    'Silver': '#C0C0C0',
}

# Line styles for multiple curves
LINE_STYLES = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]

# Marker styles
MARKER_STYLES = ['o', 's', '^', 'v', 'D', 'p', '*', 'h', '<', '>']


class PlottingUtils:
    """
    Utility class for creating publication-quality plots.
    Provides consistent styling and helper functions for common plot types.
    """
    
    def __init__(self, style: str = 'publication'):
        """
        Initialize plotting utilities with specified style.
        
        Args:
            style: Plot style ('publication', 'presentation', 'notebook')
        """
        self.style = style
        self.apply_style(style)
        logger.info(f"✓ PlottingUtils initialized with '{style}' style")
    
    def apply_style(self, style: str = 'publication'):
        """
        Apply predefined plotting style.
        
        Args:
            style: Style name
                - 'publication': High-quality for papers/journals
                - 'presentation': Larger fonts for presentations
                - 'notebook': Optimized for Jupyter notebooks
        """
        if style == 'publication':
            plt.rcParams.update(PUBLICATION_PARAMS)
            sns.set_style('whitegrid')
            
        elif style == 'presentation':
            # Larger fonts for presentations
            params = PUBLICATION_PARAMS.copy()
            params.update({
                'figure.figsize': (12, 8),
                'font.size': 16,
                'axes.titlesize': 20,
                'axes.labelsize': 16,
                'legend.fontsize': 14,
                'xtick.labelsize': 14,
                'ytick.labelsize': 14,
                'lines.linewidth': 3.0,
            })
            plt.rcParams.update(params)
            sns.set_style('whitegrid')
            
        elif style == 'notebook':
            # Optimized for Jupyter notebooks
            params = PUBLICATION_PARAMS.copy()
            params.update({
                'figure.figsize': (10, 6),
                'figure.dpi': 100,  # Lower DPI for faster rendering
                'savefig.dpi': 150,
            })
            plt.rcParams.update(params)
            sns.set_style('whitegrid')
            
        else:
            logger.warning(f"Unknown style '{style}', using 'publication'")
            self.apply_style('publication')
        
        logger.info(f"Applied '{style}' plotting style")
    
    def get_color_palette(self, name: str = 'default', n_colors: int = 10) -> List:
        """
        Get color palette for plotting.
        
        Args:
            name: Palette name ('default', 'materials', 'sequential', 'diverging', etc.)
            n_colors: Number of colors to return
            
        Returns:
            List of colors
        """
        if name in COLOR_PALETTES:
            palette = COLOR_PALETTES[name]
            if len(palette) < n_colors:
                # Extend palette if needed - use seaborn palette names
                palette_map = {
                    'default': 'deep',
                    'materials': 'deep',
                    'sequential': 'viridis',
                    'diverging': 'RdBu_r',
                    'categorical': 'Set2',
                    'pastel': 'pastel'
                }
                sns_name = palette_map.get(name, 'deep')
                palette = sns.color_palette(sns_name, n_colors)
            return palette[:n_colors]
        else:
            logger.warning(f"Unknown palette '{name}', using 'default'")
            return sns.color_palette('deep', n_colors)
    
    def get_material_color(self, material_name: str) -> str:
        """
        Get color for specific material.
        
        Args:
            material_name: Name of material
            
        Returns:
            Color as hex string
        """
        return MATERIAL_COLORS.get(material_name, '#1f77b4')  # Default blue
    
    def get_line_style(self, index: int) -> str:
        """
        Get line style by index (cycles through available styles).
        
        Args:
            index: Line index
            
        Returns:
            Line style string
        """
        return LINE_STYLES[index % len(LINE_STYLES)]
    
    def get_marker_style(self, index: int) -> str:
        """
        Get marker style by index (cycles through available markers).
        
        Args:
            index: Marker index
            
        Returns:
            Marker style string
        """
        return MARKER_STYLES[index % len(MARKER_STYLES)]
    
    def configure_axes(
        self,
        ax: plt.Axes,
        xlabel: str = '',
        ylabel: str = '',
        title: str = '',
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = None,
        xlog: bool = False,
        ylog: bool = False,
        grid: bool = True
    ) -> plt.Axes:
        """
        Configure axes with labels, limits, and scales.
        
        Args:
            ax: Matplotlib axes object
            xlabel: X-axis label
            ylabel: Y-axis label
            title: Plot title
            xlim: X-axis limits (min, max)
            ylim: Y-axis limits (min, max)
            xlog: Use logarithmic scale for x-axis
            ylog: Use logarithmic scale for y-axis
            grid: Show grid
            
        Returns:
            Configured axes object
        """
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        if title:
            ax.set_title(title)
        
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')
        
        ax.grid(grid)
        
        return ax
    
    def add_legend(
        self,
        ax: plt.Axes,
        loc: str = 'best',
        ncol: int = 1,
        frameon: bool = True,
        title: Optional[str] = None
    ) -> plt.Axes:
        """
        Add legend to axes with publication-quality formatting.
        
        Args:
            ax: Matplotlib axes object
            loc: Legend location
            ncol: Number of columns
            frameon: Show frame around legend
            title: Legend title
            
        Returns:
            Axes with legend
        """
        legend = ax.legend(
            loc=loc,
            ncol=ncol,
            frameon=frameon,
            title=title,
            fancybox=True,
            shadow=False
        )
        
        # Make legend frame slightly transparent
        if frameon:
            legend.get_frame().set_alpha(0.9)
        
        return ax
    
    def save_figure(
        self,
        fig: plt.Figure,
        filename: str,
        dpi: int = 300,
        format: str = 'png',
        transparent: bool = False
    ):
        """
        Save figure with publication-quality settings.
        
        Args:
            fig: Matplotlib figure object
            filename: Output filename (with or without extension)
            dpi: Resolution in dots per inch
            format: Output format ('png', 'pdf', 'svg', 'eps')
            transparent: Transparent background
        """
        # Add extension if not present
        if not filename.endswith(f'.{format}'):
            filename = f'{filename}.{format}'
        
        fig.savefig(
            filename,
            dpi=dpi,
            format=format,
            bbox_inches='tight',
            transparent=transparent,
            facecolor='white' if not transparent else 'none',
            edgecolor='none'
        )
        
        logger.info(f"Saved figure to: {filename} ({format}, {dpi} DPI)")
    
    def create_figure(
        self,
        nrows: int = 1,
        ncols: int = 1,
        figsize: Optional[Tuple[float, float]] = None,
        **kwargs
    ) -> Tuple[plt.Figure, Union[plt.Axes, np.ndarray]]:
        """
        Create figure and axes with publication-quality settings.
        
        Args:
            nrows: Number of subplot rows
            ncols: Number of subplot columns
            figsize: Figure size (width, height) in inches
            **kwargs: Additional arguments passed to plt.subplots()
            
        Returns:
            Tuple of (figure, axes)
        """
        if figsize is None:
            figsize = plt.rcParams['figure.figsize']
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
        
        logger.debug(f"Created figure: {nrows}x{ncols}, size={figsize}")
        
        return fig, axes
    
    def reset_style(self):
        """Reset matplotlib to default settings."""
        plt.rcdefaults()
        sns.reset_defaults()
        logger.info("Reset plotting style to defaults")


# =============================================================================
# MODULE-LEVEL HELPER FUNCTIONS
# =============================================================================

def apply_publication_style():
    """
    Apply publication-quality style to all plots.
    Convenience function for quick setup.
    """
    plt.rcParams.update(PUBLICATION_PARAMS)
    sns.set_style('whitegrid')
    logger.info("✓ Applied publication style globally")


def get_figure_with_style(
    nrows: int = 1,
    ncols: int = 1,
    style: str = 'publication'
) -> Tuple[plt.Figure, Union[plt.Axes, np.ndarray]]:
    """
    Quick function to create figure with specific style.
    
    Args:
        nrows: Number of rows
        ncols: Number of columns
        style: Style name
        
    Returns:
        Tuple of (figure, axes)
    """
    utils = PlottingUtils(style=style)
    return utils.create_figure(nrows, ncols)


# Initialize default style on module import
apply_publication_style()


if __name__ == "__main__":
    # Example usage and testing
    print("="*75)
    print("PLOTTING UTILITIES - EXAMPLE USAGE")
    print("="*75)
    print()
    
    # Create plotting utils instance
    utils = PlottingUtils(style='publication')
    
    # Example 1: Create simple plot
    print("1. Creating sample publication-quality plot...")
    fig, ax = utils.create_figure(figsize=(8, 6))
    
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Plot with different styles
    ax.plot(x, y1, label='sin(x)', linewidth=2, color=utils.get_color_palette('materials')[0])
    ax.plot(x, y2, label='cos(x)', linewidth=2, linestyle='--', 
            color=utils.get_color_palette('materials')[1])
    
    # Configure axes
    utils.configure_axes(
        ax,
        xlabel='X Values',
        ylabel='Y Values',
        title='Sample Publication-Quality Plot',
        xlim=(0, 10),
        ylim=(-1.5, 1.5)
    )
    
    # Add legend
    utils.add_legend(ax, loc='upper right')
    
    # Save figure
    utils.save_figure(fig, 'sample_plot_test', dpi=300, format='png')
    print("   ✓ Created and saved sample_plot_test.png")
    plt.close(fig)
    print()
    
    # Example 2: Color palettes
    print("2. Available color palettes:")
    for palette_name in COLOR_PALETTES.keys():
        print(f"   • {palette_name}")
    print()
    
    # Example 3: Material colors
    print("3. Predefined material colors:")
    for material, color in MATERIAL_COLORS.items():
        print(f"   • {material}: {color}")
    print()
    
    # Example 4: Style options
    print("4. Available styles:")
    print("   • publication (default)")
    print("   • presentation")
    print("   • notebook")
    print()
    
    print("="*75)
    print("✓ Plotting utilities initialized and tested")
    print("="*75)
