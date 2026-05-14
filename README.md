# Bachelor Project Title
Bachelor project in Data Science at the IT University of Copenhagen (ITU). The study of the use of genetic algorithms to create and optimize metro networks, in particular the Copenhagen metro system.

## Repository structure

genetic-algorithms-metro-optimization/
- `README.md` - Project description and instructions
- `requirements.txt` - Python dependencies
- `.gitignore` - Files ignored by Git

- `basic_genetic/` - Jupyter notebooks implementing data preparation, grid creation, population allocation, and genetic algorithm experiments
     - `GA_synthetic.ipynb` - TBA
     - `GA_district_pop.ipynb`- TBA
     - `GA_extensions.ipynb` - Main extension notebook with preprocessing, OD generation, evaluation, and visualization

- `Results/`
     - `extraction_performers.py` - script for extracting performance metrics (TBA)

     - `Synthetic/`
          - `Synthetic_best_by_coverage_averages.csv` -
          - `Synthetic_best_by_coverage.csv` -
          - `Cycle_01/` … `Cycle_10/` -

     - `Built_from_scratch_population/` 
          - `Built_from_scratch_population_best_by_coverage_averages.csv` -
          - `Built_from_scratch_population_best_by_coverage.csv` -
          - `Cycle_01/` … `Cycle_10/` - 

     - `Extension_Population/`
          - `Extension_Population_best_by_coverage_averages.csv` -
          - `Extension_Population_best_by_coverage.csv` -
          - `Cycle_01/` … `Cycle_10/` -

- `data/`
     - `Postal_code_data/` - Population data based on postal codes and district regions (TBA)
     - `raw/` - Original, untouched data
          - `GTFS_Copenhagen.zip/` - TBA
          - `README.md` - TBA
     - `od_data_matrix.csv` - Looks like it is the the same file as the next one
     - `synthetic_od_data_matrix.csv` - TBA

- `src/`
     - `preprocessing.py`-  Data cleaning and required preprocessing functions, before implementing algorithm
     - `analysis.py` - Analysis function
     - `algorithms.py` - Model/Algorithm training and evaluation
     - `visualizations.py`- Plotting functions


- `data_loading.ipynb` - Exploratory notebook used during EDA for loading, filtering, and projecting GTFS data before structuring the final research workflow


## Installation - steps before running the code 

## Usage - how to run the code

## Algorithms - ???



