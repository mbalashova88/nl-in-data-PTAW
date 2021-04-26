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

df_province_shortage = pd.read_csv("/home/datanl/nl-in-data-PTAW/province_shortage_house.csv")
map_province = gpd.read_file("/home/datanl/nl-in-data-PTAW/geoserver-GetFeature_province2.application")

shortage_province_map = map_province.merge(df_province_shortage, on = "statcode")
shortage_province_map.sort_values(by = "Woningtekort_2020_%", ascending  = True, inplace = True)

# create a new plot and add a renderer
df_json = json.loads(shortage_province_map.to_json())
json_data = json.dumps(df_json)
geosource = GeoJSONDataSource(geojson = json_data)

# Set the color palette
palette = brewer['Blues'][6]
palette = palette[::-1]

# Create a color bar
color_mapper = LinearColorMapper(palette = palette, low = 0,
                                 high = 0.06)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=5,width = 250, height = 7,
border_line_color="white", bar_line_color = "grey", location = "bottom_center", orientation ='horizontal',
major_tick_line_color = "white", major_tick_in = 0, margin = 0, padding = 0)

first = figure(plot_height = 350, plot_width = 300, toolbar_location = None)
first.title.vertical_align = "top"
dot_hover = bkm.HoverTool(tooltips=[("Region","@Provincie")])
first.add_tools(dot_hover)
first.patches('xs','ys', source = geosource,fill_color = {'field':'Woningtekort_2020_%', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1, hover_line_color = "#ff8157", hover_line_width = 3)

# Remove gird lines
first.xgrid.grid_line_color = None
first.ygrid.grid_line_color = None

# Remove axis
first.axis.visible = False

# Remove figure outline
first.outline_line_color = "white"
first.y_range.range_padding = 0.05
first.add_layout(color_bar, 'below')


# create another new plot, add a renderer that uses the view of the data source
shortage_bar = figure(y_range = shortage_province_map["Provincie"].head(12), plot_width=300, plot_height=350, title=None, toolbar_location = None, tools = "")
shortage_bar.hbar(y = 'Provincie', height = 0.6, right = 'Woningtekort_2020_%', fill_color = "slategray", line_color = "slategray", hover_color="#ff8157", source = geosource)


# Adding labels to bars
label_source = ColumnDataSource(dict(x=shortage_province_map["Woningtekort_2020_%"].head(12), y=shortage_province_map["Provincie"].head(12), text = [f'{round(i*100,1)}%' for i in shortage_province_map["Woningtekort_2020_%"].head(12)]))
grey_text = Text(x='x', y='y', text='text', text_color="slategrey", text_font_size = '8pt', x_offset = -25, y_offset = 6, text_font_style = "bold")

color_bar.formatter = NumeralTickFormatter(format='0%')


shortage_bar.add_glyph(label_source, grey_text)


# Creating Hover Tool
bar_hover = bkm.HoverTool(tooltips= None)
shortage_bar.add_tools(bar_hover)

# Add vertical line with NL avg.
nl = df_province_shortage["Woningtekort_2020_%"].iloc[12]
vline = Span(location=nl, dimension='height', line_color='black', line_width=1.5, line_dash = "dotted")
shortage_bar.renderers.extend([vline])

# Add label to the vertical line

source = ColumnDataSource(dict(x=[0.045], y=[4], text = [f'NL {round(nl*100,1)}%']))
glyph = Text(x='x', y='y', text='text', text_color="slategray", text_font_size = '10pt')
shortage_bar.add_glyph(source, glyph)



# Editing visual attributes
shortage_bar.grid.visible = False
shortage_bar.xaxis.bounds = (0, 6)
shortage_bar.yaxis.axis_line_color = 'white'
shortage_bar.xaxis.axis_line_color = 'white'
shortage_bar.yaxis.major_tick_line_color = None
shortage_bar.xaxis.major_tick_line_color = "slategray"
shortage_bar.xaxis.minor_tick_line_color = "slategray"
#shortage_bar.yaxis.major_label_standoff = 15

shortage_bar.yaxis.major_label_text_font_size = '8pt'
shortage_bar.xaxis.major_label_text_font_size = '8pt'

shortage_bar.xaxis[0].formatter = NumeralTickFormatter(format="0%")

shortage_bar.min_border_right = 10
shortage_bar.outline_line_color = "white"

shortage_bar.x_range.start = 0
shortage_bar.x_range.end = 0.06
shortage_bar.y_range.range_padding = 0.03



title = Div(text="<b>Houses shortage per province</b>", style={'font-size': '100%', 'color': 'Black'})



p = gridplot([[first, shortage_bar]], toolbar_location = None)
#show(column(title,p))

js5,div5 = components(p)