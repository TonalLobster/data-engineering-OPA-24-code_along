import requests
import json
import dlt
from pathlib import Path
import os


def _get_ads(url_for_search, params):
    headers = {"accept": "application/json"}
    response = requests.get(url_for_search, headers=headers, params=params)
    response.raise_for_status()  # check for http errors
    return json.loads(response.content.decode("utf8"))


@dlt.resource(write_disposition="replace")
def jobsearch_resource(params):
    url = "https://jobsearch.api.jobtechdev.se"
    url_for_search = f"{url}/search"

    limit = params.get("limit", 100)
    offset = 0

    while True:
        page_params = dict(params, offset=offset)
        data = _get_ads(url_for_search, page_params)

        hits = data.get("hits", [])

        if not hits:
            break
        for ads in hits:
            yield ads
        if len(hits) < limit or offset > 1900:
            break

        offset += limit


def run_pipeline(query, table_name, occupation_fields):
    pipeline = dlt.pipeline(
        pipeline_name="jobads_project",
        destination=dlt.destinations.duckdb("ads_data_warehouse.duckdb"),
        dataset_name="staging",
    )

    for occupation_field in occupation_fields:
        params = {"q": query, "limit": 100, "occupation-field": occupation_field}
        load_info = pipeline.run(
            jobsearch_resource(params=params), table_name=table_name
        )

        print(f"{occupation_field = }")
        print(load_info)


def example_search_return_number_of_hits(query):
    # limit: 0 means no ads, just a value of how many ads were found.
    search_params = {"q": query, "limit": 0}
    json_response = _get_ads(search_params)
    number_of_hits = json_response["total"]["value"]
    print(f"\nNumber of hits = {number_of_hits}")


def example_search_loop_through_hits(query):
    # limit = 100 is the max number of hits that can be returned.
    # If there are more (which you find with ['total']['value'] in the json response)
    # you have to use offset and multiple requests to get all ads.
    search_params = {"q": query, "limit": 100}
    json_response = _get_ads(search_params)
    hits = json_response["hits"]
    for hit in hits:
        print(f"{hit['headline']}, {hit['employer']['name']}")


if __name__ == "__main__":
    working_directory = Path(__file__).parent
    
    os.chdir(working_directory)

    query = ""
    table_name = "job_ads"


    # Teknisk inriktning, "Hälsa sjukvård", "Pedagogik"
    occupation_fields = ("6Hq3_tKo_V57", "NYW6_mP6_vwf", "MVqp_eS8_kDZ")

    run_pipeline(query, table_name, occupation_fields)