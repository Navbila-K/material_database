"""
Property Comparison Plotting Functions
Provides visualization functions for comparing material properties across multiple materials.

This module implements Task 3.2: Property Comparison Plots
- Grouped bar charts for property comparison
- Styled tables for property data
- Scatter plots for property relationships

Author: Materials Database Team
Date: 2026-02-22
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
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


def plot_property_comparison_bar(
    materials: List[str],
    properties: List[str],
    data: Dict[str, Dict[str, Union[float, str]]],
    units: Optional[Dict[str, str]] = None,
    figsize: Optional[Tuple[float, float]] = None,
    style: str = 'publication',
    show_values: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create grouped bar chart comparing properties across materials.
    
    Args:
        materials: List of material names
        properties: List of property names to compare
        data: Nested dict {material_name: {property_name: value}}
        units: Dict mapping property names to units (for y-axis label)
        figsize: Figure size (width, height) in inches
        style: Plotting style ('publication', 'presentation', 'notebook')
        show_values: If True, display values on top of bars
        save_path: Optional path to save figure
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> materials = ['Aluminum', 'Copper', 'Steel']
        >>> properties = ['Density', 'Melting Temperature']
        >>> data = {
        ...     'Aluminum': {'Density': 2700, 'Melting Temperature': 933},
        ...     'Copper': {'Density': 8960, 'Melting Temperature': 1358},
        ...     'Steel': {'Density': 7850, 'Melting Temperature': 1811}
        ... }
        >>> fig = plot_property_comparison_bar(materials, properties, data)
    """
    # Initialize plotting utilities
    plotter = PlottingUtils(style=style)
    
    # Determine figure size
    if figsize is None:
        # Adaptive sizing based on number of materials and properties
        width = max(8, 2 * len(materials))
        height = max(6, 1.5 * len(properties))
        figsize = (width, height)
    
    # Create figure
    fig, axes = plotter.create_figure(
        nrows=len(properties),
        ncols=1,
        figsize=figsize
    )
    
    # Handle single property case (axes is not array)
    if len(properties) == 1:
        axes = [axes]
    
    # Get color palette for materials
    colors = plotter.get_color_palette('materials', len(materials))
    
    # Bar width and positions
    x = np.arange(len(materials))
    
    # Plot each property in its own subplot
    for idx, prop in enumerate(properties):
        ax = axes[idx]
        
        # Extract values for this property
        values = []
        valid_materials = []
        
        for mat in materials:
            if mat in data and prop in data[mat]:
                val = data[mat][prop]
                # Convert to float if it's a string
                if isinstance(val, str):
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = None
                
                if val is not None:
                    values.append(val)
                    valid_materials.append(mat)
                else:
                    values.append(0)
                    valid_materials.append(mat)
            else:
                values.append(0)
                valid_materials.append(mat)
        
        # Create bars
        bars = ax.bar(x, values, color=colors[:len(materials)], alpha=0.85, edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        if show_values and any(v != 0 for v in values):
            for i, (bar, val) in enumerate(zip(bars, values)):
                if val > 0:
                    height = bar.get_height()
                    # Format value based on magnitude
                    if val >= 1000:
                        label = f'{val:.0f}'
                    elif val >= 10:
                        label = f'{val:.1f}'
                    else:
                        label = f'{val:.2f}'
                    
                    ax.text(
                        bar.get_x() + bar.get_width() / 2, height,
                        label,
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold'
                    )
        
        # Configure axes
        unit_str = units.get(prop, '') if units else ''
        y_label = f"{prop} ({unit_str})" if unit_str else prop
        
        plotter.configure_axes(
            ax,
            xlabel='',
            ylabel=y_label,
            title=f'{prop} Comparison',
            grid=True
        )
        
        # Set x-ticks to material names
        ax.set_xticks(x)
        ax.set_xticklabels(valid_materials, rotation=45, ha='right')
        
        # Add gridlines only on y-axis
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
    
    # Overall title
    if len(properties) > 1:
        fig.suptitle('Property Comparison Across Materials', fontsize=16, fontweight='bold', y=0.995)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plotter.save_figure(fig, save_path)
        logger.info(f"Saved bar chart to: {save_path}")
    
    logger.info(f"✓ Created bar chart comparing {len(properties)} properties across {len(materials)} materials")
    return fig


def plot_property_comparison_table(
    materials: List[str],
    properties: List[str],
    data: Dict[str, Dict[str, Any]],
    units: Optional[Dict[str, str]] = None,
    figsize: Optional[Tuple[float, float]] = None,
    style: str = 'publication',
    color_scale: bool = True,
    save_html: Optional[str] = None,
    save_png: Optional[str] = None
) -> Tuple[pd.DataFrame, plt.Figure]:
    """
    Create styled DataFrame table with color-coded cells for property comparison.
    
    Args:
        materials: List of material names
        properties: List of property names
        data: Nested dict {material_name: {property_name: value}}
        units: Dict mapping property names to units (shown in column headers)
        figsize: Figure size for PNG export
        style: Plotting style ('publication', 'presentation', 'notebook')
        color_scale: If True, color-code cells based on values
        save_html: Optional path to save HTML table
        save_png: Optional path to save PNG image
    
    Returns:
        Tuple of (pandas DataFrame, matplotlib Figure)
    
    Example:
        >>> df, fig = plot_property_comparison_table(materials, properties, data)
        >>> df.to_html('comparison_table.html')
    """
    # Build DataFrame
    table_data = {}
    
    for prop in properties:
        column_values = []
        for mat in materials:
            if mat in data and prop in data[mat]:
                val = data[mat][prop]
                # Handle dict format (with value, unit, ref)
                if isinstance(val, dict):
                    val = val.get('value', '')
                column_values.append(val)
            else:
                column_values.append('N/A')
        
        # Add units to column name
        col_name = f"{prop}\n({units[prop]})" if units and prop in units else prop
        table_data[col_name] = column_values
    
    # Create DataFrame
    df = pd.DataFrame(table_data, index=materials)
    
    # Convert numeric strings to floats for color scaling
    df_numeric = df.copy()
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
    
    # Create figure for PNG export
    plotter = PlottingUtils(style=style)
    
    if figsize is None:
        # Adaptive sizing
        width = max(10, 2 * len(properties))
        height = max(6, 0.8 * len(materials) + 2)
        figsize = (width, height)
    
    fig, ax = plotter.create_figure(nrows=1, ncols=1, figsize=figsize)
    ax.axis('off')
    
    # Create table
    if color_scale:
        # Normalize values for color mapping (per column)
        cell_colors = []
        cmap = plt.cm.RdYlGn  # Red-Yellow-Green colormap
        
        for i, mat in enumerate(materials):
            row_colors = []
            for j, col in enumerate(df.columns):
                val = df_numeric.iloc[i, j]
                if pd.notna(val):
                    # Normalize within column range
                    col_min = df_numeric[col].min()
                    col_max = df_numeric[col].max()
                    if col_max > col_min:
                        norm_val = (val - col_min) / (col_max - col_min)
                        color = cmap(norm_val)
                    else:
                        color = 'lightgray'
                else:
                    color = 'white'
                row_colors.append(color)
            cell_colors.append(row_colors)
    else:
        # Uniform coloring
        cell_colors = [['white'] * len(properties) for _ in range(len(materials))]
    
    # Create matplotlib table
    table = ax.table(
        cellText=df.values,
        rowLabels=df.index,
        colLabels=df.columns,
        cellColours=cell_colors,
        cellLoc='center',
        loc='center',
        colWidths=[0.15] * len(properties)
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)  # Make cells taller
    
    # Bold headers
    for i in range(len(properties)):
        cell = table[(0, i)]
        cell.set_text_props(weight='bold', fontsize=11)
        cell.set_facecolor('#4CAF50')
        cell.set_text_props(color='white')
    
    # Bold row labels
    for i in range(len(materials)):
        cell = table[(i+1, -1)]
        cell.set_text_props(weight='bold', fontsize=11)
        cell.set_facecolor('#2196F3')
        cell.set_text_props(color='white')
    
    # Title
    ax.set_title('Material Property Comparison Table', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save HTML if requested
    if save_html:
        if color_scale:
            # Create styled HTML with color gradients
            styled_df = df_numeric.style.background_gradient(cmap='RdYlGn', axis=0)
            styled_df = styled_df.format(precision=2, na_rep='N/A')
            html = styled_df.to_html()
        else:
            html = df.to_html()
        
        with open(save_html, 'w') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Material Property Comparison</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; margin: 20px auto; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #ddd; }}
    </style>
</head>
<body>
    <h1 style="text-align: center;">Material Property Comparison</h1>
    {html}
</body>
</html>
""")
        logger.info(f"Saved HTML table to: {save_html}")
    
    # Save PNG if requested
    if save_png:
        plotter.save_figure(fig, save_png, dpi=300)
        logger.info(f"Saved PNG table to: {save_png}")
    
    logger.info(f"✓ Created comparison table: {len(materials)} materials × {len(properties)} properties")
    return df, fig


def plot_property_scatter(
    materials: List[str],
    property_x: str,
    property_y: str,
    data: Dict[str, Dict[str, Any]],
    units: Optional[Dict[str, str]] = None,
    figsize: Tuple[float, float] = (10, 8),
    style: str = 'publication',
    show_labels: bool = True,
    label_offset: float = 0.02,
    fit_line: bool = False,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create scatter plot showing relationship between two properties across materials.
    Each point is labeled with the material name.
    
    Args:
        materials: List of material names
        property_x: Property name for x-axis
        property_y: Property name for y-axis
        data: Nested dict {material_name: {property_name: value}}
        units: Dict mapping property names to units
        figsize: Figure size (width, height) in inches
        style: Plotting style ('publication', 'presentation', 'notebook')
        show_labels: If True, label each point with material name
        label_offset: Offset for text labels (as fraction of axis range)
        fit_line: If True, add linear regression line
        save_path: Optional path to save figure
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> fig = plot_property_scatter(
        ...     materials=['Al', 'Cu', 'Fe'],
        ...     property_x='Density',
        ...     property_y='Melting Temperature',
        ...     data=data_dict
        ... )
    """
    # Initialize plotting utilities
    plotter = PlottingUtils(style=style)
    
    # Create figure
    fig, ax = plotter.create_figure(nrows=1, ncols=1, figsize=figsize)
    
    # Extract x and y values
    x_values = []
    y_values = []
    valid_materials = []
    
    for mat in materials:
        if mat in data:
            x_val = data[mat].get(property_x)
            y_val = data[mat].get(property_y)
            
            # Handle dict format (with value, unit, ref)
            if isinstance(x_val, dict):
                x_val = x_val.get('value')
            if isinstance(y_val, dict):
                y_val = y_val.get('value')
            
            # Convert to float
            try:
                x_val = float(x_val) if x_val else None
                y_val = float(y_val) if y_val else None
            except (ValueError, TypeError):
                x_val = None
                y_val = None
            
            if x_val is not None and y_val is not None:
                x_values.append(x_val)
                y_values.append(y_val)
                valid_materials.append(mat)
    
    if not x_values or not y_values:
        logger.warning("No valid data points for scatter plot")
        return fig
    
    # Get material colors
    material_colors = []
    for mat in valid_materials:
        color = plotter.get_material_color(mat)
        if color is None:
            # Use palette color if no material-specific color
            idx = valid_materials.index(mat)
            colors = plotter.get_color_palette('materials', len(valid_materials))
            color = colors[idx]
        material_colors.append(color)
    
    # Create scatter plot
    scatter = ax.scatter(
        x_values, y_values,
        c=material_colors,
        s=150,
        alpha=0.7,
        edgecolors='black',
        linewidths=1.5,
        zorder=3
    )
    
    # Add labels to points
    if show_labels:
        x_range = max(x_values) - min(x_values)
        y_range = max(y_values) - min(y_values)
        
        for i, (x, y, mat) in enumerate(zip(x_values, y_values, valid_materials)):
            ax.annotate(
                mat,
                xy=(x, y),
                xytext=(x + label_offset * x_range, y + label_offset * y_range),
                fontsize=10,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1, color='gray'),
                zorder=4
            )
    
    # Add fit line if requested
    if fit_line and len(x_values) >= 2:
        # Linear regression
        coeffs = np.polyfit(x_values, y_values, 1)
        poly = np.poly1d(coeffs)
        
        # Generate smooth line
        x_fit = np.linspace(min(x_values), max(x_values), 100)
        y_fit = poly(x_fit)
        
        ax.plot(x_fit, y_fit, 'r--', linewidth=2, alpha=0.6, label=f'y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}', zorder=2)
        
        # Calculate R²
        y_pred = poly(x_values)
        ss_res = np.sum((np.array(y_values) - y_pred) ** 2)
        ss_tot = np.sum((np.array(y_values) - np.mean(y_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Add R² to legend
        ax.text(
            0.05, 0.95,
            f'R² = {r_squared:.3f}',
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
    
    # Configure axes
    x_unit = units.get(property_x, '') if units else ''
    y_unit = units.get(property_y, '') if units else ''
    
    x_label = f"{property_x} ({x_unit})" if x_unit else property_x
    y_label = f"{property_y} ({y_unit})" if y_unit else property_y
    
    plotter.configure_axes(
        ax,
        xlabel=x_label,
        ylabel=y_label,
        title=f'{property_y} vs {property_x}',
        grid=True
    )
    
    # Add legend if fit line shown
    if fit_line:
        plotter.add_legend(ax, loc='lower right')
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plotter.save_figure(fig, save_path)
        logger.info(f"Saved scatter plot to: {save_path}")
    
    logger.info(f"✓ Created scatter plot: {property_x} vs {property_y} for {len(valid_materials)} materials")
    return fig


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def demo_property_comparison_plots():
    """
    Demonstration of property comparison plotting functions.
    Creates sample plots using synthetic data.
    """
    print("\n" + "="*70)
    print("PROPERTY COMPARISON PLOTS - DEMONSTRATION")
    print("="*70 + "\n")
    
    # Sample data
    materials = ['Aluminum', 'Copper', 'Steel', 'Titanium', 'Nickel']
    
    # Sample property data
    data = {
        'Aluminum': {
            'Density': 2700,
            'Melting Temperature': 933,
            'Thermal Conductivity': 237,
            'Young\'s Modulus': 70
        },
        'Copper': {
            'Density': 8960,
            'Melting Temperature': 1358,
            'Thermal Conductivity': 401,
            'Young\'s Modulus': 130
        },
        'Steel': {
            'Density': 7850,
            'Melting Temperature': 1811,
            'Thermal Conductivity': 50,
            'Young\'s Modulus': 200
        },
        'Titanium': {
            'Density': 4540,
            'Melting Temperature': 1941,
            'Thermal Conductivity': 22,
            'Young\'s Modulus': 116
        },
        'Nickel': {
            'Density': 8908,
            'Melting Temperature': 1728,
            'Thermal Conductivity': 91,
            'Young\'s Modulus': 200
        }
    }
    
    units = {
        'Density': 'kg/m³',
        'Melting Temperature': 'K',
        'Thermal Conductivity': 'W/(m·K)',
        'Young\'s Modulus': 'GPa'
    }
    
    # Test 1: Bar chart
    print("Test 1: Creating grouped bar chart...")
    properties_bar = ['Density', 'Melting Temperature']
    fig1 = plot_property_comparison_bar(
        materials=materials,
        properties=properties_bar,
        data=data,
        units=units,
        save_path='demo_property_bar.png'
    )
    print("✓ Bar chart created\n")
    plt.close(fig1)
    
    # Test 2: Comparison table
    print("Test 2: Creating comparison table...")
    properties_table = ['Density', 'Melting Temperature', 'Thermal Conductivity', 'Young\'s Modulus']
    df, fig2 = plot_property_comparison_table(
        materials=materials,
        properties=properties_table,
        data=data,
        units=units,
        color_scale=True,
        save_html='demo_property_table.html',
        save_png='demo_property_table.png'
    )
    print(f"✓ Table created with shape {df.shape}")
    print("\nDataFrame preview:")
    print(df)
    print()
    plt.close(fig2)
    
    # Test 3: Scatter plot
    print("Test 3: Creating scatter plot...")
    fig3 = plot_property_scatter(
        materials=materials,
        property_x='Density',
        property_y='Melting Temperature',
        data=data,
        units=units,
        show_labels=True,
        fit_line=True,
        save_path='demo_property_scatter.png'
    )
    print("✓ Scatter plot created\n")
    plt.close(fig3)
    
    print("="*70)
    print("✓✓✓ ALL DEMONSTRATIONS COMPLETED ✓✓✓")
    print("="*70)
    print("\nGenerated files:")
    print("  • demo_property_bar.png")
    print("  • demo_property_table.html")
    print("  • demo_property_table.png")
    print("  • demo_property_scatter.png")
    print()


if __name__ == "__main__":
    # Run demonstration
    demo_property_comparison_plots()
