import json
import os
from dataclasses import asdict


def save_data_to_json(list_data: list, json_path: str) -> None:

    data = [asdict(data_obj) for data_obj in list_data]

    with open(os.path.join("data", json_path), "w") as json_file:
        json.dump(data, json_file, indent=2)
