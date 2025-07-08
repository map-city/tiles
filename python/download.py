import requests


class Layer:
    def __init__(self, id, name, format="geojson"):
        self.id = id
        self.name = name
        self.format = format


def resource_url(
    data_id,
    format="geojson",
    api_url="https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show",
):
    response = requests.get(api_url, params={"id": data_id}).json()
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
        Layer(id="toronto-centreline-tcl", name="roads"),
        Layer(id="property-boundaries", name="property-boundaries"),
    ]

    for layer in LAYERS:
        url = resource_url(data_id=layer.id, format=layer.format)
        filename = f"{DATA_FOLDER}/{layer.name}.{layer.format}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, mode="wb") as data_file:
                data_file.write(response.content)
                print(filename)


if __name__ == "__main__":
    main()
