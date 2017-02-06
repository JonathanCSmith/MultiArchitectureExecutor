import csv
import json


def load_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def load_csv(file_path, delimiter=",", header_lines=0):
    out = []
    with open(file_path, "r") as source:
        counter = 0
        for line in source:
            if counter < header_lines:
                counter += 1
                continue

            fields = line.split(delimiter)
            if not type(fields) is list or len(fields) == 0:
                continue

            out.append(fields)

    return out


def save_json(file_path, json_data):
    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file)


def save_csv(file_path, sheet):
    with open(file_path, "w") as target:
        writer = csv.writer(target, delimiter="\t")
        for line in sheet:
            writer.writerow(line)
