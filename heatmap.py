# Creating a heatmap in matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG
from pylab import *
import io
from flask import Response




def heatmap_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")

def create_figure():
    df_age_map = pd.read_csv("Age_data_1950-2020.csv", header=[5], engine='python')
    df_age_map.index = df_age_map["Age_group"].str.replace(",%", "")
    df_age_map.set_index("Age_group", inplace=True)
    df_age_map = pd.concat([df_age_map[col].str.rstrip("%").astype("int") / 100 for col in df_age_map], axis=1)
    df_age_map = df_age_map[df_age_map.columns[::5]]

    fig, ax = plt.subplots(figsize = (5.5,4.5))
    bounds = np.array([0.00,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10,0.11,0.12])

    new_RdYlBu = cm.get_cmap('RdYlBu_r', 13)
    c = pcolor(df_age_map, cmap = new_RdYlBu, edgecolors = "slategray", linewidth = 0.1)
    # Show all ticks
    ax.set_xticks(np.arange(len(df_age_map.columns)))
    ax.set_yticks(np.arange(len(df_age_map.index)))

    # Label the ticks
    ax.set_xticklabels(df_age_map.columns)
    ax.set_yticklabels(df_age_map.index)

    #Rotate the tick labels

    plt.setp(ax.get_xticklabels(), rotation = 0, ha = "center")
    start, end = ax.get_xlim()
    starty, endy = ax.get_ylim()
    ax.xaxis.set_ticks(np.arange(start, end, 2), minor = False)
    ax.yaxis.set_ticks(np.arange(starty, endy, 2), minor = True)

    plt.setp(ax.spines.values(), color="slategray")

    # Remove ticks from y-axis
    ax.tick_params(axis = "x", length = 0, labelsize = 7, labelcolor = 'slategray')
    ax.tick_params(axis = "y", length = 0, labelsize = 7, labelcolor = 'slategray')
    plt.setp(ax.get_xticklabels(), rotation = 0, ha = "left")
    plt.setp(ax.get_yticklabels(), rotation = 0, va = "bottom")

    ax.text(1, 1, 'Baby boom', fontsize = 10, color =  '#262626')
    ax.text(11.5, 9, 'Ageing\npopulation', fontsize = 10, color =  '#262626')
    ax.text(11.1, 0.5, 'Relatively\nless children', fontsize = 10, color =  '#262626')
    # ax.annotate('annotate', xy=(12, 10), xytext=(3, 4),
    #             arrowprops=dict(facecolor='black', shrink=10))

    plt.arrow(4, 2, 6.5,6.5, width=0.05, head_width = 0.3, head_length = 0.6, color = '#262626', alpha = 0.7, overhang = 0.4)


    cb = fig.colorbar(c, ax=ax, boundaries = bounds, drawedges = True, orientation = "vertical", pad = 0.05)

    cb.outline.set_edgecolor('slategray')
    cb.outline.set_linewidth(0.5)
    cb.ax.tick_params(size=0, labelcolor = 'slategray', labelsize = 7)

    cb.ax.set_yticklabels(["{:.0%}".format(i) for i in cb.get_ticks()])
    cb.ax.set_yticklabels(cb.ax.get_yticklabels(), va = "center")
    return fig
