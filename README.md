# A Study on the Generation and Development of Metro Networks Using Genetic Algorithms
Bachelor project in Data Science at the IT University of Copenhagen (ITU). The study of the use of genetic algorithms to create and optimize metro networks, in particular the Copenhagen metro system.

## Key Features

- Genetic algorithm implementation for metro network design and optimization
- Multiple research stages: synthetic demand, build-from-scratch, and network extensions
- Automated evaluation using demand coverage metrics
- Visualization and result extraction tools
- Full data processing pipeline from raw GTFS data to optimized networks

## Repository structure

genetic-algorithms-metro-optimization/
- `Genetic_algo/` - **Jupyter notebooks for the genetic algorithm workflow: preprocessing, OD matrix preparation, algorithm execution, evaluation, and visualizations**
     - `GA_synthetic.ipynb` -  main notebook for synthetic demand experiments
     - `GA_district_pop.ipynb`- main notebook for build-from-scratch metro network experiments, including population data 
     - `GA_extensions.ipynb` - main notebook for current metro network extensions

- `Results/`

     Research stages:
     - `Synthetic/` - Base 
     - `Built_from_scratch_population/` - Base+
     - `Extension_Population/` - Base++

     For each research stage folder:
     - `*_best_by_coverage.csv` - per-cycle best coverage metrics
     - `*_best_by_coverage_averages.csv` - average metrics across cycles
     - `Cycle_01/` … `Cycle_10/` - per-cycle run output with:
          - one `.pkl` file with saved run state
          - two image files with visualizations

- `Visualizations_notebooks/` - **Report and presentation notebooks** 
     - `Implement_M5_visual.ipynb` - Visualization of M5 implementation and network design
     - `Population_visualizations.ipynb` - Visualizations for population-based research results
     - `Synthetic_visualizations.ipynb` - Visualizations for synthetic demand experiments
     
Contains utility functions embedded within notebooks (functions should ideally be in `src/`)
Used primarily for generating figures, tables, and visual reports from research results.

- `data/`
     - `Postal_code_data/` - Population and geographic data for postal code districts
          - `20264139490617746621POSTNR139926258718.csv` - Population counts by Danish postal code
          - `86249533323639c4792ccbd48b0d9449f543d83f9e5a2f612a7ae700bb08c9ac/wgs84_geojson/` - GeoJSON boundaries for postal code districts (WGS84 projection)
     - `raw/` - Original, untouched data
          - `GTFS_Copenhagen.zip/` - contains transit feed data used to identify metro stops and routes, not stored in GitHub, due to the size
          - `README.md` - explanation of the data location
     - `od_data_matrix.csv` - Origin-destination matrix for Base+ and Base++ stages of the research, based on postal population 
     - `synthetic_od_data_matrix.csv` - Origin-destination matrix for Base stage of the research, the range is based on the number of passengers in Copenhagen metro stations.

- `src/`
     - `preprocessing.py`-  Data cleaning and required preprocessing functions, before implementing algorithm
     - `algorithms.py` - Model/Algorithm training and evaluation
     - `visualizations.py`- Plotting functions

- `.gitignore` - Files ignored by Git
- `README.md` - Project description and instructions
- `gtfs_data_loading.ipynb` - Exploratory notebook used during EDA for loading, filtering, and projecting GTFS data before structuring the final research workflow
- `requirements.txt` - Python dependencies

## Prerequisites

- Recommended Python version: 3.12
- Git
- Virtual environment support (venv, virtualenv, or conda)

## Installation

1. Clone the repository.
2. Create and activate a Python virtual environment:
   - **macOS/Linux:**
     ```sh
     # For recommended Python 3.12:
     python3.12 -m venv .venv
     # Or for any Python 3 version:
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows:**
     ```sh
     # For recommended Python 3.12:
     python3.12 -m venv .venv
     # Or:
     python -m venv .venv
     .venv\Scripts\activate
     ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage - how to run the code

1. Open the notebooks in `basic_genetic/` using Jupyter Notebook or JupyterLab.

2. For example, start with `basic_genetic/GA_synthetic.ipynb` and run cells sequentially:
   - grid creation
   - synthetic population creation
   - OD matrix preparation
   - running the Genetic algorithm
   - Genetic algorithm evaluation

3. The notebooks import and use the following Python modules:
   - `src/preprocessing.py` 
   - `src/analysis.py` 
   - `src/algorithms.py` 
   - `src/visualizations.py` 

4. Results can be saved to `Results/` after execution, follow the instructions given at the beginning of the notebook.

## Algorithms 

- Genetic algorithm for metro network design 
- Encodes candidate networks and evaluates them using demand coverage 
- Uses parent selection, crossover, mutation, and iterative improvement
- Implemented in `src/algorithms.py` and explored in the notebooks for each research stage


## Notes

- This repository isresearch-oriented.
- Use the notebooks to follow the full data processing and algorithm pipeline.
- Results can be saved in `Results/` after the notebook cells or scripts are executed.

## Authors

Jevgenijs Burlakovs and Janus Sebastian Petersen - Bachelor Project, IT University of Copenhagen

## License

This project is provided for educational and research purposes.