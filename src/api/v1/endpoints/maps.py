from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv
from folium import Map, TileLayer
from fastapi.responses import HTMLResponse
from src.utils.get_item_count import get_item_count

load_dotenv()
router = APIRouter()

STAC_API_URL = os.getenv("STAC_API_URL")
RASTER_API_URL = os.getenv("RASTER_API_URL")


@router.get('/co2-concentrations', response_class=HTMLResponse)
async def get_map_co2_concentrations(): 
    collection_id = os.getenv("COLLECTION_CO2_CONCENTRATIONS")
    
    number_of_items = get_item_count(collection_id)
    items = requests.get(f"{STAC_API_URL}/collections/{collection_id}/items?limit={number_of_items}").json()["features"]
    
    items = {item["properties"]["datetime"]: item for item in items} 
    asset_name = "xco2"
    
    rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}
    
    color_map = "magma"
    oco2 = requests.get(
        f"{RASTER_API_URL}/collections/{items[list(items.keys())[0]]['collection']}/items/{items[list(items.keys())[0]]['id']}/tilejson.json?"
        f"&assets={asset_name}"
        f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
        f"&rescale={rescale_values['min']},{rescale_values['max']}", 
    ).json()

    map_co2 = Map(location=(34, -118), zoom_start=2, control_scale=True, width="70vw", height="70vh")

    map_layer = TileLayer(
        tiles=oco2["tiles"][0],
        attr="GHG",
        opacity=0.5,
    )
    map_layer.add_to(map_co2)

    return map_co2._repr_html_()

@router.get('/fossil-fuel-emissions', response_class=HTMLResponse)
async def get_map_fossil_fuel_emissions():
    collection_name = os.getenv("COLLECTION_FOSSIL_FUEL_EMISSION")
    
    number_of_items = get_item_count(collection_name)

    items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]
    
    items = {item["properties"]["start_datetime"][:7]: item for item in items} 
    
    asset_name = "co2-emissions"
    
    rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}

    color_map = "rainbow" 

    january_2020_tile = requests.get(

        f"{RASTER_API_URL}/collections/{items['2020-01']['collection']}/items/{items['2020-01']['id']}/tilejson.json?"

        f"&assets={asset_name}"

        f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

        f"&rescale={rescale_values['min']},{rescale_values['max']}", ).json()
    
    map = Map(location=(54, -118), zoom_start=2, control_scale=True, width="70vw", height="70vh")

    map_layer_2020 = TileLayer(
        tiles=january_2020_tile["tiles"][0],
        attr="GHG",
        opacity=0.8,
    )

    map_layer_2020.add_to(map)

    return map._repr_html_()

@router.get('/methane-emissions/{type_methane_emission}', response_class=HTMLResponse)
async def get_map_methane_emissions(type_methane_emission: str):
    collection_name = os.getenv("COLLECTION_METHANE_EMISSION")
    
    number_of_items = get_item_count(collection_name)

    items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]

    items = {item["properties"]["start_datetime"][:10]: item for item in items} 

    asset_name = ""
    
    if (type_methane_emission == 'fossil'):
        asset_name = 'fossil'
    elif (type_methane_emission == 'microbial'):
        asset_name='microbial'
    elif (type_methane_emission == 'pyrogenic'):
        asset_name='pyrogenic'
        
    rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}
    
    color_map = "rainbow"

    ch4_flux = requests.get(
        f"{RASTER_API_URL}/collections/{items['2016-12-01']['collection']}/items/{items['2016-12-01']['id']}/tilejson.json?"
        f"&assets={asset_name}"
        f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
        f"&rescale={rescale_values['min']},{rescale_values['max']}").json()
    
    map = Map(location=(34, -118), zoom_start=2, control_scale=True, width="70vw", height="70vh")

    map_layer_2016 = TileLayer(
        tiles=ch4_flux["tiles"][0],
        attr="GHG", 
        opacity=0.8, 
    )

    map_layer_2016.add_to(map)

    return map._repr_html_()
