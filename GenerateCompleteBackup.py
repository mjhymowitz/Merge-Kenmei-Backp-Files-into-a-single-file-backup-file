# Imports
import pandas as pd
import os
import datetime

# get list of file name with path to csv
# ['./Raw-Backups/kenmei-export-2022-08-27T17_19_00Z.csv']
def get_csv_file_path():
  csv_file_list = sorted(os.listdir(path="./Raw-Backups/"))
  location = "./Raw-Backups/{}"
  return [
    location.format(file_name)
    for file_name in csv_file_list
    if file_name.endswith(".csv")
  ]

# recieve filename and return datetime of file creation
def parse_datetime_from_filename(filename):
  try:
    # Extract datetime string from filename: 'kenmei-export-2022-08-27T17_19_00Z.csv'
    dt_str = filename.split('kenmei-export-')[-1].replace('.csv', '').replace('_', ':').replace('T', ' ')
    return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%SZ")
  except Exception as e:
    raise ValueError(f"Could not parse datetime from filename '{filename}': {e}")

# read MasterBackup.xlsx file, if doesn't exist create MasterBackup.xlsx
def load_history(filepath):
  EXPECTED_COLUMNS = [
    "title", "status", "score", "last_volume_read", "last_chapter_read",
    "last_chapter_title_read", "last_read_at", "migratable",
    "source_to_be_removed_at", "notes", "tracked_site", "series_url", "tags"
  ]

  if os.path.exists(filepath):
    sheet_data = pd.read_excel(filepath, sheet_name=None)

    # Pad MasterData if any columns are missing
    if "MasterData" in sheet_data:
      df = sheet_data["MasterData"]
      for col in EXPECTED_COLUMNS:
        if col not in df.columns:
          df[col] = pd.NA
      sheet_data["MasterData"] = df[EXPECTED_COLUMNS]  # reorder columns
    else:
      sheet_data["MasterData"] = pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Ensure ImportHistory at least has default structure
    if "ImportHistory" not in sheet_data:
      sheet_data["ImportHistory"] = pd.DataFrame(columns=["filename", "file_datetime", "imported_at"])

    return sheet_data

  else:
    return {
      "MasterData": pd.DataFrame(columns=EXPECTED_COLUMNS),
      "ImportHistory": pd.DataFrame(columns=["filename", "file_datetime", "imported_at"])
    }

# merge source_to_be_removed_at and source_removed_at columns and delete source_removed_at column
def merge_source_columns(df):
  # If both columns exist, merge them
  if "source_removed_at" in df.columns and "source_to_be_removed_at" in df.columns:
    # Fill NaNs in source_to_be_removed_at with values from source_removed_at
    df["source_to_be_removed_at"] = df["source_to_be_removed_at"].combine_first(df["source_removed_at"])
    # Drop the old column
    df.drop(columns=["source_removed_at"], inplace=True)

  return df

# save MasterBackup.xlsx file
def save_master(filepath, master_df, history_df):
  with pd.ExcelWriter(filepath, engine='openpyxl', mode='w') as writer:
    master_df.to_excel(writer, index=False, sheet_name="MasterData")
    history_df.to_excel(writer, index=False, sheet_name="ImportHistory")

# Recursively Update MasterBackup content
def recursive_merge(files, idx, master_df, history_df, master_path):
  if idx >= len(files):
    print("✅ All files processed.")
    master_df = merge_source_columns(master_df)
    save_master(master_path, master_df, history_df)
    return

  current_file = files[idx]
  file_dt = parse_datetime_from_filename(current_file)
  filename = os.path.basename(current_file)

  # Skip if already imported
  if filename in history_df["filename"].values:
    print(f"⚠️ {filename} already imported. Skipping.")
    return recursive_merge(files, idx + 1, master_df, history_df, master_path)

  print(f"📂 Importing {filename}")

  new_df = pd.read_csv(current_file)

  # 1. Ensure all new columns exist in master
  for col in new_df.columns:
    if col not in master_df.columns:
      master_df[col] = None

  # 2. Ensure all master columns exist in new_df (fill if missing)
  for col in master_df.columns:
    if col not in new_df.columns:
      new_df[col] = None

  # 3. Update records (assumes "series_url" is unique key)
  for _, new_row in new_df.iterrows():
    match = master_df[master_df['series_url'] == new_row['series_url']]
    if not match.empty:
      index = match.index[0]
      for col in new_df.columns:
        if pd.notna(new_row[col]) and master_df.at[index, col] != new_row[col]:
          master_df.at[index, col] = new_row[col]
    else:
      master_df = pd.concat([master_df, pd.DataFrame([new_row])], ignore_index=True)

  # 4. Record history
  history_df = pd.concat([history_df, pd.DataFrame([{
    "filename": filename,
    "file_datetime": file_dt,
    "imported_at": datetime.datetime.now()
  }])], ignore_index=True)

  return recursive_merge(files, idx + 1, master_df, history_df, master_path)


# Setup
master_backup_filename = "MasterBackup.xlsx"

# Step 1: Get all CSVs and sort them by datetime extracted from filename
all_csvs = get_csv_file_path()

# Step 2: Load existing master and history
loaded = load_history(master_backup_filename)
master_df = loaded["MasterData"]
history_df = loaded["ImportHistory"]

# Step 3: Start recursive import
recursive_merge(all_csvs, 0, master_df, history_df, master_backup_filename)


