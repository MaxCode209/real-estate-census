# School Data Cost Comparison - NC & SC

## The Challenge
We need **numerical 1-10 ratings** for all schools in NC and SC. Basic school info (name, address) is free, but ratings are the expensive part.

## Option Comparison

### Option 1: Apify Zillow Scraper (Current Plan)
**Cost**: $70-90 one-time
- ✅ One-time cost (no subscription)
- ✅ Includes all data (names, addresses, ratings)
- ✅ ~4,000 schools = $80
- ❌ Most expensive option

### Option 2: GreatSchools API (Subscription)
**Cost**: $52.50/month + $0.003 per school after 15,000
- For 4,000 schools: $52.50 + (0 × $0.003) = **$52.50/month**
- ✅ Cheaper per month than Apify one-time
- ❌ **Subscription required** - you pay monthly forever
- ❌ After 1.5 months, you've paid more than Apify
- ⚠️ Could cancel after 1 month, but need to make all 4,000 API calls in that month

**Total if you cancel after 1 month**: $52.50 (but you'd need to make 4,000 API calls quickly)

### Option 3: SchoolDigger API
**Cost**: $19.90/month + $0.004 per school after 2,000
- For 4,000 schools: $19.90 + (2,000 × $0.004) = **$27.90/month**
- ✅ Cheapest subscription option
- ❌ Still a subscription (pay monthly)
- ❌ After 3 months = $83.70 (more than Apify)
- ⚠️ Need to make 4,000 API calls in 1 month to cancel

**Total if you cancel after 1 month**: $27.90 (but need 4,000 API calls)

### Option 4: Free NCES Data + Manual Rating Lookup
**Cost**: $0 for data, but...
- ✅ NCES has free school lists (names, addresses, locations)
- ❌ **No ratings included** - would need to manually look up 4,000 schools
- ❌ Not practical - would take weeks of manual work

### Option 5: State Education Department Data
**Cost**: Free
- ✅ NC and SC both have free school report cards
- ❌ **May not have 1-10 numerical ratings** (often have letter grades or test scores)
- ❌ Would need to scrape/parse state websites
- ⚠️ Unclear if ratings match what we need

## Recommendation

### Best Option: **Apify ($80 one-time)**
**Why?**
1. **One-time cost** - no recurring subscription
2. **Complete data** - ratings + names + addresses in one go
3. **Predictable** - know exactly what you're paying
4. **After 2-3 months**, it's cheaper than any subscription

### Alternative: **SchoolDigger ($27.90/month)**
**Only if:**
- You can make all 4,000 API calls in 1 month
- You're okay with subscription model
- You cancel immediately after bulk download

**Risk**: If you forget to cancel or need to re-download, costs add up quickly.

## Cost Over Time

| Months | Apify (One-time) | GreatSchools | SchoolDigger |
|--------|------------------|--------------|--------------|
| 1      | $80              | $52.50       | $27.90       |
| 2      | $80              | $105.00      | $55.80       |
| 3      | $80              | $157.50      | $83.70       |
| 6      | $80              | $315.00      | $167.40      |
| 12     | $80              | $630.00      | $334.80      |

**Apify wins after 2-3 months!**

## Hybrid Approach (Most Cost-Effective)

1. **Get free school lists from NCES** (names, addresses, locations) - $0
2. **Use Apify only for ratings** - but Apify charges per result, not per lookup
3. **Result**: Still need to pay Apify for all schools

**Unfortunately, this doesn't save money** because Apify charges per school returned, not per query.

## Final Recommendation

**Stick with Apify ($80 one-time)** because:
- ✅ One-time cost (no subscription trap)
- ✅ Complete solution
- ✅ Cheaper long-term
- ✅ Predictable budget

**$80 is actually quite reasonable** for 4,000 schools with ratings - that's only **$0.02 per school**!
