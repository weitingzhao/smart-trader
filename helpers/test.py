from chartmill_files import fetch_dataset

date = "2024-12-09"
file_pattern = "SEPA_chartmill_export_"
dataset = fetch_dataset(date, file_pattern)
if dataset is not None:
    print(dataset.head())
else:
    print("Dataset could not be fetched.")
