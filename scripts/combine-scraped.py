import os
import pandas as pd

data_path = 'data/polizei'
files = os.listdir(data_path)
dataframes = []
for file in files:
    try:
      file_path = os.path.join(data_path, file)
      df = pd.read_csv(file_path)
      dataframes.append(df)
    except Exception as e:
      print(f"Skipping {file}: {e}")

combined = pd.concat(dataframes, ignore_index=True).drop_duplicates()
combined.to_csv(os.path.join('data', 'crimes.csv'))
