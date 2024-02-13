from football_api_extractor import FootballAPI as Extractor 
from load_data import DataLoader

# Instantiate Extractor and DataLoader
extractor = Extractor()
loader = DataLoader()

# Establish connection
loader.connect()

# Extract data
data = extractor.get_data()
# Write data
loader.write_data(data_df=data)

q = """ select * from fixtures """
print(loader.query(q))