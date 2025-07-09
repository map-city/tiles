import argparse
import json
import os

import requests


class Layer:
    def __init__(self, id, name, format="geojson"):
        self.id = id
        self.name = name
        self.format = format


def resource_url(data_id, format):
    metadata_url = f"https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id={data_id}"
    response = requests.get(metadata_url).json()
    resources = [
        resource
        for resource in response["result"]["resources"]
        if resource["format"].lower() == format and resource["url_type"] == "upload"
    ]
    if not resources:
        return None
    resources.sort(key=lambda res: res["last_modified"], reverse=True)
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
    return parser.parse_args()


def load_layers(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    layers = []
    for item in data:
        try:
            layers.append(Layer(**item))
        except TypeError as e:
            print(f"Error loading layer entry {item}: {e}")
    return layers


def main():
    args = get_args()
    data_folder = args.folder
    layers = load_layers(args.layers)

    os.makedirs(data_folder, exist_ok=True)

    for layer in layers:
        url = resource_url(layer.id, layer.format)

        if not url:
            print(f"Unable to find resource url for layer {layer.id}")
            continue

        filename = f"{data_folder}/{layer.name}.{layer.format}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, mode="wb") as data_file:
                data_file.write(response.content)
                print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download {layer.id}, HTTP {response.status_code}")


if __name__ == "__main__":
    main()
