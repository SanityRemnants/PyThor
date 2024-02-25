
USERNAME = "kdrozd"
PASSWORD = "Death5142"
# Import modules
import copernicusmarine

# Set parameters
data_request = {
   "dataset_id_sst_gap_l3s" : "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m",
   "longitude" : [-6.17, -5.09],
   "latitude" : [35.75, 36.29],
   "time" : ["2023-01-01", "2023-01-31"],
   "variables" : ["sea_surface_temperature"]
}

# Load xarray dataset
sst_l3s = copernicusmarine.open_dataset(
    dataset_id = data_request["dataset_id_sst_gap_l3s"],
    minimum_longitude = data_request["longitude"][0],
    maximum_longitude = data_request["longitude"][1],
    minimum_latitude = data_request["latitude"][0],
    maximum_latitude = data_request["latitude"][1],
    start_datetime = data_request["time"][0],
    end_datetime = data_request["time"][1],
    variables = data_request["variables"],username=USERNAME,password=PASSWORD
)

# Print loaded dataset information
print(sst_l3s["sea_surface_temperature"])
print(sst_l3s["sea_surface_temperature"].values[0][1])
print(sst_l3s["sea_surface_temperature"]["longitude"].values)
