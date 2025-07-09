import requests


class Layer:
    def __init__(self, id, name, source, format="geojson"):
        self.id = id
        self.name = name
        self.source = source
        self.format = format


def resource_url(data_id, format="geojson"):
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


def main():
    DATA_FOLDER = "data"
    LAYERS = [
        Layer(id="toronto-centreline-tcl", name="roads", source="Open Data TO"),
        Layer(id="property-boundaries", name="property-boundaries", source="Open Data TO"),
    ]

    for layer in LAYERS:
        url = resource_url(layer.id, layer.format)
        filename = f"{DATA_FOLDER}/{layer.name}.{layer.format}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, mode="wb") as data_file:
                data_file.write(response.content)
                print(filename)


if __name__ == "__main__":
    main()
