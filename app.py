import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(page_title="OEWS Visualizer", page_icon="📊", layout="wide")


# Function to clean numeric columns (consistent with generate_data.py)
def clean_numeric(x):
    if isinstance(x, str):
        if x == "**" or x == "#":
            return np.nan
        else:
            return x.replace(",", "").replace("%", "")
    return x

# Function to process uploaded Excel files
def process_excel(file):
    df = pd.read_excel(file)
    # Apply cleaning function to all columns
    for col in df.columns:
        df[col] = df[col].apply(clean_numeric)
    # Convert to numeric, coercing errors to NaN
    for col in df.columns:
        if col not in ["AREA_TITLE", "PRIM_STATE", "NAICS", "NAICS_TITLE", "I_GROUP", "OCC_CODE", "OCC_TITLE", "O_GROUP"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# Modified load_data function
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return process_excel(uploaded_file)
    else:
        return pd.read_parquet("data/all_data_M_2023.parquet")



# Add file uploader to sidebar
fileUpload = st.sidebar.checkbox("Upload Custom Data", value=False)
if fileUpload:
    st.sidebar.info("Please upload an Excel file from https://www.bls.gov/oes/tables.htm. \n\nDue to OEWS format changes over the past years, as of now this program only supports [All data] of 2020 and later.")
    uploaded_file = st.sidebar.file_uploader("Upload Excel file", type={"xlsx", "xls"})
    df = load_data(uploaded_file)
else:
    df = load_data(None)   

# Load data based on user input



st.title("📊 Wage Percentiles Explorer")


# Helper function to get unique sorted values
@st.cache_data
def get_unique_sorted(column):
    return sorted(df[column].unique())


# Initialize query parameters
if "geo_level" not in st.query_params:
    st.query_params["geo_level"] = "National"
if "selected_geo" not in st.query_params:
    st.query_params["selected_geo"] = "National"
if "selected_job" not in st.query_params:
    st.query_params["selected_job"] = get_unique_sorted("OCC_TITLE")[0]

# Sidebar for user input
st.sidebar.header("Select Filters")

# Geography selection
geo_level = st.sidebar.selectbox(
    "Geographic Level",
    ["National", "State", "Metropolitan"],
    index=["National", "State", "Metropolitan"].index(
        st.query_params["geo_level"]
    ),
)

if geo_level == "National":
    selected_geo = "National"
elif geo_level == "State":
    selected_geo = st.sidebar.selectbox(
        "Select State",
        get_unique_sorted("PRIM_STATE"),
        index=(
            get_unique_sorted("PRIM_STATE").index(
                st.query_params["selected_geo"]
            )
            if st.query_params["selected_geo"]
            in get_unique_sorted("PRIM_STATE")
            else 0
        ),
    )
else:
    selected_geo = st.sidebar.selectbox(
        "Select Metropolitan Area",
        get_unique_sorted("AREA_TITLE"),
        index=(
            get_unique_sorted("AREA_TITLE").index(
                st.query_params["selected_geo"]
            )
            if st.query_params["selected_geo"]
            in get_unique_sorted("AREA_TITLE")
            else 0
        ),
    )

# Checkbox for selecting all industries
all_industries = st.sidebar.checkbox("All Industries", value=True)

# Industry selection dropdown (only enabled if "All Industries" is not checked)
if all_industries:
    selected_industry = None  # Represents all industries
else:
    selected_industry = st.query_params.get("selected_industry")
    if selected_industry not in get_unique_sorted("NAICS_TITLE"):
        selected_industry = get_unique_sorted("NAICS_TITLE")[0]  # Fallback to first industry

    selected_industry = st.sidebar.selectbox(
        "Select Industry",
        get_unique_sorted("NAICS_TITLE"),
        index = get_unique_sorted("NAICS_TITLE").index(selected_industry)
    )


# Filter occupations based on selection
if all_industries:
    filtered_occupations = get_unique_sorted("OCC_TITLE")
else:
    filtered_occupations = sorted(df[df["NAICS_TITLE"] == selected_industry]["OCC_TITLE"].unique())

# Job selection with safe index handling
default_job = st.query_params.get("selected_job")

# If the stored job is not in the filtered list, fall back to the first available option
if default_job not in filtered_occupations:
    default_job = filtered_occupations[0] if filtered_occupations else None

if filtered_occupations:
    if default_job not in filtered_occupations:
        default_job = filtered_occupations[0] if filtered_occupations else None

    if filtered_occupations:
        selected_job = st.sidebar.selectbox(
            "Select Occupation", filtered_occupations,
            index=filtered_occupations.index(default_job) if default_job else 0
        )
    else:
        st.sidebar.warning("No occupations available for the selected industry.")
        selected_job = None

else:
    st.sidebar.warning("No occupations available for the selected industry.")
    selected_job = None


# # Update query parameters
# st.query_params["geo_level"] = geo_level
# st.query_params["selected_geo"] = selected_geo
# st.query_params["selected_job"] = selected_job
# st.query_params["selected_industry"] = selected_industry

# Filter data
if geo_level == "National":
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] == "U.S.")
    ]
