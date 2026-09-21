from src.data_loader import DataLoader
import pandas as pd

# Initialize loader
loader = DataLoader()

# Option 1: Heart Disease Dataset
def load_heart_disease():
    """
    Load the Heart Disease dataset (processed Cleveland data, UCI ML Repository /
    Kaggle "Heart Disease Dataset").

    This CSV is the widely-used 1025-row version of the dataset, which is the
    original 303-instance Cleveland set repeated with some duplication - the
    cleaning notebook detects and removes those duplicate rows.

    Place heart.csv in data/raw/ before running this function, or point `path`
    at wherever you've stored it.
    """
    path = "data/raw/heart.csv"
    df = pd.read_csv(path)

    # Reorder so the diagnosis target sits near the front - this is the
    # column most of the analysis (grouped boxplots, colored scatter plots)
    # cares about.
    column_order = [
        "age", "target", "sex", "cp", "trestbps", "chol", "fbs",
        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal",
    ]
    df = df[column_order]
    return df

# Option 2: Student Performance
def load_student_performance():
    """Load Student Performance dataset from UCI."""
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip"
    # Note: This needs unzipping - alternative: download manually
    return None

# Option 3: Temperature
def load_temperature():
    """Load NASA temperature data."""
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    return loader.load_from_url(url, "temperature.csv")

# Option 4: COVID-19
def load_covid():
    """Load COVID-19 data from Our World in Data."""
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    return loader.load_from_url(url, "covid_data.csv")

# Choose your dataset
df = load_heart_disease()

# Save raw data
loader.save_processed_data(df, "raw_data.csv")
print(f"Dataset loaded: {df.shape}")
