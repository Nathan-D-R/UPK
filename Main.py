import requests
import os
import subprocess

def download_file(url, directory="Data", filename=None):
    if filename is None:
        filename = url.split('/')[-1]
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {filename} to {filepath}")

def run_python(script_name):
    subprocess.run(["python", script_name], check=True)
    print(f"Ran script {script_name}")

def run_sas(script_name):
    subprocess.run(["sas", script_name], check=True)
    print(f"Ran script {script_name}")

urls = [
    "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov19.xlsx",
    "https://nieer.org/sites/default/files/2023-12/state_preschool_quality_standards_met.xlsx",
    "https://nieer.org/sites/default/files/2023-12/state_preschool_spending.xlsx",
    "https://nieer.org/sites/default/files/2023-12/state_preschool_enrollment.xlsx"
]

def main():
    for url in urls:
        download_file(url)

    run_python("DataCleaning.py")

    #run_sas("Regression.sas")

if __name__ == "__main__":
    main()
