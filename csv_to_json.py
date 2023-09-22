import pandas as pd

data = pd.read_csv('AB_NYC_2019.csv')
json_data = data.to_json(orient='records')
with open('AB_NYC_2019.json', 'w') as json_file:
    json_file.write(json_data)
