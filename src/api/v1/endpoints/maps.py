from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

STAC_API_URL = os.getenv("STAC_API_URL")

async def get_item_count(collection_id):
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

@router.get('/co2-concentrations')
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
    
    return oco2
