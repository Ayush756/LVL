import pandas as pd
import numpy as np

from sqlalchemy import create_engine
user = 'kishor'
password = 'kishor'
host = 'localhost'
port = '5432'
database = 'LVL'
table_name = 'competitors'

connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)
df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
comps = df.to_dict(orient='records')
print("Competitors loaded from database:")

names = np.array(df['name'])
capacities = np.array(df['capacity'])
varieties = np.array(df['variety'])
populations = np.array(df['population'])
pop_grids = np.array(df['popGrid'])
distances = np.array(df['distance'])
costs = np.array(df['cost'])

print("Names:", names)
print("Capacities:", capacities)
print("Populations:", populations)