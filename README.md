# Bachelor Project Title
Bachelor project in Data Science at the IT University of Copenhagen (ITU). The study of the use of genetic algorithms to create and optimize metro networks, in particular the Copenhagen metro system.

## Repository structure

genetic-algorithms-metro-optimization/
- `Results/`
     - `extraction_performers.py` - script for extracting performance metrics (TBA)

     Research stages:
     - `Synthetic/` - Base 
     - `Built_from_scratch_population/` - Base+
     - `Extension_Population/` - Base++

     For each of these research stage its own folder contains:
      - `*_best_by_coverage.csv` - per-cycle metric based on best performer
      - `*_best_by_coverage_averages.csv` - average metrics across cycles
      - `Cycle_01/ … Cycle_10/` - per-cycle run output, including: pickle file with saved run state, two image files with visualizations

- `basic_genetic/` - Jupyter notebooks implementing algorithms
     - `GA_synthetic.ipynb` -  main notebook for synthetic demand experiments, including preprocessing, synthetic OD matrix preparation, evaluation, and visualizations
     - `GA_district_pop.ipynb`- main notebook for build-from-scratch metro network experiments, including population data with preprocessing, OD matrix preparation, evaluation, and visualizations
     - `GA_extensions.ipynb` - Main extension notebook with preprocessing, OD generation, evaluation, and visualizations

- `data/`
     - `Postal_code_data/` - Population data based on postal codes and district regions (TBA)
     - `raw/` - Original, untouched data
          - `GTFS_Copenhagen.zip/` - contains transit feed data used to identify metro stops and routes (TBA)
          - `README.md` - explanation of the data location
     - `od_data_matrix.csv` - Looks like it is the the same file as the next one (TBA)
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

## Algorithms 

- Genetic algorithm for metro network design 
- Encodes candidate networks and evaluates them using demand coverage 
- Uses parent selection, crossover, mutation, and iterative improvement
- Implemented in `src/algorithms.py` and explored in the notebooks for each research stage


## Notes

- This repository isresearch-oriented.
- Use the notebooks to follow the full data processing and algorithm pipeline.
- Results can be saved in `Results/` after the notebook cells or scripts are executed.