
## OEWS Visualizer

### Overview

OEWS Visualizer is a Streamlit-based web application that provides interactive visualizations and analysis of Occupational Employment and Wage Statistics (OEWS) data from the Bureau of Labor Statistics. This tool allows users to explore wage percentiles, job demand, and salary comparisons across different occupations, industries, and geographic levels in the United States.

### Features

- Interactive selection of geographic levels (National, State, Metropolitan)
- Occupation and industry filtering
- Wage distribution histograms
- Wage percentile tables
- Interactive choropleth maps for average salaries and job demand across US states
- Multi-job salary comparison with bar charts
- Raw data explorer with search functionality


### Installation

1. Clone this repository
2. Install the required packages:

```
pip install streamlit numpy pandas plotly
```

3. Ensure you have the necessary data file: `data/all_data_M_2023.parquet`

### Usage

Run the Streamlit app:

```
streamlit run app.py
```


### Data Upload

Users can upload custom Excel files from the BLS website (https://www.bls.gov/oes/tables.htm). The app currently supports [All data] Excel files from 2020 and later.

### Dependencies

- Streamlit
- NumPy
- Pandas
- Plotly


### Data Source

Data is sourced from the Bureau of Labor Statistics, Occupational Employment and Wage Statistics 2023.

### Creator

Created by [Shawn Wang](https://github.com/ShouzhiWang)

### Note

'N/A' in the visualizations indicates missing or unavailable data.