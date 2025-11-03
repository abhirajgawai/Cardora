"""
Gemini AI Service for PDF Statement Extraction

This service uses Google's Gemini AI to:
1. Extract text/data from PDF credit card statements
2. Parse transactions intelligently
3. Categorize transactions automatically
4. Detect recurring payments

Compare to .NET:
    // In .NET, you might use Azure OpenAI or similar:
    public class AiService
    {
        private readonly HttpClient _httpClient;

        public async Task<TransactionList> ExtractTransactionsAsync(byte[] pdfBytes)
        {
            var response = await _httpClient.PostAsync(
                "https://api.openai.com/v1/chat/completions",
                new StringContent(JsonSerializer.Serialize(request))
            );
            return ParseResponse(await response.Content.ReadAsStringAsync());
        }
    }

Python Gemini SDK makes this simpler with built-in PDF support.
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from decimal import Decimal

import google.generativeai as genai
from PyPDF2 import PdfReader

# Import category mapping
from app.features.categories.models import Category
from app.core.config import settings


# ═══════════════════════════════════════════════════════════════════
# GEMINI API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

def configure_gemini():
    """
    Configure Gemini AI with API key from environment

    Compare to .NET:
        var client = new OpenAIClient(new ApiKeyCredential(
            Environment.GetEnvironmentVariable("OPENAI_API_KEY")
        ));
    """
    api_key = settings.GEMINI_API_KEY

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not configured! "
            "Please set it in .env file. "
            "Get API key from: https://makersuite.google.com/app/apikey"
        )

    genai.configure(api_key=api_key)
    print("[INFO] Gemini AI configured successfully")


# ═══════════════════════════════════════════════════════════════════
# PDF TEXT EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file using PyPDF2

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content

    Compare to .NET:
        using PdfSharp;
        var document = PdfReader.Open(pdfPath, PdfDocumentOpenMode.Import);
        var text = string.Join("", document.Pages.Select(p => p.ExtractText()));
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        print(f"[INFO] Extracted {len(text)} characters from PDF")
        return text

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# AI TRANSACTION EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def extract_transactions_with_gemini(
    pdf_text: str,
    categories: List[Category],
    statement_month: int,
    statement_year: int
) -> Tuple[List[Dict], Dict]:
    """
    Use Gemini AI to extract and categorize transactions from PDF text

    Args:
        pdf_text: Extracted text from PDF
        categories: Available categories for classification
        statement_month: Statement month (1-12)
        statement_year: Statement year

    Returns:
        Tuple of (transactions_list, stats_dict)

    Example output:
        transactions = [
            {
                "merchant_name": "Starbucks",
                "amount": 6.50,
                "transaction_date": "2024-10-15",
                "description": "Coffee purchase",
                "category_name": "Dining",
                "is_recurring": False,
                "confidence_score": 0.95
            },
            ...
        ]

        stats = {
            "total_transactions": 45,
            "total_amount": 1523.50,
            "avg_confidence": 0.92,
            "categories_assigned": {"Groceries": 12, "Dining": 15, ...}
        }
    """

    # Configure Gemini
    configure_gemini()

    # Prepare category list for AI
    category_names = [cat.name for cat in categories]
    category_descriptions = "\n".join([
        f"- {cat.name}: {cat.icon}" for cat in categories
    ])

    # Create AI prompt
    prompt = f"""
You are an expert at analyzing credit card statements and extracting transaction data.

I will provide you with text extracted from a credit card PDF statement for {statement_month}/{statement_year}.

Your task:
1. Extract ALL transactions from the statement
2. For each transaction, extract:
   - Merchant/store name
   - Transaction amount (in dollars)
   - Transaction date (format: YYYY-MM-DD)
   - Brief description (if available)
   - Categorize the transaction (use the categories below)
   - Categorize merchant type (for spending insights - see MERCHANT CATEGORIES below)
   - Determine if it's likely a recurring payment (subscription, utility bill, etc.)
   - Provide a confidence score (0.0 to 1.0) for your extraction accuracy

