#!/usr/bin/python

import time
import gdata.spreadsheet.service
from collections import defaultdict
import sys,os
import string



numero_riga = [6,16,26,34]


def worksheet_dict(feed):
  d = defaultdict(str)
  for i, entry in enumerate(feed.entry):
    d[entry.title.text] = entry.id.text.split('/')[-1] 
  return d


def aggiungi_calciatore(id_allenatore, nome_calciatore, numeroruolo, costo,numeridaprendere):
  daprendere = map(int, numeridaprendere.split(","))
  colonna = 2*id_allenatore-1
  riga = numero_riga[numeroruolo] - daprendere[numeroruolo]
  (spr_client, spreadsheet_key, sheetcode) = login()
  batchRequest = gdata.spreadsheet.SpreadsheetsCellsFeed()
  cells = spr_client.GetCellsFeed(spreadsheet_key, sheetcode)
  cella = spr_client.GetCellsFeed(spreadsheet_key, sheetcode,  "R%dC%d" % (riga, colonna))
  cella.cell.inputValue = nome_calciatore.title()
  batchRequest.AddUpdate(cella)
  cellaPrezzo = spr_client.GetCellsFeed(spreadsheet_key, sheetcode, "R%dC%d" % (riga, colonna+1))
  cellaPrezzo.cell.inputValue = str(costo)
  batchRequest.AddUpdate(cellaPrezzo)
  return spr_client.ExecuteBatch(batchRequest, cells.GetBatchLink().href)
 
  

def login():
  email = 'abenassen@gmail.com'
  password = '301988435'
  weight = '180'
  # Find this value in the url with 'key=XXX' and copy XXX below
  spreadsheet_key = "0AmdiVmUeeZxtdFhjT3VkWW5lNHRxdTlMR1QzbWNJS2c"
  spreadsheet_key = "0AmdiVmUeeZxtdFFkMmVUVkNyLWJQTWJHNUFNMnUxb2c"
  spr_client = gdata.spreadsheet.service.SpreadsheetsService()
  spr_client.email = email
  spr_client.password = password
  spr_client.source = 'Example Spreadsheet Writing Application'
  spr_client.ProgrammaticLogin()
  s = spr_client.GetWorksheetsFeed(key=spreadsheet_key)
  #PrintFeed(s)
  wkst_dict = worksheet_dict(s)
  sheetcode = wkst_dict['Rose']
  return (spr_client, spreadsheet_key, sheetcode)


