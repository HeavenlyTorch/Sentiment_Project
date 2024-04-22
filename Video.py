import h5py

# Attempt to open the file to see its internal structure
model_path = 'model.h5'
try:
    with h5py.File(model_path, 'r') as file:
        print(list(file.keys()))  # List all main groups in the HDF5 file
except Exception as e:
    print("Failed to read the file:", e)
