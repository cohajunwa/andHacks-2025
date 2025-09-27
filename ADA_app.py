import pandas as pd
import geopandas as gpd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from shapely.geometry import Point

cvs_loc = "locations.csv"   
# Add your Mapbox token here (you can get one from https://account.mapbox.com/access-tokens/)

# Initialize the Dash app
app = Dash(__name__)

# Step 1: Function to load data (including image paths)
def csv_to_geopandas(file_path):
    df = pd.read_csv(file_path,encoding='latin1')
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("CSV must contain 'latitude' and 'longitude' columns.")
    
    gdf = gpd.GeoDataFrame(df, 
                           geometry=[Point(xy) for xy in zip(df['longitude'], df['latitude'])], 
                           crs="EPSG:4326")
    
    return gdf

# Load the data
gdf = csv_to_geopandas(cvs_loc)

# Create a Plotly map using Mapbox
def create_map(gdf):
    # Filter out rows where latitude or longitude are NaN
    gdf_filtered = gdf[gdf.geometry.notnull()]

    # Create the map using the filtered GeoDataFrame
    fig = px.scatter_mapbox(gdf_filtered,
                            lat=gdf_filtered.geometry.y,
                            lon=gdf_filtered.geometry.x,
                            hover_name="Name",  # Assuming you meant 'Name'
                            hover_data=["ADA_Violation"],  # Show ADA violation in hover
                            zoom=6,  # Adjust zoom level for Virginia
                            center={"lat": 37.4316, "lon": -78.6569},  # Center on Virginia
                            height=600)

    # Customize the appearance of the hover text using hovertemplate
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"  # Main label (e.g., 'name') in bold
            "<i>ADA_Violation:</i> %{customdata[0]}<br>"  # Italic 'ADA Violation:' and show the first custom data
            "<i>Date:</i> %{customdata[1]}<br>"         # Add Date
            "<i>Building:</i> %{customdata[2]}<br>"     # Add Building
            "<extra></extra>"  # This removes extra information (e.g., trace info)
        ),
        # Pass description, date, and building columns into customdata
        customdata=gdf_filtered[['ADA_Violation', 'Date', 'Building',"image"]]
    )

    # Update layout to use the Mapbox token and show street lines
    fig.update_layout(
        mapbox_style="streets",  # Show street lines
        mapbox_accesstoken=mapbox_token,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Remove margins for full-screen map
        mapbox_zoom=6,  # Zoom level to focus on Virginia
        mapbox_center={"lat": 37.4316, "lon": -78.6569}
    )
    
    return fig

# Step 3
app.layout = html.Div(style={'position': 'relative'}, children=[
    # Map
    dcc.Graph(id="location-map", style={'position': 'relative', 'z-index': '1'}),
    
    # Image overlay (initially hidden)
    html.Div(id="image-container", style={
        'position': 'absolute',
        'top': '20px',
        'right': '20px',
        'width': '300px',
        'height': '300px',
        'z-index': '2',
        'display': 'none',  # Initially hidden
        'background-color': 'white',
        'padding': '10px',
        'box-shadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
        'border': '1px solid #ccc'
    }, children=[
        html.Img(id='location-image', style={'max-width': '100%', 'height': 'auto'})
    ]),
    
    # Add interval component for periodic updates
    dcc.Interval(
        id='interval-component',
        interval=100000*1000,  # Update every 10 seconds
        n_intervals=0
    )
])

# Callback to update the map
@app.callback(
    Output('location-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    # Reload the CSV file each time the interval is triggered
    gdf = csv_to_geopandas(cvs_loc)
    return create_map(gdf)

# Callback to update the image and control its visibility
@app.callback(
    [Output('location-image', 'src'),
     Output('image-container', 'style')],
    [Input('location-map', 'clickData')]
)
def update_image(clickData):
    if clickData is None:
        # Hide the image if no point is clicked
        return "", {'display': 'none'}
    
    # Get the image filename from the clicked point
    clicked_point = clickData['points'][0]
    
    # 'customdata[1]' now refers to the image path we passed in customdata
    image_name = clicked_point['customdata'][3]  # Assuming 'customdata' has the image filename
    
    # Build the src path for the image (Ensure image file is available in assets/images)
    image_src = f"/assets/images/{image_name}"
    

    # Debugging: Print the image path
    print(image_src)

    # Set the style to make the image visible
    style = {
        'position': 'absolute',
        'top': '20px',
        'right': '20px',
        'width': '300px',
        'height': '400px',
        'z-index': '2',
        'display': 'block',  # Make the image visible
        'background-color': 'white',
        'padding': '10px',
        'box-shadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
        'border': '1px solid #ccc'
    }
    
    # Return the image path and the style (to show the image)
    return image_src, style

# Run the app
if __name__ == "__main__":
