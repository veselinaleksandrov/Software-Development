import os
from urllib.parse import parse_qs, urljoin, urlparse

import gspread
import pandas as pd
import requests
from google.oauth2.credentials import Credentials


def validate_url(url: str):
  parsed = urlparse(url, allow_fragments=True)
  if (parsed.scheme != "https" \
      or not parsed.netloc.endswith("google.com")
      or not parsed.path.startswith("/spreadsheets/d/")
      or not parsed.path.endswith("/edit")
     ):

    raise ValueError("Invalid Google Sheets URL format")
  if "gid" not in parsed.fragment:
    raise ValueError("gid parameter missing in the URL")
  elif not parse_qs(parsed.fragment).get('gid'):
    raise ValueError("gid parameter missing in the URL")


def fetch_connector_credentials():
  hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
  if not hostname:
    raise Exception('REPLIT_CONNECTORS_HOSTNAME environment variable not found')
  
  x_replit_token = None
  if os.environ.get('REPL_IDENTITY'):
    x_replit_token = 'repl ' + os.environ['REPL_IDENTITY']
  elif os.environ.get('WEB_REPL_RENEWAL'):
    x_replit_token = 'depl ' + os.environ['WEB_REPL_RENEWAL']
  
  if not x_replit_token:
    raise Exception('Authentication token not found (REPL_IDENTITY or WEB_REPL_RENEWAL required)')
  
  response = requests.get(
    f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet',
    headers={
      'Accept': 'application/json',
      'X_REPLIT_TOKEN': x_replit_token
    }
  )
  
  if not response.ok:
    raise Exception(f'Failed to fetch connector credentials: HTTP {response.status_code} - {response.text}')
  
  data = response.json()
  items = data.get('items', [])
  
  if not items:
    raise Exception('Google Sheets connector not set up. Please connect your Google Sheets account.')
  
  connection_settings = items[0]
  settings = connection_settings.get('settings', {})
  
  access_token = settings.get('access_token')
  if not access_token:
    oauth_creds = settings.get('oauth', {}).get('credentials', {})
    access_token = oauth_creds.get('access_token')
  
  if not access_token:
    raise Exception('Access token not found in connector response')
  
  refresh_token = settings.get('refresh_token')
  token_uri = settings.get('token_uri', 'https://oauth2.googleapis.com/token')
  client_id = settings.get('client_id')
  client_secret = settings.get('client_secret')
  
  return Credentials(
    token=access_token,
    refresh_token=refresh_token,
    token_uri=token_uri,
    client_id=client_id,
    client_secret=client_secret
  )


def get_gspread_client():
  credentials = fetch_connector_credentials()
  gc = gspread.authorize(credentials)
  return gc


def load_worksheet_from_url(spreadsheet_url: str,
                            worksheed_gid: str) -> pd.DataFrame:
  url = urljoin(spreadsheet_url, f'export?gid={worksheed_gid}&format=csv')

  return pd.read_csv(url, header=None)


def load_worksheet_from_api(spreadsheet_url: str,
                            worksheed_gid: str) -> pd.DataFrame:
  gc = get_gspread_client()

  sheet = gc.open_by_url(spreadsheet_url)
  worksheet = sheet.get_worksheet_by_id(int(worksheed_gid))

  data = worksheet.get_all_values()
  return pd.DataFrame(data)


def trim_dataframe(df: pd.DataFrame, skip_cols: int, skip_rows: int,
                   has_header: bool):
  if len(df) < skip_rows:
    raise ValueError(
        "skip_rows is greater than the number of rows in the dataframe.")
  if len(df.columns) < skip_cols:
    raise ValueError(
        "skip_cols is greater than the number of columns in the dataframe.")
  try:
    df = df.iloc[skip_rows:, skip_cols:]

    if has_header:
      df.columns = df.iloc[0]
      df = df[1:]

  except Exception as e:
    raise ValueError(
        f"Please check your skip_rows, skip_cols, & has_header values: {e}")
  return df


def get_worksheet_gid(spreadsheet_url: str) -> str:
  parsed = urlparse(spreadsheet_url, allow_fragments=True)

  return parse_qs(parsed.fragment)['gid'][0]


def get_worksheet_as_dataframe(spreadsheet_url: str,
                               require_auth: bool = True,
                               has_header: bool = True,
                               skip_rows: int = 0,
                               skip_cols: int = 0) -> pd.DataFrame:

  validate_url(spreadsheet_url)

  worksheed_gid = get_worksheet_gid(spreadsheet_url)

  if not require_auth:
    df = load_worksheet_from_url(spreadsheet_url, worksheed_gid)
  else:
    df = load_worksheet_from_api(spreadsheet_url, worksheed_gid)

  return trim_dataframe(df=df,
                        skip_cols=skip_cols,
                        skip_rows=skip_rows,
                        has_header=has_header)
