# Merge Kenmei Backp Files into a single file backup file
 Merge kenmei backup files into a singe file so all removed entries and latest entries all all available in a single file


## Setup
- Create A `Raw-Backup` folder in this project
- Copy over all Kenmei csv exports into `Raw-Backup`
  - All files should be the original name exported from Kenmei

- Open Terminal/Command Prompt in this project and execute the following code depending on the system you use.
```Terminal
python3 -m venv .venv
source .venv/bin/activate        # On Linux/macOS
.venv\Scripts\activate.bat       # On Windows Command Prompt
.venv\Scripts\Activate.ps1       # On Windows PowerShell
pip3 install -r requirements.txt
```
- Verify this by running `which python` and it should return `${path to project}/.venv/bin/python`

### Using Jupyter Notebook
- Optional: change `backup_filename` value if you want custom merged backup file name
- Open `GenerateCompleteBackup.ipynb` and run all cells

### Using Python script
- Optional: change `backup_filename` value if you want custom merged backup file name
- In your Terminal/Command Prompt run `python3 GenerateCompleteBackup.py`
