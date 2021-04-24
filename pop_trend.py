from flask import Flask, render_template
#from graphs import js, div, cdn_js, cdn_css
import json
#import bokeh
#import bokeh.models as bkm
import geopandas as gpd
import pandas as pd
#from bokeh.io import curdoc
#from bokeh.layouts import column
from bokeh.layouts import gridplot
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Text, Span, Range1d, LinearAxis
import bokeh.models as bkm
#from bokeh.models.widgets import Select
from bokeh.palettes import brewer
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, LabelSet, Line, FactorRange, Ray
from bokeh.models.formatters import NumeralTickFormatter
import pandas as pd



df_population_early = pd.read_csv("Bevolking__huishoudens_en_bevolkingsontwikkeling__vanaf_1899_01022021_150304.csv", header = [3], skipfooter = 1, engine = "python")
df_population_early.set_index("Onderwerp",inplace=True)
df_population_early2 = df_population_early.T
df_population_early2.drop(index = ["Unnamed: 1", "1899"], axis = 0, inplace = True)
df_population_early2.reset_index(level=0, inplace=True)
df_pop_trend = df_population_early2.filter(["index", "Bevolking op 1 januari|Naar geslacht|Mannen en vrouwen"])
df_pop_trend.columns = ["Jaren", "Bevolking aan het eind van de periode"]
df_pop_trend["Jaren"] = df_pop_trend["Jaren"].apply(lambda x: int(x)-1)
df_pop_trend["Jaren_int"] = df_pop_trend["Jaren"]
df_pop_trend["Jaren"] = pd.to_datetime(df_pop_trend['Jaren'], format='%Y')
#df_pop_trend["Jaren"] = pd.to_datetime(df_pop_trend['Jaren'], format='%Y')- pd.tseries.offsets.MonthEnd()
df_pop_trend["Bevolking aan het eind van de periode"].astype("int")
df_pop_trend["x_c"] = ""
df_pop_trend['x_c'].iloc[-1] = df_pop_trend["Jaren"].iloc[-1]
df_pop_trend['x_c'].iloc[:-1] = -10
df_pop_trend["y_c"] = ""
df_pop_trend["y_c"].iloc[-1] = df_pop_trend["Bevolking aan het eind van de periode"].iloc[-1]
df_pop_trend["y_c"].iloc[:-1] = -5000


# Create a line graph

l = figure(x_axis_type="datetime", plot_width=400, plot_height=400, toolbar_location = None)
line_source2 = ColumnDataSource(data = dict(x=list(df_pop_trend["Jaren"]),
                                            y=list(df_pop_trend["Bevolking aan het eind van de periode"]),
                                            q=list(df_pop_trend["Jaren_int"]),
                                            x_c = list(df_pop_trend["x_c"]),
                                            y_c = list(df_pop_trend["y_c"])))

l.line(x = 'x', y = 'y', line_width=3, source = line_source2, line_color = "slategray")

l.circle(x = 'x_c', y = "y_c", color = "slategray", size = 12, source = line_source2)

hover_pop = bkm.HoverTool(tooltips = [("Year", "@q"), ("Population, thousands", "@y")])
l.add_tools(hover_pop)

l.y_range.start = 0
l.x_range.start = df_pop_trend["Jaren"].min()
l.y_range.end = 20000

l.yaxis.axis_line_color = 'slategray'
l.xaxis.axis_line_color = 'slategray'
l.xaxis.major_tick_line_color = "slategray"
l.xaxis.minor_tick_line_color = "slategray"
l.yaxis.major_tick_line_color = "slategray"
l.yaxis.minor_tick_line_color = "slategray"
l.xaxis.major_label_text_color = "slategray"
l.yaxis.major_label_text_color = "slategray"

l.grid.grid_line_color = None
l.outline_line_color = None

js3,div3 = components(l)