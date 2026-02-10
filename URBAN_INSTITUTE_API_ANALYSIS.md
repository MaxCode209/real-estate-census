# Urban Institute Education Data Portal API - Analysis

## What It Provides (FREE) ✅

The Urban Institute's Education Data Portal API provides access to **NCES (National Center for Education Statistics)** data, including:

- ✅ School names
- ✅ School addresses
- ✅ School coordinates (latitude/longitude)
- ✅ School levels (elementary, middle, high)
- ✅ Enrollment numbers
- ✅ School type (public, private, charter)
- ✅ District information
- ✅ Other administrative data

**Endpoint Example:**
```
https://educationdata.urban.org/api/v1/schools/ccd/directory/2022/
```

## What It Does NOT Provide ❌

- ❌ **Numerical GreatSchools ratings (1-10)**
- ❌ Any school quality ratings
- ❌ Test scores (though NCES has separate datasets for this)
- ❌ Parent/student reviews

## Why This Doesn't Save Money

### The Problem
Even though we could get a **free list of all schools** in NC and SC from the Urban Institute API, we still need to **get the ratings** from somewhere.

### The Reality
1. **Apify charges per school result**, not per query
   - If we query Apify for 4,000 schools, we pay $0.02 × 4,000 = $80
   - Getting a free list first doesn't change this cost

2. **GreatSchools API doesn't offer 1-10 ratings**
   - Their standard API only provides "rating bands" (below average/average/above average)
   - 1-10 numerical ratings require their Enterprise Data Licensing (not publicly available)

3. **No free source for 1-10 ratings**
   - NCES data: No ratings
   - State education departments: Usually letter grades or test scores, not 1-10 ratings
   - Urban Institute: Mirrors NCES, so also no ratings

## Could We Use It for Something Else?

### Potential Use Case: School Directory
If you wanted to:
- Build a comprehensive school directory
- Get all school locations for mapping
- Cross-reference with other data sources

Then the Urban Institute API would be **perfect and free**!

### But For Ratings...
We still need to pay Apify to scrape Zillow for the 1-10 ratings, regardless of where we get the school list.

## Cost Breakdown

| Step | Data Source | Cost |
|------|-------------|------|
| Get school list | Urban Institute API | **$0** ✅ |
| Get school ratings | Apify Zillow Scraper | **$80** |
| **Total** | | **$80** |

**Same cost as using Apify directly!**

## Conclusion

The Urban Institute API is **excellent for free school directory data**, but it doesn't help us avoid the $80 cost for ratings because:

1. ✅ We can get school lists for free
2. ❌ We still need to pay Apify for ratings
3. ❌ No free alternative exists for 1-10 numerical ratings

**Recommendation:** Stick with the Apify bulk import plan. The $80 one-time cost is the most cost-effective way to get numerical 1-10 ratings for all NC and SC schools.
