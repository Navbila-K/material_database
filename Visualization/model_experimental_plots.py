"""
Model vs Experimental Overlay Plotting Functions
Provides visualization functions for comparing theoretical models with experimental data.

This module implements Task 3.3: Model + Experimental Overlay Plot
- Overlay plots showing model curves and experimental points
- Theme customization (light/dark mode)
- Plot annotations for parameters and references

Author: Materials Database Team
Date: 2026-02-22
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.plotting_utils import PlottingUtils, apply_publication_style

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Theme configurations
LIGHT_THEME = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.labelcolor': 'black',
    'text.color': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'grid.color': '#CCCCCC',
    'legend.facecolor': 'white',
    'legend.edgecolor': 'black',
    'model_color': '#1f77b4',  # Blue
    'exp_color': '#d62728',    # Red
    'annotation_bg': 'lightyellow'
}

DARK_THEME = {
    'figure.facecolor': '#2E2E2E',
    'axes.facecolor': '#1E1E1E',
    'axes.edgecolor': '#CCCCCC',
    'axes.labelcolor': 'white',
    'text.color': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'grid.color': '#555555',
    'legend.facecolor': '#2E2E2E',
    'legend.edgecolor': '#CCCCCC',
    'model_color': '#4A9EFF',  # Lighter Blue
    'exp_color': '#FF6B6B',    # Lighter Red
    'annotation_bg': '#3E3E3E'
}


def customize_plot_theme(dark_mode: bool = False) -> Dict[str, Any]:
    """
    Get plot theme configuration for light or dark mode.
    Supports matching GUI theme for consistent appearance.
    
    Args:
        dark_mode: If True, return dark theme. If False, return light theme.
    
    Returns:
        Dictionary with theme parameters for matplotlib rcParams
    
    Example:
        >>> theme = customize_plot_theme(dark_mode=True)
        >>> plt.rcParams.update(theme)
        >>> # Now all plots will use dark theme
    """
    theme = DARK_THEME.copy() if dark_mode else LIGHT_THEME.copy()
    
    logger.info(f"✓ Theme configured: {'Dark' if dark_mode else 'Light'} mode")
    return theme


def apply_theme_to_figure(fig: plt.Figure, theme: Dict[str, Any]) -> None:
    """
    Apply theme to an existing figure.
    
    Args:
        fig: Matplotlib figure object
        theme: Theme dictionary from customize_plot_theme()
    """
    fig.patch.set_facecolor(theme['figure.facecolor'])
    
    for ax in fig.axes:
        ax.set_facecolor(theme['axes.facecolor'])
        ax.spines['bottom'].set_color(theme['axes.edgecolor'])
        ax.spines['top'].set_color(theme['axes.edgecolor'])
        ax.spines['left'].set_color(theme['axes.edgecolor'])
        ax.spines['right'].set_color(theme['axes.edgecolor'])
        ax.xaxis.label.set_color(theme['axes.labelcolor'])
        ax.yaxis.label.set_color(theme['axes.labelcolor'])
        ax.title.set_color(theme['text.color'])
        ax.tick_params(axis='x', colors=theme['xtick.color'])
        ax.tick_params(axis='y', colors=theme['ytick.color'])
        
        # Update grid color
        if ax.get_xgridlines():
            for line in ax.get_xgridlines():
                line.set_color(theme['grid.color'])
        if ax.get_ygridlines():
            for line in ax.get_ygridlines():
                line.set_color(theme['grid.color'])
        
        # Update legend if present
        legend = ax.get_legend()
        if legend:
            legend.get_frame().set_facecolor(theme['legend.facecolor'])
            legend.get_frame().set_edgecolor(theme['legend.edgecolor'])
            for text in legend.get_texts():
                text.set_color(theme['text.color'])


def add_plot_annotations(
    ax: plt.Axes,
    annotations: List[Dict[str, Any]],
    theme: Optional[Dict[str, Any]] = None
) -> None:
    """
    Add text boxes with model parameters, references, or other annotations to plot.
    
    Args:
        ax: Matplotlib axes object to annotate
        annotations: List of annotation dictionaries with:
            - text: str (required) - Text to display
            - position: tuple (optional) - (x, y) in axes coordinates (0-1)
            - box_style: str (optional) - 'round', 'square', 'roundtooth', etc.
            - font_size: int (optional) - Font size
            - color: str (optional) - Text color
            - bg_color: str (optional) - Background color
        theme: Optional theme dictionary for styling
    
    Example:
        >>> annotations = [
        ...     {'text': 'C₀ = 3940 m/s\\ns = 1.489', 'position': (0.05, 0.95)},
        ...     {'text': 'Ref: [107]', 'position': (0.95, 0.05)}
        ... ]
        >>> add_plot_annotations(ax, annotations)
    """
    if theme is None:
        theme = LIGHT_THEME
    
    default_position = (0.05, 0.95)
    default_box_style = 'round,pad=0.5'
    default_font_size = 10
    
    for i, annot in enumerate(annotations):
        if not isinstance(annot, dict) or 'text' not in annot:
            logger.warning(f"Skipping invalid annotation {i}: {annot}")
            continue
        
        text = annot.get('text', '')
        position = annot.get('position', (default_position[0], default_position[1] - i * 0.15))
        box_style = annot.get('box_style', default_box_style)
        font_size = annot.get('font_size', default_font_size)
        text_color = annot.get('color', theme.get('text.color', 'black'))
        bg_color = annot.get('bg_color', theme.get('annotation_bg', 'lightyellow'))
        
        # Create text box
        bbox_props = dict(
            boxstyle=box_style,
            facecolor=bg_color,
            edgecolor=theme.get('axes.edgecolor', 'black'),
            alpha=0.9,
            linewidth=1.5
        )
        
        ax.text(
            position[0], position[1],
            text,
            transform=ax.transAxes,
            fontsize=font_size,
            verticalalignment='top',
            horizontalalignment='left',
            bbox=bbox_props,
            color=text_color,
            fontweight='bold',
            zorder=10
        )
    
    logger.info(f"✓ Added {len(annotations)} annotations to plot")


def plot_model_vs_experimental(
    model_curve: Dict[str, np.ndarray],
    exp_data: Dict[str, np.ndarray],
    metadata: Optional[Dict[str, Any]] = None,
    figsize: Tuple[float, float] = (10, 8),
    style: str = 'publication',
    dark_mode: bool = False,
    show_equation: bool = True,
    show_references: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create overlay plot comparing theoretical model curve with experimental data.
    
    Args:
        model_curve: Dict with 'x' and 'y' arrays for model curve
            Example: {'x': array([0, 1, 2, ...]), 'y': array([0, 1.5, 3, ...])}
        exp_data: Dict with 'x' and 'y' arrays for experimental points
            Example: {'x': array([0.5, 1.5, ...]), 'y': array([0.7, 2.1, ...])}
        metadata: Optional dict with:
            - title: str - Plot title
            - xlabel: str - X-axis label
            - ylabel: str - Y-axis label
            - model_name: str - Name of model (e.g., 'US-Up Linear', 'Mie-Gruneisen')
            - model_equation: str - Equation string for legend (e.g., 'Uₛ = C₀ + s·Uₚ')
            - model_params: dict - Model parameters (e.g., {'C₀': 3940, 's': 1.489})
            - exp_source: str - Experimental data source
            - references: list - Reference citations
            - material: str - Material name
        figsize: Figure size (width, height) in inches
        style: Plotting style ('publication', 'presentation', 'notebook')
        dark_mode: If True, use dark theme
        show_equation: If True, show model equation in legend
        show_references: If True, add reference citations in caption
        save_path: Optional path to save figure
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> # US-Up plot
        >>> model_curve = {
        ...     'x': np.linspace(0, 3000, 100),
        ...     'y': 3940 + 1.489 * np.linspace(0, 3000, 100)
        ... }
        >>> exp_data = {
        ...     'x': np.array([500, 1000, 1500, 2000]),
        ...     'y': np.array([4685, 5429, 6173, 6917])
        ... }
        >>> metadata = {
        ...     'title': 'Copper Hugoniot',
        ...     'xlabel': 'Particle Velocity Uₚ (m/s)',
        ...     'ylabel': 'Shock Velocity Uₛ (m/s)',
        ...     'model_name': 'US-Up Linear',
        ...     'model_equation': 'Uₛ = 3940 + 1.489·Uₚ',
        ...     'exp_source': 'LASL Shock Hugoniot Data'
        ... }
        >>> fig = plot_model_vs_experimental(model_curve, exp_data, metadata)
    """
    # Initialize plotting utilities
    plotter = PlottingUtils(style=style)
    
    # Get theme
    theme = customize_plot_theme(dark_mode=dark_mode)
    
    # Create figure
    fig, ax = plotter.create_figure(nrows=1, ncols=1, figsize=figsize)
    
    # Apply theme
    apply_theme_to_figure(fig, theme)
    
    # Extract metadata with defaults
    if metadata is None:
        metadata = {}
    
    title = metadata.get('title', 'Model vs Experimental Data')
    xlabel = metadata.get('xlabel', 'X')
    ylabel = metadata.get('ylabel', 'Y')
    model_name = metadata.get('model_name', 'Model')
    model_equation = metadata.get('model_equation', '')
    exp_source = metadata.get('exp_source', 'Experimental Data')
    references = metadata.get('references', [])
    material = metadata.get('material', '')
    model_params = metadata.get('model_params', {})
    
    # Plot model curve - Blue solid line
    model_x = model_curve.get('x', np.array([]))
    model_y = model_curve.get('y', np.array([]))
    
    if len(model_x) > 0 and len(model_y) > 0:
        model_label = model_name
        if show_equation and model_equation:
            model_label = f"{model_name}: {model_equation}"
        
        ax.plot(
            model_x, model_y,
            color=theme['model_color'],
            linestyle='-',
            linewidth=2.5,
            label=model_label,
            zorder=2
        )
        logger.info(f"✓ Plotted model curve: {len(model_x)} points")
    
    # Plot experimental data - Red scatter points
    exp_x = exp_data.get('x', np.array([]))
    exp_y = exp_data.get('y', np.array([]))
    exp_labels = exp_data.get('labels', None)  # Optional point labels
    
    if len(exp_x) > 0 and len(exp_y) > 0:
        ax.scatter(
            exp_x, exp_y,
            color=theme['exp_color'],
            marker='o',
            s=100,
            alpha=0.8,
            edgecolors='black',
            linewidths=1.5,
            label=exp_source,
            zorder=3
        )
        logger.info(f"✓ Plotted experimental data: {len(exp_x)} points")
        
        # Add point labels if provided
        if exp_labels is not None and len(exp_labels) == len(exp_x):
            for i, (x, y, label) in enumerate(zip(exp_x, exp_y, exp_labels)):
                ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=8,
                    color=theme['text.color'],
                    alpha=0.7
                )
    
    # Configure axes
    plotter.configure_axes(
        ax,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        grid=True
    )
    
    # Add legend with model equation
    legend = ax.legend(
        loc='lower right',
        frameon=True,
        framealpha=0.95,
        fontsize=11,
        edgecolor=theme['legend.edgecolor'],
        facecolor=theme['legend.facecolor']
    )
    
    # Set legend text color
    for text in legend.get_texts():
        text.set_color(theme['text.color'])
    
    # Add annotations for model parameters
    annotations = []
    
    if model_params:
        param_text = '\n'.join([f"{key} = {value}" for key, value in model_params.items()])
        annotations.append({
            'text': param_text,
            'position': (0.05, 0.95),
            'font_size': 10,
            'bg_color': theme['annotation_bg']
        })
    
    if annotations:
        add_plot_annotations(ax, annotations, theme)
    
    # Add reference citations in caption
    if show_references and references:
        ref_text = "References: " + ", ".join([f"[{ref}]" for ref in references])
        fig.text(
            0.5, 0.02,
            ref_text,
            ha='center',
            fontsize=9,
            style='italic',
            color=theme['text.color']
        )
        logger.info(f"✓ Added {len(references)} references to caption")
    
    plt.tight_layout()
    
    # Adjust for reference caption
    if show_references and references:
        plt.subplots_adjust(bottom=0.08)
    
    # Save if requested
    if save_path:
        plotter.save_figure(fig, save_path)
        logger.info(f"Saved model vs experimental plot to: {save_path}")
    
    logger.info(f"✓ Created model vs experimental overlay plot: {title}")
    return fig


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON PLOT TYPES
# ============================================================================

