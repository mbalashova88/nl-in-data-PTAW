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
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Text, Span, Range1d, LinearAxis, Label
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
import numpy as np



df_population_early = pd.read_csv("/home/datanl/nl-in-data-PTAW/Bevolking__huishoudens_en_bevolkingsontwikkeling__vanaf_1899_01022021_150304.csv", header = [3], skipfooter = 1, engine = "python")
# Format dataframe for a line graph
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
df_pop_trend["Bevolking aan het eind van de periode"] = df_pop_trend["Bevolking aan het eind van de periode"].apply(lambda x: round(int(x) * 1000, 1))
df_pop_trend["x_c"] = ""
df_pop_trend['x_c'].iloc[-1] = df_pop_trend["Jaren"].iloc[-1]
df_pop_trend['x_c'].iloc[:-1] = -10
df_pop_trend["y_c"] = ""
df_pop_trend["y_c"].iloc[-1] = df_pop_trend["Bevolking aan het eind van de periode"].iloc[-1]
df_pop_trend["y_c"].iloc[:-1] = -5000000


# Create a line graph

l = figure(x_axis_type="datetime", plot_width=450, plot_height=400, toolbar_location = None, title = "Population is growing steadily")
line_source2 = ColumnDataSource(data = dict(x=list(df_pop_trend["Jaren"]),
                                            y=list(df_pop_trend["Bevolking aan het eind van de periode"]),
                                            q=list(df_pop_trend["Jaren_int"]),
                                            x_c = list(df_pop_trend["x_c"]),
                                            y_c = list(df_pop_trend["y_c"])))
l.line(x = 'x', y = 'y', line_width=3, source = line_source2, line_color = "slategray")
l.circle(x = 'x_c', y = "y_c", color = "#ff8157", size = 12, source = line_source2)
hover_pop = bkm.HoverTool(tooltips = [("Year", "@q"), ("Population", "@y{(0.0 a)}")])
l.add_tools(hover_pop)


citation = Label(x=265, y=240, x_units='screen', y_units='screen',
                 text='17.5 m people in 2020', render_mode='css',
                 border_line_color=None,
                 background_fill_color='white', background_fill_alpha=0, text_color = "#ff8157", text_font_size = "11pt")


l.add_layout(citation)

l.y_range.start = 0
l.y_range.end = 20000000
l.x_range.start = df_pop_trend["Jaren"].min()

l.yaxis.axis_line_color = 'slategray'
l.xaxis.axis_line_color = 'slategray'
l.xaxis.major_tick_line_color = "slategray"
l.xaxis.minor_tick_line_color = "slategray"
l.yaxis.major_tick_line_color = "slategray"
l.yaxis.minor_tick_line_color = "slategray"
l.xaxis.major_label_text_color = "slategray"
l.yaxis.major_label_text_color = "slategray"
l.yaxis[0].formatter = NumeralTickFormatter(format="0 a")

l.grid.grid_line_color = None
l.outline_line_color = None
l.min_border_top = 50

arrays = [np.array(["Addition", "Addition", "Deduction", "Deduction", "Total"]),
          np.array(["Birth", "Immigration", "Deaths", "Emigration", "Net change"])]



#index = ['Births','Immigration','Deaths', 'Emigration']
data = {'amount': [170000,269000,-152000,-161000, 0]}
df = pd.DataFrame(data=data,index=arrays)
# Determine the total net value by adding the start and all additional transactions
net = df['amount'].sum()
# Create additional columns that we will use to build the waterfall
df['running_total'] = df['amount'].cumsum()
df['y_start'] = df['running_total'] - df['amount']

# Where do we want to place the label
df['label_pos'] = df['running_total']

# We need to have a net column at the end with the totals and a full bar
df_net = pd.DataFrame.from_records([(net, net, 0, net)],
                                   columns=['amount', 'running_total', 'y_start', 'label_pos'],
                                   index=["Net change"])
# df = df.append(df_net)

df.loc["Total", "Net change"] = df_net.loc["Net change"]


# We want to color the positive values gray and the negative red
df['color'] = '#6baed6'
df.loc[df.amount < 0, 'color'] = "#ff8157"
df.loc[("Total", "Net change"), "color"] = "slategray"
# The 10000 factor is used to make the text positioned correctly.
# You will need to modify if the values are significantly different
df.loc[df.amount < 0, 'label_pos'] = df.label_pos - 27000
# #df["bar_label"] = df["amount"].map('{:,.0f}'.format)
df["bar_label"] = df["amount"].apply(lambda x: str(round(x/1000)) + " K")

source = ColumnDataSource(df)
factors2 = list(df.index)

# Create the figure and assign range values that look good for the data set
w = figure(tools="", x_range=FactorRange(*factors2, group_padding = 0), y_range=(0, net+400000), plot_width=520, plot_height = 300,
           title = "Population growth of 126k in 2019 is driven by the net immigration", toolbar_location = None)
# # Add the segments
w.segment(x0='index', y0="y_start", x1="index", y1="running_total", source = source,
          color="color", line_width=55)

w.xgrid.grid_line_color = None
w.ygrid.grid_line_color = None
w.outline_line_color = None
w.xaxis.axis_line_color = 'white'
w.xaxis.major_tick_line_color = None
w.yaxis.visible = False
w.x_range.range_padding = -0.12
w.xaxis.major_label_text_color = 'grey'
w.xaxis.group_text_color = "grey"





data_ray = {'x_coord': [0.74, 1.74, 2.74, 3.74], "y_coord": df["running_total"].head(4),
            'length': [0.5, 0.5, 0.5, 0.5]}


df_ray = pd.DataFrame(data = data_ray)
source_ray = ColumnDataSource(data_ray)


glyph_ray = Ray(x="x_coord", y="y_coord", length="length", angle=0, line_color="slategray", line_width=1, line_dash = "dotted", angle_units = "deg")
w.add_glyph(source_ray, glyph_ray)


label_text = Text(x='index', y='label_pos', text='bar_label', text_color="grey", text_font_size = '8pt', x_offset = -16, y_offset = 0, text_font_style = "bold")
w.add_glyph(source, label_text)

w.min_border_left = 80
w.min_border_right = 9


p = gridplot([[l, w]], toolbar_location = None)

#js4,div4 = components(p)
js4,div4 = components(l)