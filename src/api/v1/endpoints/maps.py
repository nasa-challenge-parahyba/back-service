from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv
import folium
import folium.plugins
from folium import Map, TileLayer
from fastapi.responses import HTMLResponse

load_dotenv()
router = APIRouter()

STAC_API_URL = os.getenv("STAC_API_URL")

def get_item_count(collection_id):
    count = 0
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"

    while True:
        response = requests.get(items_url)

        if not response.ok:
            print("error getting items")
            exit()

        stac = response.json()
        count += int(stac["context"].get("returned", 0))
        next = [link for link in stac["links"] if link["rel"] == "next"]

        if not next:
            break
        items_url = next[0]["href"]

    return count


@router.get('/co2-concentrations', response_class=HTMLResponse)
async def get_map_co2_concentrations(): 
    raster_api_url = os.getenv("RASTER_API_URL")
    collection_id = os.getenv("COLLECTION_CO2_CONCENTRATIONS")
    
    # Check total number of items available
    number_of_items = get_item_count(collection_id)
    items = requests.get(f"{STAC_API_URL}/collections/{collection_id}/items?limit={number_of_items}").json()["features"]
    
    # To access the year value from each item more easily, this will let us query more explicitly by year and month (e.g., 2020-02)
    items = {item["properties"]["datetime"]: item for item in items} 
    asset_name = "xco2" #fossil fuel
    
    # Fetching the min and max values for a specific item
    rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}
    
    color_map = "magma"
    oco2 = requests.get(
        f"{raster_api_url}/collections/{items[list(items.keys())[0]]['collection']}/items/{items[list(items.keys())[0]]['id']}/tilejson.json?"
        f"&assets={asset_name}"
        f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
        f"&rescale={rescale_values['min']},{rescale_values['max']}", 
).json()

    # Create the map with a single layer
    map_co2 = Map(location=(34, -118), zoom_start=12)

    map_layer = TileLayer(
        tiles=oco2["tiles"][0],
        attr="GHG",
        opacity=0.5,
    )
    map_layer.add_to(map_co2)

    # Return the map as HTML
    return map_co2._repr_html_()



def get_item_count_ff(collection_id):

    count = 0

    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"

    while True:

        response = requests.get(items_url)

        if not response.ok:
            print("error getting items")
            exit()

        stac = response.json()

        count += int(stac["context"].get("returned", 0))

        next = [link for link in stac["links"] if link["rel"] == "next"]

        if not next:
            break
        
        items_url = next[0]["href"]

    return count    


@router.get('/fossil_fuel_concentrations', response_class=HTMLResponse)
async def get_map_ff_concentrations():
    raster_api_url = os.getenv("RASTER_API_URL")
    collection_id = os.getenv("COLLECTION_FOSSIL_FUEL")
    number_of_items = get_item_count_ff(collection_id)

    items = requests.get(f"{STAC_API_URL}/collections/{collection_id}/items?limit={number_of_items}").json()["features"]

    items = {item["properties"]["start_datetime"]: item for item in items} 

    # Next, we need to specify the asset name for this collection
    # The asset name is referring to the raster band containing the pixel values for the parameter of interest
    # For the case of the OCO-2 MIP Top-Down CO₂ Budgets collection, the parameter of interest is “ff”
    asset_name = "ff" #fossil fuel

    # Fetching the min and max values for a specific item
    rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}

    # Hardcoding the min and max values to match the scale in the GHG Center dashboard
    rescale_values = {"max": 450, "min": 0}


    color_map = "purd"


    # 2020
    co2_flux_1 = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{raster_api_url}/collections/{items[list(items.keys())[0]]['collection']}/items/{items[list(items.keys())[0]]['id']}/tilejson.json?"
    f"&assets={asset_name}"
    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    # Pass the minimum and maximum values for rescaling
    f"&rescale={rescale_values['min']},{rescale_values['max']}", ).json()

    map_ = Map(location=(34, -118), zoom_start=12)

    # Define the first map layer (2020)
    map_ff_2020 = TileLayer(
        tiles=co2_flux_1["tiles"][0], # Path to retrieve the tile
        attr="GHG", # Set the attribution
        opacity=0.5, # Adjust the transparency of the layer
    )

    # Add the first layer to the Dual Map
    map_ff_2020.add_to(map_)

    # Visualize the Dual Map
    return map_._repr_html_()