def plot_usup_hugoniot(
    c0: float,
    s: float,
    exp_data: Dict[str, np.ndarray],
    material: str,
    references: Optional[List[str]] = None,
    dark_mode: bool = False,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Convenience function for US-Up Hugoniot plots.
    
    Args:
        c0: Bulk sound speed (m/s)
        s: Hugoniot slope parameter
        exp_data: Experimental data dict with 'x' (Up) and 'y' (Us)
        material: Material name
        references: Optional list of reference citations
        dark_mode: If True, use dark theme
        save_path: Optional path to save figure
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> exp_data = {'x': np.array([500, 1000]), 'y': np.array([4685, 5429])}
        >>> fig = plot_usup_hugoniot(3940, 1.489, exp_data, 'Copper', ['107'])
    """
    # Generate model curve
    if 'x' in exp_data and len(exp_data['x']) > 0:
        up_min = 0
        up_max = max(exp_data['x']) * 1.2
    else:
        up_min = 0
        up_max = 3000
    
    up_model = np.linspace(up_min, up_max, 200)
    us_model = c0 + s * up_model
    
    model_curve = {'x': up_model, 'y': us_model}
    
    metadata = {
        'title': f'{material} Hugoniot (US-Up)',
        'xlabel': 'Particle Velocity Uₚ (m/s)',
        'ylabel': 'Shock Velocity Uₛ (m/s)',
        'model_name': 'US-Up Linear',
        'model_equation': f'Uₛ = {c0:.0f} + {s:.3f}·Uₚ',
        'model_params': {'C₀ (m/s)': f'{c0:.0f}', 's': f'{s:.3f}'},
        'exp_source': 'Experimental Data',
        'references': references or [],
        'material': material
    }
    
    return plot_model_vs_experimental(
        model_curve=model_curve,
        exp_data=exp_data,
        metadata=metadata,
        dark_mode=dark_mode,
        save_path=save_path
    )


def plot_eos_comparison(
    pressure: np.ndarray,
    volume_model: np.ndarray,
    volume_exp: Optional[np.ndarray] = None,
    material: str = '',
    model_name: str = 'EOS Model',
    dark_mode: bool = False,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Convenience function for Equation of State (P-V) comparison plots.
    
    Args:
        pressure: Pressure array (GPa)
        volume_model: Specific volume from model (cm³/g)
        volume_exp: Optional experimental volume data
        material: Material name
        model_name: Name of EOS model
        dark_mode: If True, use dark theme
        save_path: Optional path to save figure
    
    Returns:
        matplotlib Figure object
    """
    model_curve = {'x': pressure, 'y': volume_model}
    
    if volume_exp is not None and len(volume_exp) == len(pressure):
        exp_data = {'x': pressure, 'y': volume_exp}
    else:
        exp_data = {'x': np.array([]), 'y': np.array([])}
    
    metadata = {
        'title': f'{material} Equation of State' if material else 'Equation of State',
        'xlabel': 'Pressure (GPa)',
        'ylabel': 'Specific Volume (cm³/g)',
        'model_name': model_name,
        'exp_source': 'Experimental Data',
        'material': material
    }
    
    return plot_model_vs_experimental(
        model_curve=model_curve,
        exp_data=exp_data,
        metadata=metadata,
        dark_mode=dark_mode,
        save_path=save_path
    )


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def demo_model_experimental_plots():
    """
    Demonstration of model vs experimental plotting functions.
    Creates sample plots using synthetic data.
    """
    print("\n" + "="*70)
    print("MODEL VS EXPERIMENTAL PLOTS - DEMONSTRATION")
    print("="*70 + "\n")
    
    # Test 1: US-Up Hugoniot plot (Light mode)
    print("Test 1: US-Up Hugoniot plot (Light mode)...")
    
    # Model: Us = C0 + s * Up
    c0 = 3940  # m/s
    s = 1.489
    up_model = np.linspace(0, 3000, 200)
    us_model = c0 + s * up_model
    
    model_curve = {'x': up_model, 'y': us_model}
    
    # Experimental data (synthetic)
    up_exp = np.array([500, 1000, 1500, 2000, 2500])
    us_exp = c0 + s * up_exp + np.random.normal(0, 50, 5)  # Add some noise
    
    exp_data = {'x': up_exp, 'y': us_exp}
    
    metadata = {
        'title': 'Copper Hugoniot (US-Up)',
        'xlabel': 'Particle Velocity Uₚ (m/s)',
        'ylabel': 'Shock Velocity Uₛ (m/s)',
        'model_name': 'US-Up Linear',
        'model_equation': f'Uₛ = {c0} + {s}·Uₚ',
        'model_params': {'C₀ (m/s)': f'{c0}', 's': f'{s}'},
        'exp_source': 'LASL Shock Hugoniot Data',
        'references': ['107', 'Marsh1980'],
        'material': 'Copper'
    }
    
    fig1 = plot_model_vs_experimental(
        model_curve=model_curve,
        exp_data=exp_data,
        metadata=metadata,
        dark_mode=False,
        save_path='demo_model_exp_light.png'
    )
    print("✓ Light mode plot created\n")
    plt.close(fig1)
    
    # Test 2: Same plot in Dark mode
    print("Test 2: US-Up Hugoniot plot (Dark mode)...")
    
    fig2 = plot_model_vs_experimental(
        model_curve=model_curve,
        exp_data=exp_data,
        metadata=metadata,
        dark_mode=True,
        save_path='demo_model_exp_dark.png'
    )
    print("✓ Dark mode plot created\n")
    plt.close(fig2)
    
    # Test 3: Theme customization
    print("Test 3: Testing theme customization...")
    light_theme = customize_plot_theme(dark_mode=False)
    dark_theme = customize_plot_theme(dark_mode=True)
    print(f"✓ Light theme: {len(light_theme)} parameters")
    print(f"✓ Dark theme: {len(dark_theme)} parameters\n")
    
    # Test 4: Custom annotations
    print("Test 4: Testing plot annotations...")
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    ax3.plot([0, 1, 2], [0, 1, 4], 'b-')
    
    annotations = [
        {
            'text': 'Model Parameters:\nC₀ = 3940 m/s\ns = 1.489',
            'position': (0.05, 0.95),
            'font_size': 10
        },
        {
            'text': 'Reference: [107]',
            'position': (0.95, 0.05),
            'font_size': 9,
            'box_style': 'square,pad=0.3'
        }
    ]
    
    add_plot_annotations(ax3, annotations)
    plt.savefig('demo_annotations.png', dpi=300, bbox_inches='tight')
    print("✓ Annotations added\n")
    plt.close(fig3)
    
    # Test 5: Convenience function for US-Up
    print("Test 5: Testing US-Up convenience function...")
    fig4 = plot_usup_hugoniot(
        c0=3940,
        s=1.489,
        exp_data={'x': up_exp, 'y': us_exp},
        material='Copper',
        references=['107', 'LASL'],
        save_path='demo_usup_convenience.png'
    )
    print("✓ US-Up convenience plot created\n")
    plt.close(fig4)
    
    # Test 6: EOS comparison
    print("Test 6: Testing EOS comparison plot...")
    pressure = np.linspace(0, 100, 50)  # GPa
    volume_model = 0.112 / (1 + pressure / 100)  # Simple compression model
    volume_exp = volume_model + np.random.normal(0, 0.002, 50)  # Add noise
    
    fig5 = plot_eos_comparison(
        pressure=pressure,
        volume_model=volume_model,
        volume_exp=volume_exp,
        material='Copper',
        model_name='Mie-Gruneisen',
        save_path='demo_eos_comparison.png'
    )
    print("✓ EOS comparison plot created\n")
    plt.close(fig5)
    
    print("="*70)
    print("✓✓✓ ALL DEMONSTRATIONS COMPLETED ✓✓✓")
    print("="*70)
    print("\nGenerated files:")
    print("  • demo_model_exp_light.png (Light theme)")
    print("  • demo_model_exp_dark.png (Dark theme)")
    print("  • demo_annotations.png (Annotations example)")
    print("  • demo_usup_convenience.png (US-Up convenience function)")
    print("  • demo_eos_comparison.png (EOS comparison)")
    print()


if __name__ == "__main__":
    # Run demonstration
    demo_model_experimental_plots()
