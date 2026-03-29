import json

with open(r"D:\CODING\AirBeat\templates\Close_Open_Hand.json", "r") as file:
    data = json.load(file)

print(data[0]['representative_vector'])