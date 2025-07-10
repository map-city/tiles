import argparse
import json
import os
from typing import List

import requests


class Layer:
    def __init__(self, id, name, sort_by=("position", False), zoom="all", format="geojson"):
        self.id = id
        self.name = name
        self.sort_key, self.sort_reverse = sort_by
        self.zoom = zoom
        self.format = format


def resource_url(layer: Layer) -> str:
    metadata_url = f"https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id={layer.id}"
    response = requests.get(metadata_url).json()
    resources = [
        resource
        for resource in response["result"]["resources"]
        if resource["format"].lower() == layer.format and resource["url_type"] == "upload"
    ]
    if not resources:
        return None
    resources.sort(key=lambda res: res[layer.sort_key], reverse=layer.sort_reverse)
    return resources[0]["url"]


def get_args():
    parser = argparse.ArgumentParser(description="Download GeoJSON layers from Open Data Toronto.")
    parser.add_argument(
        "--folder", 
        type=str, 
        required=True, 
        help="Download folder."
    )
    parser.add_argument(
        "--layers",
        type=str,
        required=True,
        help="Path to JSON file containing data sources.",
    )
    parser.add_argument(
        "--env",
        type=str,
        required=True,
        help="Path to shell-compatible file containing downloaded filenames.",
    )
    return parser.parse_args()


def load_layers(file_path: str) -> List[Layer]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return [Layer(**item) for item in data]


def main():
    args = get_args()
    data_folder = args.folder
    layers = load_layers(args.layers)
    downloaded_layers_file = args.env
    low_zoom_layers = []
    high_zoom_layers = []

    os.makedirs(data_folder, exist_ok=True)

    for layer in layers:
        url = resource_url(layer)

        if not url:
            raise ValueError(f"Unable to find resource url for layer {layer.id}")

        response = requests.get(url)
        response.raise_for_status()

        filename = f"{data_folder}/{layer.name}.{layer.format}"
        with open(filename, mode="wb") as data_file:
            data_file.write(response.content)
            print(f"Downloaded: {filename}")
        
        if layer.zoom == "low":
            low_zoom_layers.append(filename)
        elif layer.zoom == "high":
            high_zoom_layers.append(filename)
        else: # layer.zoom == "all"
            low_zoom_layers.append(filename)
            high_zoom_layers.append(filename)
    
    with open(downloaded_layers_file, "w") as env_file:
        env_file.write(
            f"LOW_ZOOM_LAYERS='{' '.join(low_zoom_layers)}'\n"
            f"HIGH_ZOOM_LAYERS='{' '.join(high_zoom_layers)}'\n"
        )



if __name__ == "__main__":
    main()