elif geo_level == "State":
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["PRIM_STATE"] == selected_geo)
    ]
else:
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] == selected_geo)
    ]

# Display results
if geo_level == "National":
    st.header(f"{selected_job} in the United States")
else:
    st.header(f"{selected_job} in {selected_geo}")






if not filtered_df.empty:
    # Display wage frequency histogram
    fig = px.histogram(
    filtered_df,
    x="A_MEAN",
    nbins=30,
    title="Wage Distribution",
    labels={"A_MEAN": "Average Annual Wage", "count": "Frequency"}
)
    fig.update_layout(yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)

    # Display percentiles
    st.subheader("Wage Percentiles")
    percentiles = [
        "H_PCT10",
        "H_PCT25",
        "H_MEDIAN",
        "H_PCT75",
        "H_PCT90",
        "A_PCT10",
        "A_PCT25",
        "A_MEDIAN",
        "A_PCT75",
        "A_PCT90",
    ]
    percentile_labels = ["10th", "25th", "50th (Median)", "75th", "90th"]

    wage_data = filtered_df[percentiles].iloc[0]
    wage_df = pd.DataFrame(
        {
            "Percentile": percentile_labels,
            "Hourly": wage_data[percentiles[:5]].values,
            "Annual": wage_data[percentiles[5:]].values,
        }
    )

    wage_df["Hourly"] = wage_df["Hourly"].apply(
        lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A"
    )
    wage_df["Annual"] = wage_df["Annual"].apply(
        lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
    )

    st.table(wage_df.set_index("Percentile"))

    

    


else:
    st.warning(
        "No data available for the selected combination of job and geography."
    )












st.subheader("Interactive Maps")
# Display maps of national level location quotient (for job demand) and average salaries

# Filter for the selected occupation and exclude national-level data
occupation_data = df[(df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] != "U.S.")]

if not occupation_data.empty:
    # Assume df and selected_job are already defined

    # Prepare the data
    state_avg_salaries = df[(df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] != "U.S.")].groupby('PRIM_STATE').agg({
        'A_MEAN': 'mean',
        'TOT_EMP': 'sum',  # Adding total employment for each state
        'A_PCT10': 'mean',  # 10th percentile wage
        'A_PCT90': 'mean'  # 90th percentile wage
    }).reset_index()

    state_avg_salaries.columns = ['PRIM_STATE', 'Average Salary', 'Total Employment', 'Lower Wage', 'Upper Wage']

    # Create the choropleth map
    fig = px.choropleth(
        state_avg_salaries,
        locations='PRIM_STATE',
        color='Average Salary',
        locationmode='USA-states',
        scope="usa",
        color_continuous_scale="Viridis",
        custom_data=['PRIM_STATE', 'Average Salary', 'Total Employment', 'Lower Wage', 'Upper Wage'],
        title= f'Average Salaries of {selected_job} Across US States'

    )

    # Update layout for interactivity
    fig.update_layout(
        clickmode='event+select',
        margin=dict(t=30, b=0),
        autosize=False,
        width=600,
        height=400,
    )

    # Add hover template
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>" +
        "Average Salary: $%{customdata[1]:.2f}<br>" +
        "Total Employment: %{customdata[2]}<br>" +
        "Wage Range: $%{customdata[3]:.2f} - $%{customdata[4]:.2f}<extra></extra>"
        
    )
    

    # Create a placeholder for the clicked state info
    clicked_state_info = st.empty()

    # Use Streamlit's experimental_rerun to handle map clicks
    def handle_click(trace, points, state):
        if len(points.point_inds) > 0:
            index = points.point_inds[0]
            clicked_state = state_avg_salaries.iloc[index]
            st.session_state.clicked_state = clicked_state
            st.experimental_rerun()

    # Display the chart

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False})
    st.divider()

    # Check if a state was clicked and display its information
    if 'clicked_state' in st.session_state:
        clicked_state = st.session_state.clicked_state
        clicked_state_info.write(f"""
        ### Details for {clicked_state['PRIM_STATE']}
        - Average Salary: ${clicked_state['Average Salary']:,.2f}
        - Total Employment: {clicked_state['Total Employment']:,}
        - Wage Range: ${clicked_state['Lower Wage']:,.2f} - ${clicked_state['Upper Wage']:,.2f}
        """)

        

    # Add a callback to handle clicks
    fig.data[0].on_click(handle_click)




    # Calculate total employment per state
    state_total_emp = df[df["AREA_TITLE"] != "U.S."].groupby('PRIM_STATE')['TOT_EMP'].sum().reset_index()
    state_total_emp.columns = ['PRIM_STATE', 'Total_State_Emp']

    # Merge to get employment for the selected job per state
    state_occupation_data = occupation_data.groupby('PRIM_STATE')['TOT_EMP'].sum().reset_index()
    state_occupation_data.columns = ['PRIM_STATE', 'Job_Emp']

    # Merge total employment and job-specific employment
    state_avg_demand = state_occupation_data.merge(state_total_emp, on='PRIM_STATE')

    # Compute national employment for the occupation and total employment
    national_job_emp = df[(df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] == "U.S.")]['TOT_EMP'].values[0]
    national_total_emp = df[df["AREA_TITLE"] == "U.S."]['TOT_EMP'].sum()

    # Calculate Location Quotient (LQ)
    state_avg_demand['LQ'] = (state_avg_demand['Job_Emp'] / state_avg_demand['Total_State_Emp']) / \
                            (national_job_emp / national_total_emp)


    # Create choropleth map using LQ
    fig = px.choropleth(
        state_avg_demand,
        locations='PRIM_STATE',
        color='LQ',
        locationmode='USA-states',
        scope="usa",
        color_continuous_scale="Plasma",
        title= f"Job Demand of {selected_job} Across US States",
        labels={'LQ': 'Demand', 'PRIM_STATE': 'State'}

    )

    fig.update_layout(
        margin=dict(t=30, b=0),
        autosize=False,
        width=600,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False})



    # Add explanation for Location Quotient
    with st.expander("Understanding Job Demand"):
        st.markdown("""
        Job demand is calculated using the Location Quotient (LQ) formula:
        """)
        st.latex(r"""
        LQ = \frac{\left(\frac{\text{Job Employment in State}}{\text{Total Employment in State}}\right)}{\left(\frac{\text{Job Employment Nationally}}{\text{Total Employment Nationally}}\right)}
        """)
        st.markdown("""
        The Location Quotient (LQ) helps identify regions with higher or lower demand for a specific job relative to the national average. 
        An LQ greater than 1 indicates higher demand or specialization for that job in a state.
        """)

    st.divider()

    

    
