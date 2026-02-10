# NC & SC School Data Import - Cost Estimate

## Overview

Importing **ALL schools** in North Carolina and South Carolina using Apify Zillow School Scraper.

## Coverage

- **North Carolina**: 7 regions covering entire state
- **South Carolina**: 4 regions covering entire state
- **Total Regions**: 11

## Cost Estimate

### Apify Pricing
- **$20 per 1,000 results** = **$0.02 per school**

### School Count Estimates
- **North Carolina**: ~2,600 public schools
- **South Carolina**: ~1,200 public schools  
- **Plus charter schools**: ~300 total
- **Total**: ~4,000 schools

### Cost Breakdown

| Estimate | Schools | Cost |
|----------|---------|------|
| **Low** | 3,500 | **$70.00** |
| **Middle** | 4,000 | **$80.00** |
| **High** | 4,500 | **$90.00** |

**Recommended Budget: $80-90**

## Time Estimate

- **Per Region**: 30-60 seconds (Apify scraping)
- **11 Regions**: ~10-15 minutes total
- **Plus processing**: ~20-30 minutes total

## What You Get

✅ **All public schools** in NC and SC  
✅ **All charter schools** in NC and SC  
✅ **1-10 numerical ratings** for each school  
✅ **School names and addresses**  
✅ **Instant lookups** after import (no more 30-60 second waits!)  

## Running the Import

```bash
python scripts/bulk_import_schools.py
```

The script will:
1. Show cost estimate
2. Ask for confirmation
3. Import all 11 regions
4. Show progress and running cost
5. Complete in ~20-30 minutes

## After Import

Once complete, searching for any address in NC or SC will return school scores **instantly** - no API calls needed!
