from utils.google_sheets import get_worksheet_as_dataframe
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from great_tables import GT
import uvicorn

WORKSHEET_URL = "https://docs.google.com/spreadsheets/d/1xZODLYSYG5g9PMP3VAPeFfNF8Ne1quIJhlTCeNGg-mM/edit?gid=1386834576#gid=1386834576"

TITLE = "TO DO LIST TEST"

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def main():
  df = get_worksheet_as_dataframe(spreadsheet_url=WORKSHEET_URL,
                                  require_auth=True,
                                  skip_rows=0,
                                  skip_cols=0,
                                  has_header=True)
  
  if 'name' in df.columns:
    gt_tbl = GT(df, rowname_col='name').tab_header(title=TITLE)
  else:
    gt_tbl = GT(df).tab_header(title=TITLE)

  return gt_tbl.as_raw_html(make_page=True)


uvicorn.run(app, port=5000, host="0.0.0.0")
