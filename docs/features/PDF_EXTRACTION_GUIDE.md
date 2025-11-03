# PDF Extraction with Merchant Categorization

## 🎯 Goal

Modify your Gemini PDF extraction prompt to include merchant categorization in the SAME API call.

---

## 📋 What You Need to Do

### **Step 1: Find Your Extraction Service**

Your PDF extraction is likely in one of these locations:
- `app/routers/statements.py` (if extraction happens in the router)
- `app/services/pdf_extraction.py` (if you have a dedicated service)
- Look for where you call `genai.GenerativeModel` or `gemini` with PDF

### **Step 2: Update Your Extraction Prompt**

#### **OLD Prompt (Example):**
```python
prompt = """
Extract transactions from this credit card statement PDF.

Return JSON with this exact format:
{
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "merchant_name": "Merchant name as it appears",
      "amount": 123.45,
      "description": "Optional description"
    }
  ]
}

Rules:
- Extract all transactions
- Format dates as YYYY-MM-DD
- Amounts should be positive numbers
"""
```

#### **NEW Prompt (With Categorization):**
```python
prompt = """
Extract transactions from this credit card statement PDF and categorize each merchant.

Return JSON with this exact format:
{
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "merchant_name": "Merchant name as it appears",
      "amount": 123.45,
      "description": "Optional description",
      "category": "category_value"
    }
  ]
}

CATEGORY VALUES (choose ONE for each transaction):
- "groceries" - Supermarkets, grocery stores, food markets
  Examples: NTUC, Fairprice, Cold Storage, Sheng Siong, Giant

- "public_transport" - Buses, trains, MRT, metro
  Examples: SMRT, MRT, LTA, BUS, TransitLink, EZ-Link

- "ride_sharing" - Taxis, ride-hailing services
  Examples: Grab, Gojek, Uber, Comfort taxi

- "coffee_shop" - Coffee chains, cafes
  Examples: Starbucks, Coffee Bean, Costa

- "dining_out" - Restaurants, full-service dining
  Examples: Restaurants, cafes, bistros

- "fast_food" - Quick service restaurants
  Examples: McDonald's, KFC, Burger King

- "food_delivery" - Food delivery services
  Examples: GrabFood, Foodpanda, Deliveroo

- "entertainment" - Movies, games, streaming
  Examples: Cinema, Netflix, Spotify, gaming

- "shopping" - Retail, clothing, electronics
  Examples: Uniqlo, Lazada, Shopee, malls

- "utilities" - Bills, phone, internet
  Examples: SP Services, Singtel, StarHub

- "healthcare" - Medical, pharmacy, dental
  Examples: Clinic, hospital, pharmacy

- "lifestyle" - Gym, beauty, spa
  Examples: Gym, fitness, salon, spa

- "fuel" - Petrol, gas stations
  Examples: Shell, Esso, Caltex

- "subscription" - Recurring services
  Examples: Netflix, Spotify, gym memberships

- "unknown" - Cannot determine category

CATEGORIZATION RULES:
1. Use context from the full statement to categorize accurately
2. Common Singapore merchants:
   - NTUC/Fairprice → "groceries"
   - BUS/MRT → "public_transport"
   - Grab → "ride_sharing"
   - Starbucks → "coffee_shop"
3. If unsure, use "unknown"

EXTRACTION RULES:
- Extract all transactions
- Format dates as YYYY-MM-DD
- Amounts should be positive numbers
- Category is REQUIRED for each transaction
"""
```

---

## 💻 **Code Changes**

### **Example: Where You Create Transactions**

#### **Before:**
```python
# In your statement upload handler
for txn_data in extracted_transactions:
    transaction = Transaction(
        user_id=user_id,
        card_id=card_id,
        statement_id=statement_id,
        merchant_name=txn_data["merchant_name"],
        amount=Decimal(str(txn_data["amount"])),
        transaction_date=datetime.strptime(txn_data["date"], "%Y-%m-%d").date(),
        description=txn_data.get("description"),
        statement_month=month,
        statement_year=year
    )
    db.add(transaction)
```

#### **After:**
```python
# In your statement upload handler
for txn_data in extracted_transactions:
    transaction = Transaction(
        user_id=user_id,
        card_id=card_id,
        statement_id=statement_id,
        merchant_name=txn_data["merchant_name"],
        amount=Decimal(str(txn_data["amount"])),
        transaction_date=datetime.strptime(txn_data["date"], "%Y-%m-%d").date(),
        description=txn_data.get("description"),
        category_auto=txn_data.get("category", "unknown"),  # ← ADD THIS LINE
        statement_month=month,
        statement_year=year
    )
    db.add(transaction)
```

---

## 🧪 **Testing**

### **Test the Changes:**

1. **Upload a Statement:**
   ```bash
   # Use your frontend or API to upload a PDF statement
   ```

2. **Check Database:**
   ```sql
   -- Check if category_auto is populated
   SELECT merchant_name, amount, category_auto
   FROM cardora.transactions
   LIMIT 10;
   ```

3. **Expected Result:**
   ```
   merchant_name          | amount  | category_auto
   -----------------------+---------+------------------
   STARBUCKS ORCHARD      | 5.50    | coffee_shop
   NTUC FAIRPRICE        | 45.00   | groceries
   GRAB RIDES            | 12.00   | ride_sharing
   BUS/MRT SINGAPORE     | 1.50    | public_transport
   ```

4. **Generate Insights:**
   - Go to dashboard
   - Click "Generate Insights"
   - Should see proper categorization:
     - ✅ Grab → Transport savings advice
     - ✅ Starbucks → Coffee reduction advice
     - ❌ NTUC/BusMRT → SKIPPED (essential spending)

---

## 🔍 **Where to Find Your Extraction Code**

### **Method 1: Search for Gemini Calls**
```bash
# Search for where you call Gemini
grep -r "genai" app/
grep -r "GenerativeModel" app/
```

### **Method 2: Find Statement Upload Handler**
```bash
# Find where PDFs are uploaded
grep -r "upload" app/routers/
grep -r "statement" app/routers/
```

### **Method 3: Check Routes**
Look in `app/routers/statements.py` for endpoints like:
- `POST /statements/upload`
- `POST /statements/extract`

---

## 📊 **Benefits of This Approach**

| Metric | Before | After |
|--------|--------|-------|
| **API Calls** | 1 (extraction) + N (categorization) | 1 (extraction + categorization) |
| **Insight Speed** | Slow (categorize during insights) | Instant (pre-categorized) |
| **Cost** | Higher (separate calls) | Lower (bulk in one prompt) |
| **Accuracy** | Good | Better (full context) |

---

## ✅ **Verification Checklist**

- [ ] Found PDF extraction code
- [ ] Updated Gemini prompt to include category field
- [ ] Updated Transaction creation to save `category_auto`
- [ ] Tested with sample statement
- [ ] Verified database has category_auto populated
- [ ] Generated insights successfully
- [ ] Confirmed essential spending (groceries/transport) is skipped

---

## 🆘 **Troubleshooting**

### **Issue: category_auto is always NULL**
- Check if Gemini response includes "category" field
- Verify you're saving `txn_data.get("category")` to `category_auto`

### **Issue: Categories are wrong**
- Review Gemini prompt examples
- Add more specific examples for your region
- Check if merchant names are clear in statement

### **Issue: Insights not using categories**
- Check `app/services/insights/recurring_habit.py`
- Verify it's reading `transaction.category_auto`

---

## 📝 **Next Step**

After updating extraction, you need to update the insights services to USE the pre-categorized data.

See: `INSIGHTS_UPDATE_GUIDE.md` (will create next)
