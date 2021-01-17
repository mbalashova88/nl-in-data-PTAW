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

#instantiate the flask app
app = Flask(__name__)


# Creating geo df
geodata_url_corop = "https://geodata.nationaalgeoregister.nl/cbsgebiedsindelingen/wfs?request=GetFeature&service=WFS&version=1.1.0&typeName=cbsgebiedsindelingen:cbs_coropgebied_2020_gegeneraliseerd&outputFormat=application%2Fjson"
map_corop = gpd.read_file(geodata_url_corop)

# Creating df for plotting
cbs_original = pd.read_excel("./data/pbk-naar-corop-gebied-1e-kwartaal-1995-tot-en-met-2e-kwartaal-2020-Maria.xlsx", sheet_name = "Tabel 1", header = [2], skipfooter = 2, skiprows = [3], engine="openpyxl")
#cbs_original = pd.read_excel("C:/Users/maria/PycharmProjects/nl-in-data-PTAW/data/pbk-naar-corop-gebied-1e-kwartaal-1995-tot-en-met-2e-kwartaal-2020-Maria.xlsx", sheet_name = "Tabel 1", header = [2], skipfooter = 2, skiprows = [3], engine="openpyxl")
cbs_original.rename(columns = {"Regiocode": "statcode"}, inplace = True)
# cbs_original.astype({'statcode': 'str'})
# cbs_original.statcode = cbs_original.statcode.str.rstrip()
cbs_original.statcode = cbs_original.statcode.apply(lambda x: x.rstrip())
cbs_original['Periode'] = pd.to_datetime(cbs_original['Periode'].str[:4] + "-Q" +cbs_original['Periode'].str[5:6]).dt.to_period('Q').dt.strftime('%Y Q%q')
#Merging with geo data
df_cbs_original = map_corop.merge(cbs_original, on = "statcode")
df_cbs_original.sort_values(by = "Gemiddelde verkoopprijs", ascending = True, inplace = True)

# App code

df_cbs_original = df_cbs_original[df_cbs_original['Periode'] == "2020 Q2"]

# create a new plot and add a renderer

df_json = json.loads(df_cbs_original.to_json())
json_data = json.dumps(df_json)
geosource = GeoJSONDataSource(geojson = json_data)

# Set the color palette
palette = brewer['Blues'][6]
palette = palette[::-1]

# Create a color bar
color_mapper = LinearColorMapper(palette = palette, low = 200,
                                 high = 500)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=5,width = 450, height = 10,
border_line_color="white", bar_line_color = "grey", location = "bottom_center", orientation ='horizontal',
major_tick_line_color = "white", major_tick_in = 0, margin = 0, padding = 0,
major_label_overrides = {200: "", 250: '< €250 K', 300: '€300 K', 350: "€350 K", 400: "€400 K", 450: "> €450 K", 500: ""})

left = figure(plot_height = 650, plot_width = 500, toolbar_location = None)
left.title.vertical_align = "top"
dot_hover = bkm.HoverTool(tooltips=[("Region","@statnaam")])
left.add_tools(dot_hover)
left.patches('xs','ys', source = geosource,fill_color = {'field':'Gemiddelde verkoopprijs', 'transform' : color_mapper},
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
right = figure(y_range = df_cbs_original["statnaam"].head(40), plot_width=500, plot_height=650, title=None, toolbar_location = None, tools = "", x_axis_location = "above")
right.hbar(y = 'statnaam', height = 0.7, right = 'Gemiddelde verkoopprijs', fill_color = "slategray", line_color = "slategray", hover_color="#ff8157", source = geosource)


# Adding labels to bars
label_source = ColumnDataSource(dict(x=df_cbs_original["Gemiddelde verkoopprijs"].head(40), y=df_cbs_original["statnaam"].head(40), text = [f'€{round(i)} K' for i in df_cbs_original["Gemiddelde verkoopprijs"].head(40)]))
grey_text = Text(x='x', y='y', text='text', text_color="slategrey", text_font_size = '8pt', x_offset = -35, y_offset = 6, text_font_style = "bold")


right.add_glyph(label_source, grey_text)


# Creating Hover Tool
bar_hover = bkm.HoverTool(tooltips= None)
right.add_tools(bar_hover)

# Add vertical line with NL avg.
avg = df_cbs_original["Gemiddelde verkoopprijs"].mean()
vline = Span(location=avg, dimension='height', line_color='black', line_width=1.5, line_dash = "dotted")
right.renderers.extend([vline])

# Add label to the vertical line
source = ColumnDataSource(dict(x=[320], y=[15], text = [f'NL Avg.\n€{round(avg)}K']))
glyph = Text(x='x', y='y', text='text', text_color="slategray", text_font_size = '10pt')
right.add_glyph(source, glyph)

# Add a second x-axis
right.extra_x_ranges["x"] = Range1d(0, 530)
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
right.xaxis.major_label_overrides = {0: '€0 K', 100: '€100 K', 200: '€200 K', 300: '€300 K', 400: '€400 K', 500: '€500 K',}
right.xaxis.major_label_standoff = 9

right.min_border_bottom = 80
right.outline_line_color = "white"

right.x_range.start = 0
right.y_range.range_padding = 0.03

p = gridplot([[left, right]], toolbar_location = None)
#show(p)

js, div = components(p)
cdn_js = CDN.js_files[0]
cdn_css = 'https://cdn.bokeh.org/bokeh/release/bokeh-2.2.3.min.css'





#create index page function
@app.route("/")
def index():
    return render_template("index.html", js = js, div = div, cdn_js = cdn_js, cdn_css = cdn_css)
    #return render_template("index.html")

#run the app
if __name__ == "__main__":
    app.run(debug=True)