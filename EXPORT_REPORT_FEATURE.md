# Site Report Export Feature

## Overview

The export feature now generates professional Word documents (.docx) or PDF files instead of CSV spreadsheets. The report includes demographics and top 10 schools for a searched address.

## What's Included

### 1. Demographics Section
- **Address** - The searched address
- **Zip Code** - Zip code of the address
- **Population** - Total population for the zip code
- **Average Household Income (AHHI)** - Average household income
- **Median Age** - Median age of residents

### 2. Great School Scores (Top 10 Schools)
- **School Name** - Name of the school
- **Address** - School address
- **Type** - Elementary, Middle, or High
- **Rating** - School rating (1-10 scale)
- **Proximity** - Distance from the searched address in miles

## How to Use

1. **Search for an address:**
   - Enter an address in the "Search Address" field
   - Click "Go"
   - OR enter a zip code in "Search Zip Code" field and click "Go"

2. **Download the report:**
   - Click the "Download Report (Word/PDF)" button
   - Choose format:
     - **OK** = Word document (.docx)
     - **Cancel** = PDF document

3. **The report will download automatically** with a filename like:
   - `site_report_28204_20260126_161530.docx` (Word)
   - `site_report_28204_20260126_161530.pdf` (PDF)

## Requirements

The following Python packages are required (already added to `requirements.txt`):
- `python-docx` - For Word document generation
- `reportlab` - For PDF generation

Install with:
```bash
pip install python-docx reportlab
```

## Technical Details

### Data Sources
- **Demographics:** From `census_data` table in database
- **Schools:** Top 10 schools by proximity from `school_data` table
- **Search Radius:** 10 miles from the address location

### School Selection
The system finds the top 10 schools (all types combined) sorted by distance from the address:
- Searches within 10 miles radius
- Includes Elementary, Middle, and High schools
- Sorted by proximity (closest first)
- Shows rating if available

### Format Options
- **Word (.docx):** Professional formatted document with tables
- **PDF:** Formatted PDF with styled tables and sections

## Notes

- The report uses the address/location from your last search
- If you search by zip code only, it uses the zip code as the address
- Schools are sorted by distance, not by rating
- If no schools are found within 10 miles, the report will show "No school data available"

## Example Report Structure

```
Site Selection Report

1. Demographics
┌─────────────────────────────┬──────────────────────┐
│ Field                       │ Value                │
├─────────────────────────────┼──────────────────────┤
│ Address                     │ 1111 Metropolitan... │
│ Zip Code                    │ 28204               │
│ Population                  │ 15,234               │
│ Average Household Income    │ $65,432              │
│ Median Age                  │ 38.5 years          │
└─────────────────────────────┴──────────────────────┘

2. Great School Scores (Top 10 Schools)
┌──────────────────┬──────────────┬──────────┬────────┬──────────┐
│ School Name      │ Address      │ Type     │ Rating │ Proximity│
├──────────────────┼──────────────┼──────────┼────────┼──────────┤
│ Sedgefield Elem  │ 123 Main St  │Elementary│ 8.5/10 │ 0.5 miles│
│ ...              │ ...          │ ...      │ ...    │ ...      │
└──────────────────┴──────────────┴──────────┴────────┴──────────┘
```
