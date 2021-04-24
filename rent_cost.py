import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Text, Span, Range1d, LinearAxis, FixedTicker, NumeralTickFormatter, Div, SingleIntervalTicker
import bokeh.models as bkm
from bokeh.palettes import brewer
import json
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.embed import components



map_corop = gpd.read_file("geoserver-GetFeature.application")

df_rent_cost = pd.read_csv("Woonlasten_huur.csv", header = [4], engine = "python")
df_rent_cost_map = map_corop.merge(df_rent_cost, on = "statcode")
df_rent_cost_map.sort_values(by = "Totaal woonlasten Huurder 2018 EUR", ascending = True, inplace = True)




# create a new plot and add a renderer

df_json = json.loads(df_rent_cost_map.to_json())
json_data = json.dumps(df_json)
geosource = GeoJSONDataSource(geojson = json_data)

# Set the color palette
palette = brewer['Reds'][4]
palette = palette[::-1]

# Create a color bar
color_mapper = LinearColorMapper(palette = palette, low = 550,
                                 high = 750)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=5,width = 450, height = 10,
border_line_color="white", bar_line_color = "grey", location = "bottom_center", orientation ='horizontal',
major_tick_line_color = "white", major_tick_in = 0, margin = 0, padding = 0,
major_label_overrides = {550: '€550', 600: '€600', 650: '€650', 700: '€700', 750: '€750'})

left = figure(plot_height = 650, plot_width = 500, toolbar_location = None)
left.title.vertical_align = "top"
dot_hover = bkm.HoverTool(tooltips=[("Region","@statnaam")])
left.add_tools(dot_hover)
left.patches('xs','ys', source = geosource,fill_color = {'field':'Totaal woonlasten Huurder 2018 EUR', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1, hover_line_color = "#ff8157", hover_line_width = 3)

# Remove gird lines
left.xgrid.grid_line_color = None
left.ygrid.grid_line_color = None

# Remove axis
left.axis.visible = False

# Remove figure outline
left.outline_line_color = "white"
left.y_range.range_padding = 0.05
left.add_layout(color_bar, 'below')


# create another new plot, add a renderer that uses the view of the data source
right = figure(y_range = df_rent_cost_map["statnaam"].head(40), plot_width=500, plot_height=650, title=None, toolbar_location = None, tools = "", x_axis_location = "above")
right.hbar(y = 'statnaam', height = 0.7, right = 'Totaal woonlasten Huurder 2018 EUR', fill_color = "slategray", line_color = "slategray", hover_color="#ff8157", source = geosource)


# Adding labels to bars
label_source = ColumnDataSource(dict(x=df_rent_cost_map["Totaal woonlasten Huurder 2018 EUR"].head(40), y=df_rent_cost_map["statnaam"].head(40), text = [f'€{round(i)}' for i in df_rent_cost_map["Totaal woonlasten Huurder 2018 EUR"].head(40)]))
grey_text = Text(x='x', y='y', text='text', text_color="slategrey", text_font_size = '8pt', x_offset = -25, y_offset = 6, text_font_style = "bold")


right.add_glyph(label_source, grey_text)


# Creating Hover Tool
bar_hover = bkm.HoverTool(tooltips= None)
right.add_tools(bar_hover)

# # Add vertical line with NL avg.
nl = df_rent_cost["Totaal woonlasten Huurder 2018 EUR"].iloc[40]
vline = Span(location=nl, dimension='height', line_color='black', line_width=1.5, line_dash = "dotted")
right.renderers.extend([vline])

# Add label to the vertical line
source = ColumnDataSource(dict(x=[705], y=[15], text = [f'Total NL\n€{round(nl)}']))
glyph = Text(x='x', y='y', text='text', text_color="slategray", text_font_size = '9.5pt')
right.add_glyph(source, glyph)

# Add a second x-axis
right.extra_x_ranges["x"] = Range1d(0, 850)
right.add_layout(LinearAxis(x_range_name="x"), "below")

# Editing visual attributes
right.grid.visible = False
#right.xaxis.bounds = (0, 520)
right.yaxis.axis_line_color = 'white'
right.xaxis.axis_line_color = 'white'
right.yaxis.major_tick_line_color = None
right.xaxis.major_tick_line_color = "slategray"
right.xaxis.minor_tick_line_color = "slategray"
#right.yaxis.major_label_standoff = 15

right.yaxis.major_label_text_font_size = '8pt'
right.xaxis.major_label_text_font_size = '8pt'
right.xaxis.major_label_overrides = {0: '€0', 100: '€100', 200: '€200', 300: '€300', 400: '€400', 500: '€500', 600: '€600' , 700: '€700', 800: '€800'}
right.xaxis.major_label_standoff = 9

right.min_border_bottom = 80
right.min_border_right = 20
right.outline_line_color = "white"


right.y_range.range_padding = 0.03

right.xaxis.ticker = SingleIntervalTicker(interval=100)
right.x_range.start = 0
right.x_range.end = 850


p = gridplot([[left, right]], toolbar_location = None)

js6,div6 = components(p)