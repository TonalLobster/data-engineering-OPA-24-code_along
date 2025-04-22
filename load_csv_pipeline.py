import pandas as pd
import dlt
from pathlib import Path
import os


#used for extracting data from source, in this case a local csv file
@dlt.resource(write_disposition="replace")
def load_csv_resource(file_path: str, **kwargs):
    df = pd.read_csv(file_path, **kwargs)
    yield df


if __name__ == "__main__":
    # Utgå från där skriptfilen finns
    current_file_path = Path(__file__).resolve()
    project_dir = current_file_path.parent  # Projektets rotkatalog
    
    # Om du behöver ändra arbetskatalogen (oftast inte nödvändigt)
    os.chdir(project_dir)
    
    # Skapa sökväg till CSV-filen
    csv_path = project_dir / "data" / "NetflixOriginals.csv"
    
    # Kontrollera att filen finns
    if not csv_path.exists():
        print(f"Filen existerar inte på: {csv_path}")
        print(f"Aktuell arbetskatalog: {os.getcwd()}")
        exit(1)
        
    data = load_csv_resource(str(csv_path), encoding="latin1")
    
    pipeline = dlt.pipeline(
        pipeline_name='movies',
        destination=dlt.destinations.duckdb("movies.duckdb"),
        dataset_name='staging'
        )
    
    load_info = pipeline.run(data, table_name="netflix")

    # pretty print the information on data that was loaded
    print(load_info)