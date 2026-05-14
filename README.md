# Bachelor Project Title
Bachelor project in Data Science at the IT University of Copenhagen (ITU). The study of the use of genetic algorithms to create and optimize metro networks, in particular the Copenhagen metro system.

## Repository structure

genetic-algorithms-metro-optimization/
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

- `basic_genetic/` - Jupyter notebooks implementing data preparation, grid creation, population allocation, and genetic algorithm experiments
     - `GA_synthetic.ipynb` - TBA
     - `GA_district_pop.ipynb`- TBA
     - `GA_extensions.ipynb` - Main extension notebook with preprocessing, OD generation, evaluation, and visualization

- `data/`
     - `Postal_code_data/` - Population data based on postal codes and district regions (TBA)
     - `raw/` - Original, untouched data
          - `GTFS_Copenhagen.zip/` - contains transit feed data used to identify metro stops and routes (TBA)
          - `README.md` - TBA
     - `od_data_matrix.csv` - Looks like it is the the same file as the next one
     - `synthetic_od_data_matrix.csv` - TBA

- `src/`
     - `preprocessing.py`-  Data cleaning and required preprocessing functions, before implementing algorithm
     - `analysis.py` - Analysis function
     - `algorithms.py` - Model/Algorithm training and evaluation
     - `visualizations.py`- Plotting functions

- `.gitignore` - Files ignored by Git
- `README.md` - Project description and instructions
- `data_loading.ipynb` - Exploratory notebook used during EDA for loading, filtering, and projecting GTFS data before structuring the final research workflow
- `requirements.txt` - Python dependencies

## Installation

1. Clone the repository.
2. Create a Python virtual environment.
3. Install dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage - how to run the code

- Open the notebooks in `basic_genetic/` using Jupyter Notebook or JupyterLab:

- For example, start with `basic_genetic/GA_synthetic.ipynb` for the main workflow:
  - grid creation
  - synthetic population creation
  - OD matrix preparation
  - running the Genetic algorithm
  - Genetic algorithm evaluation

- This notebook uses the Python modules imported from:
  - `src/preprocessing.py`
  - `src/analysis.py`
  - `src/algorithms.py`
  - `src/visualizations.py`

## Algorithms - ???



## Notes

- This repository isresearch-oriented.
- Use the notebooks to follow the full data processing and algorithm pipeline.
- Results can be saved in `Results/` after the notebook cells or scripts are executed.