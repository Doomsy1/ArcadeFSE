import json
import os


combined_openings = {}

# get all the json files from gm_games\jsons
json_folder = "gm_games/jsons"
json_files = os.listdir(json_folder)

count = 0
for json_file in json_files:
    count += 1
    if count > 20:
        break
    json_file_path = os.path.join(json_folder, json_file)
    with open(json_file_path, "r") as file:
        data = json.load(file)
        print(f"Processing {json_file}")
        for fen in data:
            if fen not in combined_openings:
                combined_openings[fen] = data[fen]
            else:
                for move in data[fen]:
                    if move not in combined_openings[fen]:
                        combined_openings[fen][move] = data[fen][move]
                    else:
                        combined_openings[fen][move] += data[fen][move]

                        
# export the combined openings to a json file
export_file_path = "openings.json"
with open(export_file_path, "w") as file:
    json.dump(combined_openings, file)