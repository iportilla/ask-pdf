# Ask Your Excel File — User Guide

This app accepts **Excel spreadsheets (`.xlsx`)** in addition to PDFs. You upload a spreadsheet, ask a question in plain English, and the app answers using only the data in that file (see [app.py](../app.py) — every sheet is read, converted to CSV-style text, chunked, embedded, and searched the same way PDF text is).

## Supported file types

- ✅ `.xlsx` (Excel Workbook — what Excel saves by default)
- ❌ `.xls` (legacy binary Excel format — not supported)
- ❌ `.xlsm` (macro-enabled workbook — not supported)
- ❌ `.csv` (not supported directly; save/export as `.xlsx` first)

If your upload is rejected, check the file extension is exactly `.xlsx`.

## How to use it

1. Start the app (`streamlit run app.py`, or `make run` — see the main [README.md](../README.md)).
2. In the sidebar, pick an **LLM Provider** — OpenAI (cloud), Azure OpenAI / AI Foundry, or Ollama (local) — and fill in any settings not already defaulted from `.env` (see [README.md#llm-providers](../README.md#llm-providers)).
3. Click **"Upload your PDF or Excel file"** and select your `.xlsx`.
4. Wait for the file to process — all sheets in the workbook are read and indexed. Larger workbooks take longer and use bigger chunks with more overlap so numbers near a chunk boundary aren't lost (see the "Known limitations" section below).
5. Type a question about the data in the **"Ask a question about your file"** box.
6. The answer is generated only from the content of the sheet(s) you uploaded.

## Tips for better answers

- **Be specific about column names** — the app has no schema awareness beyond the raw text of each row, so referencing the exact column (e.g. "Amount Billed To Us" rather than "the cost") gets more reliable answers.
- **Ask about one thing at a time.** Questions that require scanning/aggregating *every* row (totals, counts, "which row has the max value") are the hardest for this app — it retrieves only the handful of chunks most similar to your question, so it may miss rows outside those chunks on very large sheets. Prefer questions scoped to a property, date, or invoice number when possible.
- **Multi-sheet workbooks** are supported — each sheet is labeled `Sheet: <name>` in the extracted text, so you can ask "in the Table1 sheet, ..." if a workbook has more than one sheet.

## Sample data (`data/` directory)

Two example FedEx billing workbooks are included locally for testing (not tracked in git):

| File | Rows × Columns | What it contains |
|---|---|---|
| `data/Fedex Invoice Amounts 7-10-2026 - 7-17-2026.xlsx` | 815 × 27 | Per-shipment FedEx charges for the week of 7/10–7/17/2026 |
| `data/Copy of July 24th FedEx Charge Report.xlsx` | 510 × 26 | Per-shipment FedEx charges report dated July 24th |

Both share the same `Table1` schema: `Record Type`, `Invoice #`, `Item/Ref #`, `Chargerback Property ID`, `Property Name`, `Transaction Date`, `Ship Method`, `Partner/FedEx Box Type`, `Amount Guest Paid`, `Amount Billed To Us`, `Pickup Fee Portion`, `Amount Originally Quoted`, `Best Case Courtesy Rate`, `Rebate To Hotel`, `Rebate Account Charge`, `Credit Card Fee At 3.5%`, `Difference`, `Quote/Invoice Difference`, `Best Case/Invoice Difference`, `Partner Dim`, `Partner Weight`, `FedEx Dim`, `FedEx Actual Weight`, `FedEx Dim Weight`, `FedEx Charge Info`.

> **Note:** you may also see files starting with `~$` in `data/` (e.g. `~$Copy of July 24th FedEx Charge Report.xlsx`). These are Excel's temporary lock files, created automatically while the real workbook is open in Excel — don't upload them, they contain no usable data. `data/` is gitignored because these workbooks contain real property names and dollar amounts.

## Example questions to try

> **Note:** each question is answered against **one uploaded file at a time** — the app doesn't compare two separately-uploaded workbooks in a single session. Upload the relevant file below before asking its questions.

### `Fedex Invoice Amounts 7-10-2026 - 7-17-2026.xlsx` (815 rows)

1. "What ship methods appear in this report, and how many shipments used each one?" *(mostly "Shipstation Integration", plus one "Ground" and one "International Economy")*
2. "How many rows have Record Type 'Other Fee' instead of 'Shipment'?" *(1)*
3. "Which property has the most shipments in this report, and how many?" *(Carnival Cruise Line)*
4. "List the shipments for Cedar Point."
5. "What is the Amount Billed To Us for the shipment with Invoice # 938415408?"
6. "What is the highest Amount Billed To Us in this file, and which property does it belong to?"
7. "What is the earliest and latest Transaction Date in this report?"
8. "How many shipments used FedEx Small Box packaging versus Customer Packaging?"

### `Copy of July 24th FedEx Charge Report.xlsx` (510 rows)

1. "Is there a 'Return to Sender' shipment in this report? What are its details?"
2. "What does the Ship Method value '** RTS ***Shipstation Integration' mean, and which row has it?"
3. "Which property had the highest Amount Billed To Us, and what was the amount?" *(hint: it isn't one of the top-shipment-count properties)*
4. "How many shipments went to Wynn Las Vegas?"
5. "Which property had the second-most shipments after Charlotte Douglas International Airport?"
6. "What is the date range of transactions in this report?"
7. "How many shipments used FedEx Envelope packaging?"
8. "What Record Types appear in this file, and how many rows have each one?" *(Shipment, Other Fee, Return to Sender)*

## Known limitations

- **No exact totals/aggregations.** The app can't reliably compute a true sum, average, or "top N" across an entire large sheet — it retrieves a similarity-matched subset of rows, not the whole dataset. For a 500+ row report, ask about a specific property/invoice/date rather than "what's the grand total."
- **Every question re-processes the whole file** (no caching between questions in this build), so answers on large workbooks take longer and, for cloud providers, repeat API costs.
- **Nothing is persisted.** The uploaded file and its vector index only exist in memory for the current session.
