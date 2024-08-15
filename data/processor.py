import os
import sys
import logging
import fitz
import pandas as pd

sys.path.append(os.path.abspath(os.path.join("..")))
from src import *

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define directory paths
SCRIPT_DIR = os.getcwd()
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FOLDER_PATH = os.path.join(PARENT_DIR, "data")
PDF_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "pdf")
CSV_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, "csv")

# Ensure the CSV folder exists
ensure_folder_exists(CSV_FOLDER_PATH)


def process_pdf_file(filename):
    """
    Process a PDF file based on its year and save the resulting DataFrame as CSV.
    """

    if match := re.search(r"(\d{4})", filename):
        year = match.group(1)
        file_path = os.path.join(PDF_FOLDER_PATH, filename)
        var_name = os.path.splitext(filename)[0]
        file = fitz.open(file_path)
        logging.info(f"Processing {filename}")

        if year == "2015":
            df = parser_13_to_18(file)
            df.set_index("id", inplace=True)
            if "poster" in filename.lower():
                update_df(df, [po2015_1885W, po2015_3108T, po2015_3034T, po2015_3070T])
            else:
                update_df(df, [pl2015_168])

        elif year == "2019":
            df = parser_19(file)
            if "poster" in filename.lower():
                df["header"] = df["id"].apply(
                    lambda id: next(
                        (
                            topic
                            for topic, (start, end) in topic_mapping_2019.items()
                            if start <= int(id) <= end
                        ),
                        None,
                    )
                )
        elif year == "2021":
            dfs = parser_21(file)
            save_dfs_to_csv(dfs, year, var_name)
            return

        elif year == "2022":
            df = parser_22(file)
            if "poster" in filename.lower():
                df.set_index("id", inplace=True)
                update_df(df, [po2022_1537])

        elif year == "2023":
            df = (
                parser_23_poster(file)
                if "poster" in filename.lower()
                else parser_23_non_poster(file)
            )

        else:
            df = parser_13_to_18(file)

        df["year"] = year
        save_df_to_csv(df, var_name)
    else:
        logging.info(f"Skipping {filename} (No year found)")


def update_df(df, updates):
    """
    Update the DataFrame with specific rows.
    """

    update_df = pd.DataFrame(updates).set_index("id")
    df.update(update_df)
    df.reset_index(inplace=True)


def save_df_to_csv(df, var_name):
    """
    Save the DataFrame as a CSV file.
    """

    csv_path = os.path.join(CSV_FOLDER_PATH, f"{var_name}.csv")
    df.to_csv(csv_path, index=False, escapechar="\\")
    logging.info(f"Saved DataFrame to {csv_path}")


def save_dfs_to_csv(dfs, year, var_name):
    """
    Save multiple DataFrames as separate CSV files.
    """

    suffixes = ["Plenary", "Platform", "Talks", "Presentations"]
    for df, suffix in zip(dfs, suffixes):
        df["year"] = year
        csv_path = os.path.join(CSV_FOLDER_PATH, f"{var_name}-{suffix}.csv")
        df.to_csv(csv_path, index=False, escapechar="\\")
        logging.info(f"Saved DataFrame to {csv_path}")


# Process all PDF files in the folder
for filename in os.listdir(PDF_FOLDER_PATH):
    if filename.endswith("pdf"):
        process_pdf_file(filename)

# List to store DataFrames from all CSV files
all_dfs = []

# Iterate over all files in the CSV folder
for filename in os.listdir(CSV_FOLDER_PATH):
    if filename != ".DS_Store":
        # Construct full path to the CSV file
        csv_path = os.path.join(CSV_FOLDER_PATH, filename)
        df = pd.read_csv(csv_path, encoding="utf-8")
        # Select specific columns from the DataFrame
        try:
            truncated_df = df[["title", "content", "header", "year"]].copy()
        except KeyError:
            truncated_df = df[["title", "content", "year"]].copy()
            truncated_df.loc[:, "header"] = "None"
        # Append the truncated DataFrame to the list
        all_dfs.append(truncated_df)

# Concatenate all DataFrames into a single DataFrame
complete_df = pd.concat(all_dfs, ignore_index=True)

# Replace header values according to the recat_dict dictionary
complete_df["header"] = complete_df["header"].apply(lambda x: recat_dict.get(x, "None"))

# Save the complete DataFrame to a CSV file
complete_df.to_csv(
    os.path.join(DATA_FOLDER_PATH, "complete_data.csv"), index=False, escapechar="\\"
)

# Filter and save labeled data (where header is not 'To split', 'COVID-19', or 'None')
labeled_data = complete_df[
    ~complete_df["header"].isin(["To split", "COVID-19", "None"])
]
labeled_data.to_csv(
    os.path.join(DATA_FOLDER_PATH, "labeled_data.csv"), index=False, escapechar="\\"
)

# Filter and save unlabeled data (where header is 'To split', 'COVID-19', or 'None')
unlabeled_data = complete_df[
    complete_df["header"].isin(["To split", "COVID-19", "None"])
]
unlabeled_data.to_csv(
    os.path.join(DATA_FOLDER_PATH, "unlabeled_data.csv"), index=False, escapechar="\\"
)
