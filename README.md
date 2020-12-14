# parse-google-drive
Get a list of files from Google Drive and Store it to MS SQL Database

## Configuring and Running Script


##### 1. First, Create virtualenv

```bash
virtualenv venv
```

##### 2. Activate virtualenv

```bash
source venv/bin/activate
```

##### 3. Install python packages

```bash
pip install -r requirements.txt
```

##### 4. Create .env from .env.example and fill in Folders on Google Drive and DB settings


##### 5. Download credentials from API Console and move it to **client_secrets.json** in project directory


##### 6. Run script
```bash
python main.py
```


## PyDrive Library

- https://pythonhosted.org/PyDrive/
- https://pythonhosted.org/PyDrive/quickstart.html (Authentication)

## pyodbc Library

- https://pypi.org/project/pyodbc/