else:
    st.warning(
        "No maps available for the selected combination of job and geography. There probably is no state-level data available. \nPlease try another selection."
    )



if geo_level == "State" or geo_level == "Metropolitan":
    st.subheader("Compare Salaries Across Multiple Jobs in " + selected_geo)   
    st.info("Data may not be available for all jobs under the State or Metropolitan levels.")
else:
    st.subheader("Compare Salaries Across Multiple Jobs in the United States")
def filter_data_by_geo_level(df, geo_level, selected_geo, selected_job):
    if geo_level == "National":
        return df[df["AREA_TITLE"] == "U.S."]
    elif geo_level == "State":
        return df[(df["PRIM_STATE"] == selected_geo)]
    elif geo_level == "Metropolitan":
        return df[(df["AREA_TITLE"] == selected_geo)]
    return df


def compare_salaries(jobs, df, geo_level, selected_geo):
    filtered_df = filter_data_by_geo_level(df, geo_level, selected_geo, selected_job)
    salaries = []
    for job in jobs:
        salary = filtered_df[filtered_df['OCC_TITLE'] == job]['A_MEAN'].mean()
        salaries.append(f"{salary:.2f}")
    return pd.DataFrame({'Job': jobs, 'Average Annual Salary ($)': salaries})




# Allow the user to select multiple jobs
selected_jobs = st.multiselect(
    "Select jobs to compare",
    options=get_unique_sorted('OCC_TITLE'),
    default=[selected_job]  # Include the initially selected job
)

# Compare salaries if at least one job is selected
if selected_jobs:
    comparison_df = compare_salaries(selected_jobs, df, geo_level, selected_geo)
    st.table(comparison_df)

    # Create a bar chart to visualize salary rankings
    fig = px.bar(comparison_df, x='Job', y='Average Annual Salary ($)', 
                 title='Salary Comparison',
                 labels={'Average Annual Salary ($)': 'Average Annual Salary ($)'},
                 text='Average Annual Salary ($)'
                 )
    fig.update_traces(texttemplate='$%{text:.2f}')
    #fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select at least one job to compare.")


if not filtered_df.empty:
    # Display additional information
    st.divider()
    st.subheader("Additional Information")
    info_columns = ["TOT_EMP", "JOBS_1000", "LOC_QUOTIENT"]
    info_labels = ["Total Employment", "Jobs per 1,000", "Location Quotient"]

    info_data = filtered_df[info_columns].iloc[0]
    info_df = pd.DataFrame({"Metric": info_labels, "Value": info_data.values})
    info_df["Value"] = info_df["Value"].apply(
        lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A"
    )
    st.table(info_df.set_index("Metric"))

st.sidebar.header("Explore Raw Data")
show_raw_data = st.sidebar.checkbox("Show Raw Data", value=False)

st.divider()

if show_raw_data:
    st.subheader("Raw Data Explorer")
    st.markdown("Use this table to explore and filter raw data.")
    filtered_df = df  # Start with all data
    
    # Add a text input for searching specific occupations
    search_term = st.text_input("Search Occupation", selected_job)
    if search_term:
        filtered_df = df[df["OCC_TITLE"].str.contains(search_term, case=False, na=False)]

    st.dataframe(filtered_df)

# Data source and notes
st.sidebar.markdown("---")
st.sidebar.info(
    "Data Source: [Bureau of Labor Statistics, Occupational Employment and Wage Statistics 2023](https://www.bls.gov/oes/)"
    "\n\nNote: 'N/A' or 'NaN' indicates missing or unavailable data."
    "\n\nCreated by [Shawn Wang](https://github.com/ShouzhiWang)",
    
)