Available categories (choose the MOST appropriate one):
{category_descriptions}

MERCHANT CATEGORIES (for merchant type classification - choose ONE):
- "groceries" - Supermarkets, grocery stores (NTUC, Fairprice, Cold Storage, Sheng Siong, Giant, GrabMart)
- "public_transport" - MRT, buses, trains (SMRT, BUS, TransitLink, EZ-Link)
- "ride_sharing" - Taxis, ride-hailing for RIDES ONLY (GrabCar, GrabBike, Grab rides, Gojek, Uber, Comfort, taxi)
- "coffee_shop" - Coffee chains, cafes (Starbucks, Coffee Bean, Costa)
- "dining_out" - Restaurants, full-service dining
- "fast_food" - Quick service restaurants (McDonald's, KFC, Burger King)
- "food_delivery" - Food delivery services ONLY (GrabFood, Foodpanda, Deliveroo - look for "FOOD" in description)
- "entertainment" - Movies, games, streaming (Cinema, Netflix, Spotify)
- "shopping" - Retail, clothing, electronics (Uniqlo, Lazada, Shopee)
- "utilities" - Bills, phone, internet (Singtel, StarHub, SP Services)
- "healthcare" - Medical, pharmacy, dental (Clinic, hospital, pharmacy)
- "lifestyle" - Gym, beauty, spa
- "fuel" - Petrol, gas stations (Shell, Esso, Caltex)
- "subscription" - Recurring digital services (Netflix, Spotify, gym memberships)
- "unknown" - Cannot determine category

**IMPORTANT - GRAB SUPER-APP DIFFERENTIATION:**
Grab offers multiple services. You MUST differentiate by looking at the transaction description:
- "GRAB*FOOD", "GRABFOOD" → category: "food_delivery", category_name: "Dining"
- "GRAB*CAR", "GRAB*BIKE", "GRAB*RIDE", "GRAB SINGAPORE" (no specific service mentioned) → category: "ride_sharing", category_name: "Transport"
- "GRAB*MART", "GRABMART" → category: "groceries", category_name: "Groceries"
- "GRAB*EXPRESS", "GRAB*DELIVERY" → category: "shopping", category_name: "Shopping"
- "GRABPAY TOP UP", "GRAB*PAY" → category: "unknown", category_name: "Others"

IMPORTANT RULES:
- Extract ONLY posted transactions (NOT pending)
- Amounts should be positive decimals (e.g., 6.50, not -6.50)
- Dates must be in YYYY-MM-DD format
- If merchant name is unclear, make your best guess
- Confidence score should reflect how certain you are about the data
- For recurring payments: Look for monthly subscriptions, utilities, insurance, loan payments, etc.
- category_name: Use from user's category list above
- category: Use from MERCHANT CATEGORIES list (for spending insights)

Return ONLY a JSON array of transactions in this EXACT format:
[
  {{
    "merchant_name": "Starbucks",
    "amount": 6.50,
    "transaction_date": "2024-10-15",
    "description": "Coffee purchase",
    "category_name": "Dining",
    "category": "coffee_shop",
    "is_recurring": false,
    "confidence_score": 0.95
  }},
  ...
]

Do NOT include any explanations, comments, or markdown. ONLY the JSON array.

Statement text:
{pdf_text[:10000]}
"""

    try:
        # Use Gemini Pro Latest (modern replacement for deprecated gemini-pro)
        model = genai.GenerativeModel('gemini-pro-latest')

        print("[INFO] Sending request to Gemini AI...")
        response = model.generate_content(prompt)

        # Parse AI response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        transactions = json.loads(response_text)

        print(f"[SUCCESS] Gemini extracted {len(transactions)} transactions")

        # Calculate statistics
        stats = calculate_extraction_stats(transactions)

        return transactions, stats

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Gemini response as JSON: {e}")
        print(f"[DEBUG] Response text: {response_text[:500]}")
        raise Exception("AI response was not valid JSON. Please try again.")

    except Exception as e:
        print(f"[ERROR] Gemini AI extraction failed: {e}")
        raise Exception(f"AI extraction failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# STATISTICS CALCULATION
# ═══════════════════════════════════════════════════════════════════

def calculate_extraction_stats(transactions: List[Dict]) -> Dict:
    """
    Calculate statistics from extracted transactions

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Statistics dictionary
    """
    if not transactions:
        return {
            "total_transactions": 0,
            "total_amount": 0.0,
            "avg_confidence": 0.0,
            "categories_assigned": {}
        }

    total_amount = sum(Decimal(str(t["amount"])) for t in transactions)
    total_confidence = sum(t.get("confidence_score", 0.0) for t in transactions)
    avg_confidence = total_confidence / len(transactions) if transactions else 0.0

    # Count categories
    categories_assigned = {}
    for t in transactions:
        cat_name = t.get("category_name", "Unknown")
        categories_assigned[cat_name] = categories_assigned.get(cat_name, 0) + 1

    return {
        "total_transactions": len(transactions),
        "total_amount": float(total_amount),
        "avg_confidence": round(avg_confidence, 2),
        "categories_assigned": categories_assigned
    }


# ═══════════════════════════════════════════════════════════════════
# CARD METADATA EXTRACTION (NEW!)
# ═══════════════════════════════════════════════════════════════════

def extract_card_metadata_from_pdf(pdf_text: str) -> Dict:
    """
    Extract credit card metadata from PDF statement using Gemini AI

    This function automatically extracts:
    - Bank name (e.g., "CITI", "Standard Chartered")
    - Card type/name (e.g., "PREMIERMILES WORLD MASTER")
    - Last 4 digits (e.g., "0368")
    - Cardholder name (e.g., "ABHIRAJ GAUTAM GAVAI")
    - Statement date (e.g., "2025-04-15")
    - Payment due date (e.g., "2025-05-10")
    - Credit limit (optional)
    - Current balance (optional)

    Args:
        pdf_text: Extracted text from PDF statement

    Returns:
        Dictionary with card metadata

    Example:
        {
            "bank_name": "CITI",
            "card_type": "PREMIERMILES WORLD MASTER",
            "last_four_digits": "0368",
            "cardholder_name": "ABHIRAJ GAUTAM GAVAI",
            "statement_date": "2025-04-15",
            "due_date": "2025-05-10",
            "credit_limit": 15000.00,
            "current_balance": 2345.67
        }
    """

    # Configure Gemini
    configure_gemini()

    # Create AI prompt for metadata extraction
    prompt = f"""
You are an expert at analyzing credit card statements and extracting metadata.

I will provide you with text extracted from a credit card PDF statement.

Your task: Extract the following information from the statement:

**CARD INFORMATION:**
1. **Bank Name**: The issuing bank (e.g., "CITI", "DBS", "Standard Chartered")
2. **Card Type/Name**: The card product name (e.g., "PREMIERMILES WORLD MASTER", "Cashback Visa")
3. **Last 4 Digits**: Last 4 digits of the card number (e.g., "0368")
4. **Cardholder Name**: Name on the card (e.g., "ABHIRAJ GAUTAM GAVAI")
5. **Statement Date**: The statement closing date in YYYY-MM-DD format
6. **Due Date**: Payment due date in YYYY-MM-DD format
7. **Credit Limit**: Total credit limit (if available, otherwise null)

**BALANCE & PAYMENT INFORMATION (CRITICAL FOR DEBT DETECTION):**
8. **Statement Balance**: Total amount owed on this statement (also called "New Balance", "Amount Due", "Total Amount Due")
9. **Minimum Payment Due**: Minimum payment required to avoid late fees
10. **Previous Balance**: Balance carried over from previous statement (also called "Previous Outstanding Balance", "Last Month's Balance")
11. **New Charges**: New purchases/charges this billing cycle (sum of all new transactions)
12. **Payments/Credits**: Payments and credits received this cycle (negative value or separate field, may say "Payments Received", "Credits")
13. **Interest Charged**: Interest charged this cycle (may be 0.00 if paid in full, also called "Finance Charges", "Interest/Finance Charges")
14. **Fees Charged**: Late fees, annual fees, over-limit fees, etc. (may be 0.00)
15. **APR**: Annual Percentage Rate for purchases (e.g., 24.99 for 24.99%)

IMPORTANT RULES:
- Extract ALL balance information - this is critical for detecting if user paid their bill
- Be precise with dates - use YYYY-MM-DD format
- If a field is not found, set it to null
- For amounts, use decimal format (e.g., 15000.00)
- For negative amounts (payments), use negative values (e.g., -500.00)
- Bank name should be clean (e.g., "CITI" not "Citibank N.A.")
- Look for "Summary of Account" or "Account Summary" section for balances
- Statement Balance = Previous Balance + New Charges - Payments + Interest + Fees

Return ONLY a JSON object in this EXACT format:
{{
  "bank_name": "CITI",
  "card_type": "PREMIERMILES WORLD MASTER",
  "last_four_digits": "0368",
  "cardholder_name": "ABHIRAJ GAUTAM GAVAI",
  "statement_date": "2025-04-15",
  "due_date": "2025-05-10",
  "credit_limit": 15000.00,
  "statement_balance": 2345.67,
  "minimum_payment_due": 50.00,
  "previous_balance": 1800.00,
  "new_charges": 800.00,
  "payments_credits": -300.00,
  "interest_charged": 24.00,
  "fees_charged": 0.00,
  "apr": 24.99
}}

Do NOT include any explanations, comments, or markdown. ONLY the JSON object.

Statement text (first 8000 characters to capture summary section):
{pdf_text[:8000]}
"""

    try:
        # Use Gemini Pro Latest (modern replacement for deprecated gemini-pro)
        model = genai.GenerativeModel('gemini-pro-latest')

        print("[INFO] Extracting card metadata with Gemini AI...")
        response = model.generate_content(prompt)

        # Parse AI response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        metadata = json.loads(response_text)

        print(f"[SUCCESS] Extracted card metadata:")
        print(f"  - Bank: {metadata.get('bank_name')}")
        print(f"  - Card: {metadata.get('card_type')}")
        print(f"  - Last 4: {metadata.get('last_four_digits')}")
        print(f"  - Statement Date: {metadata.get('statement_date')}")

        return metadata

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse card metadata: {e}")
        print(f"[DEBUG] Response: {response_text[:500]}")
        raise Exception("Failed to extract card metadata from PDF")

    except Exception as e:
        print(f"[ERROR] Card metadata extraction failed: {e}")
        raise Exception(f"Card metadata extraction failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# MAIN EXTRACTION FUNCTION
# ═══════════════════════════════════════════════════════════════════

def process_statement_pdf(
    pdf_path: str,
    categories: List[Category],
    statement_month: int,
    statement_year: int
) -> Tuple[List[Dict], Dict]:
    """
    Main function to process PDF statement and extract transactions

    Args:
        pdf_path: Path to PDF file
        categories: Available categories
        statement_month: Statement month (1-12)
        statement_year: Statement year

    Returns:
        Tuple of (transactions_list, stats_dict)

    Usage:
        from app.core.gemini_service import process_statement_pdf
        from app.features.categories.models import Category

        # Get categories from DB
        categories = db.query(Category).filter(Category.user_id == None).all()

        # Process PDF
        transactions, stats = process_statement_pdf(
            pdf_path="uploads/statement.pdf",
            categories=categories,
            statement_month=10,
            statement_year=2024
        )

        print(f"Extracted {stats['total_transactions']} transactions")
        print(f"Total amount: ${stats['total_amount']}")
        print(f"Average confidence: {stats['avg_confidence']}")
    """
    print("=" * 70)
    print("PROCESSING PDF STATEMENT WITH GEMINI AI")
    print("=" * 70)

    # Step 1: Extract text from PDF
    print(f"\n[1/3] Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(pdf_path)

    # Step 2: Use Gemini AI to extract transactions
    print(f"\n[2/3] Analyzing with Gemini AI...")
    transactions, stats = extract_transactions_with_gemini(
        pdf_text, categories, statement_month, statement_year
    )

    # Step 3: Validate and return
    print(f"\n[3/3] Validation complete!")
    print(f"\nExtracted {stats['total_transactions']} transactions")
    print(f"Total amount: ${stats['total_amount']:.2f}")
    print(f"Average confidence: {stats['avg_confidence']}")
    print("\nCategories breakdown:")
    for cat, count in stats['categories_assigned'].items():
        print(f"  - {cat}: {count} transactions")

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE!")
    print("=" * 70)

    return transactions, stats


# ═══════════════════════════════════════════════════════════════════
# CATEGORY MATCHING HELPER
# ═══════════════════════════════════════════════════════════════════

def match_category_by_name(
    category_name: str,
    available_categories: List[Category]
) -> Optional[Category]:
    """
    Match AI-suggested category name to actual Category object

    Args:
        category_name: Category name from AI (e.g., "Dining")
        available_categories: List of Category objects from DB

    Returns:
        Matching Category object or None

    This is a fuzzy matcher that handles:
    - Case-insensitive matching
    - Plural forms ("Grocery" vs "Groceries")
    - Common aliases ("Food" -> "Groceries", "Restaurant" -> "Dining")
    """
    category_name_lower = category_name.lower().strip()

    # Exact match (case-insensitive)
    for cat in available_categories:
        if cat.name.lower() == category_name_lower:
            return cat

    # Fuzzy match with common aliases
    aliases = {
        "food": "groceries",
        "grocery": "groceries",
        "supermarket": "groceries",
        "restaurant": "dining",
        "food & beverage": "dining",
        "f&b": "dining",
        "transportation": "transport",
        "travel": "transport",
        "gas": "transport",
        "fuel": "transport",
        "shop": "shopping",
        "retail": "shopping",
        "entertainment": "entertainment",
        "movies": "entertainment",
        "cinema": "entertainment",
        "bills": "bills & utilities",
        "utilities": "bills & utilities",
        "electricity": "bills & utilities",
        "water": "bills & utilities",
        "internet": "bills & utilities",
        "medical": "healthcare",
        "health": "healthcare",
        "doctor": "healthcare",
        "hospital": "healthcare",
        "pharmacy": "healthcare"
    }

    # Try alias matching
    matched_name = aliases.get(category_name_lower)
    if matched_name:
        for cat in available_categories:
            if cat.name.lower() == matched_name:
                return cat

    # Return "Others" as fallback
    for cat in available_categories:
        if cat.name.lower() == "others" or cat.name.lower() == "other":
            return cat

    return None


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Process a PDF statement
from app.core.gemini_service import process_statement_pdf
from app.core.database import SessionLocal
from app.features.categories.models import Category

db = SessionLocal()

# Get system categories
categories = db.query(Category).filter(Category.user_id == None).all()

# Process PDF
transactions, stats = process_statement_pdf(
    pdf_path="uploads/DBS_Visa_Oct2024.pdf",
    categories=categories,
    statement_month=10,
    statement_year=2024
)

# Save transactions to database
for trans_data in transactions:
    # Match category
    category = match_category_by_name(trans_data["category_name"], categories)

    transaction = Transaction(
        user_id=current_user.id,
        card_id=card_id,
        statement_id=statement_id,
        category_id=category.id if category else None,
        merchant_name=trans_data["merchant_name"],
        amount=Decimal(str(trans_data["amount"])),
        transaction_date=datetime.strptime(trans_data["transaction_date"], "%Y-%m-%d").date(),
        description=trans_data.get("description"),
        statement_month=statement_month,
        statement_year=statement_year,
        is_recurring=trans_data.get("is_recurring", False),
        confidence_score=Decimal(str(trans_data.get("confidence_score", 0.0)))
    )
    db.add(transaction)

db.commit()
print(f"Saved {len(transactions)} transactions to database!")
"""

