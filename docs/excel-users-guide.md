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

- **Be specific about column names** — the app has no schema awareness beyond the raw text of each row, so referencing the exact column name (e.g. the actual header text in your sheet) rather than a vague description gets more reliable answers.
- **Ask about one thing at a time.** Questions that require scanning/aggregating *every* row (totals, counts, "which row has the max value") are the hardest for this app — it retrieves only the handful of chunks most similar to your question, so it may miss rows outside those chunks on very large sheets. Prefer questions scoped to a specific record, date, or ID when possible.
- **Multi-sheet workbooks** are supported — each sheet is labeled `Sheet: <name>` in the extracted text, so you can ask "in the `<sheet name>` sheet, ..." if a workbook has more than one sheet.

## Using your own sample data (`data/` directory)

`data/` is gitignored (see `.gitignore`) so any spreadsheets you drop there for local testing — including ones with real business data — never end up in version control. This repo doesn't ship any real spreadsheets; place your own `.xlsx` file(s) there to try the app locally.

A few things worth knowing if you're testing with a real billing/shipment-style export:

- **Excel lock files:** you may see files starting with `~$` next to your workbook (e.g. `~$<your file>.xlsx`) while it's open in Excel. These are temporary lock files with no usable data — don't upload them.
- **Row/column scale matters for performance and answer quality**, not the specific content — a report with hundreds of rows will take longer to embed and is more likely to need scoped (rather than "grand total") questions. See "Known limitations" below.

## Example questions to try

Adapt these to whatever columns and values are actually in your spreadsheet — they're written to work with any per-record billing/shipment-style export (one row per transaction, with an ID, a date, a location/property, and one or more amount columns):

1. "What [category/type] values appear in this report, and how many records have each one?"
2. "Which [property/location/customer] has the most records in this report, and how many?"
3. "List all the records for [a specific property/location/customer name from your file]."
4. "What is [amount column] for the record with [ID column] = [a specific ID from your file]?"
5. "What is the highest [amount column] in this file, and which [property/location] does it belong to?"
6. "What is the earliest and latest date in this report?"
7. "How many records have [some categorical column] = [a specific value]?"
8. "Are there any records with an unusual or negative value in [amount column]? What are the details?"

> **Note:** each question is answered against **one uploaded file at a time** — the app doesn't compare two separately-uploaded workbooks in a single session.

## Known limitations

- **No exact totals/aggregations.** The app can't reliably compute a true sum, average, or "top N" across an entire large sheet — it retrieves a similarity-matched subset of rows, not the whole dataset. For a large report, ask about a specific record/ID/date rather than "what's the grand total."
- **Every question re-processes the whole file** (no caching between questions in this build), so answers on large workbooks take longer and, for cloud providers, repeat API costs. With a local Ollama model, embedding a large workbook (many chunks batched into one request) can take minutes on CPU-only hardware — see the Ollama troubleshooting notes in `README.md` if this times out.
- **Nothing is persisted.** The uploaded file and its vector index only exist in memory for the current session.
