"""
Merchant Categories Configuration

Defines merchant categories and patterns for context-aware insights.
This helps distinguish essential spending from discretionary and provide relevant advice.
"""

from typing import Dict, List, Set
from enum import Enum


class MerchantCategory(str, Enum):
    """Merchant spending categories"""
    # Essential spending
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"

    # Transport
    PUBLIC_TRANSPORT = "public_transport"  # MRT, Bus - praise worthy!
    RIDE_SHARING = "ride_sharing"  # Grab, Gojek - opportunity to save
    FUEL = "fuel"

    # Food & Dining
    DINING_OUT = "dining_out"  # Restaurants
    FAST_FOOD = "fast_food"  # McDonald's, KFC
    COFFEE_SHOP = "coffee_shop"  # Starbucks, Coffee Bean
    FOOD_DELIVERY = "food_delivery"  # Grab Food, Foodpanda

    # Discretionary
    ENTERTAINMENT = "entertainment"  # Movies, games
    SHOPPING = "shopping"  # Clothing, electronics
    SUBSCRIPTION = "subscription"  # Netflix, Spotify
    LIFESTYLE = "lifestyle"  # Gym, beauty

    # Unknown
    UNKNOWN = "unknown"


class SpendingType(str, Enum):
    """Type of spending for insight generation"""
    ESSENTIAL = "essential"  # Don't suggest reducing
    SMART = "smart"  # Praise this behavior
    DISCRETIONARY = "discretionary"  # Opportunity to save
    SEMI_DISCRETIONARY = "semi_discretionary"  # Moderate, context-dependent


# Merchant keyword patterns (lowercase)
MERCHANT_PATTERNS: Dict[MerchantCategory, List[str]] = {
    # Groceries
    MerchantCategory.GROCERIES: [
        "ntuc", "fairprice", "ntuc fairprice", "cold storage", "sheng siong", "giant", "prime",
        "market", "supermarket", "grocery", "mart", "minimart", "cheers",
        "7-eleven", "7 eleven"
    ],

    # Public Transport (PRAISE!)
    MerchantCategory.PUBLIC_TRANSPORT: [
        "smrt", "mrt", "lta", "bus", "ezlink", "transitlink", "sbs", "busmrt",
        "public transport"  # Normalized alias target
    ],

    # Ride Sharing (opportunity to save)
    MerchantCategory.RIDE_SHARING: [
        "grab", "gojek", "tada", "ryde", "comfort", "citi cab", "premier taxi"
    ],

    # Fuel
    MerchantCategory.FUEL: [
        "shell", "esso", "caltex", "spc", "petrol", "fuel", "gas station"
    ],

    # Dining Out
    MerchantCategory.DINING_OUT: [
        "restaurant", "cafe", "bistro", "grill", "steakhouse", "sushi",
        "ramen", "hotpot", "buffet", "seafood", "pizzeria", "diner",
        "izakaya", "kopitiam", "hawker", "food court"
    ],

    # Fast Food
    MerchantCategory.FAST_FOOD: [
        "mcdonald", "kfc", "burger king", "subway", "pizza hut", "domino",
        "texas chicken", "jollibee", "popeyes", "wendy", "mos burger"
    ],

    # Coffee Shops (high savings potential!)
    MerchantCategory.COFFEE_SHOP: [
        "starbucks", "coffee bean", "costa coffee", "dunkin", "tim horton",
        "toast box", "ya kun", "killiney", "coffee", "cafe"
    ],

    # Food Delivery
    MerchantCategory.FOOD_DELIVERY: [
        "grab food", "grabfood", "foodpanda", "deliveroo", "food delivery"
    ],

    # Entertainment
    MerchantCategory.ENTERTAINMENT: [
        "cinema", "cathay", "gv", "shaw", "golden village", "theater",
        "steam", "playstation", "nintendo", "xbox", "spotify", "netflix",
        "disney", "hbo", "gaming", "karaoke", "ktv"
    ],

    # Shopping
    MerchantCategory.SHOPPING: [
        "uniqlo", "h&m", "zara", "cotton on", "nike", "adidas",
        "challenger", "courts", "best denki", "harvey norman",
        "lazada", "shopee", "amazon", "qoo10", "taobao"
    ],

    # Utilities
    MerchantCategory.UTILITIES: [
        "sp services", "utility", "electricity", "water", "gas bill",
        "singtel", "starhub", "m1", "circles", "gomo", "phone bill", "telco"
    ],

    # Healthcare
    MerchantCategory.HEALTHCARE: [
        "clinic", "hospital", "pharmacy", "guardian", "watsons", "unity",
        "dentist", "dental", "medical", "health", "doctor"
    ],

    # Lifestyle
    MerchantCategory.LIFESTYLE: [
        "gym", "fitness", "yoga", "spa", "salon", "barber", "hair",
        "nail", "massage", "wellness"
    ],
}


# Category to spending type mapping
CATEGORY_SPENDING_TYPE: Dict[MerchantCategory, SpendingType] = {
    # Essential - don't suggest reducing
    MerchantCategory.GROCERIES: SpendingType.ESSENTIAL,
    MerchantCategory.UTILITIES: SpendingType.ESSENTIAL,
    MerchantCategory.HEALTHCARE: SpendingType.ESSENTIAL,
    MerchantCategory.EDUCATION: SpendingType.ESSENTIAL,

    # Smart - praise this!
    MerchantCategory.PUBLIC_TRANSPORT: SpendingType.SMART,

    # Discretionary - opportunity to save
    MerchantCategory.RIDE_SHARING: SpendingType.DISCRETIONARY,
    MerchantCategory.COFFEE_SHOP: SpendingType.DISCRETIONARY,
    MerchantCategory.FOOD_DELIVERY: SpendingType.DISCRETIONARY,
    MerchantCategory.ENTERTAINMENT: SpendingType.DISCRETIONARY,
    MerchantCategory.SHOPPING: SpendingType.DISCRETIONARY,
    MerchantCategory.LIFESTYLE: SpendingType.DISCRETIONARY,

    # Semi-discretionary - context matters
    MerchantCategory.DINING_OUT: SpendingType.SEMI_DISCRETIONARY,
    MerchantCategory.FAST_FOOD: SpendingType.SEMI_DISCRETIONARY,
    MerchantCategory.FUEL: SpendingType.SEMI_DISCRETIONARY,
}


# Merchant name aliases for better normalization
MERCHANT_ALIASES: Dict[str, str] = {
    # NTUC variations
    "ntuc fairprice": "ntuc fairprice",
    "ntuc fp": "ntuc fairprice",
    "fairprice": "ntuc fairprice",
    "fair price": "ntuc fairprice",
    "ntuc": "ntuc fairprice",

    # Grab variations
    "grab": "grab",
    "grab rides": "grab",
    "grab ride": "grab",
    "grab transport": "grab",
    "grab car": "grab",

    # MRT/Bus variations
    "smrt": "public transport",
    "mrt": "public transport",
    "bus": "public transport",
    "busmrt": "public transport",
    "sbs transit": "public transport",
    "transitlink": "public transport",
    "ezlink": "public transport",

    # Coffee shops
    "starbucks": "starbucks",
    "coffee bean": "coffee bean",
    "costa coffee": "costa coffee",

    # Fast food
    "mcdonald": "mcdonald's",
    "mcdonalds": "mcdonald's",
    "kfc": "kfc",
}


def categorize_merchant(merchant_name: str) -> MerchantCategory:
    """
    Categorize a merchant based on name patterns

    Args:
        merchant_name: The merchant name (will be lowercased)

    Returns:
        MerchantCategory enum value
    """
    if not merchant_name:
        return MerchantCategory.UNKNOWN

    name_lower = merchant_name.lower()

    # Check each category's patterns
    for category, patterns in MERCHANT_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_lower:
                return category

    return MerchantCategory.UNKNOWN


def get_spending_type(category: MerchantCategory) -> SpendingType:
    """Get the spending type for a category"""
    return CATEGORY_SPENDING_TYPE.get(category, SpendingType.DISCRETIONARY)


def normalize_merchant_name(merchant_name: str) -> str:
    """
    Normalize merchant name using aliases and common patterns

    This helps group similar merchants together (e.g., "NTUC Fairprice" and "NTUC FP")

    Args:
        merchant_name: Raw merchant name from transaction

    Returns:
        Normalized merchant name
    """
    if not merchant_name:
        return "unknown"

    import re

    # Convert to lowercase
    name = merchant_name.lower()

    # Remove common suffixes and numbers
    name = re.sub(r'\s*#\d+.*', '', name)  # Store #123
    name = re.sub(r'\s*store\s*\d+.*', '', name, flags=re.IGNORECASE)  # Store 01
    name = re.sub(r'\s*\d{4,}.*', '', name)  # Long numbers
    name = re.sub(r'[^a-z0-9\s\-]', '', name)  # Special chars

    # Remove common corporate suffixes
    name = re.sub(r'\b(inc|llc|corp|company|ltd|limited|pte|singapore)\b', '', name)
    name = name.strip()

    # Check aliases first (exact match after normalization)
    if name in MERCHANT_ALIASES:
        return MERCHANT_ALIASES[name]

    # Extract first 1-2 meaningful words
    words = name.split()
    if len(words) == 0:
        return "unknown"

    # For single word, return as is
    if len(words) == 1:
        return words[0]

    # For 2+ words, take first 2 (unless it's very common like "the", "and")
    stop_words = {"the", "and", "or", "at", "of"}
    meaningful_words = [w for w in words if w not in stop_words]

    if len(meaningful_words) >= 2:
        normalized = ' '.join(meaningful_words[:2])
    else:
        normalized = meaningful_words[0] if meaningful_words else words[0]

    # Final alias check on normalized version
    if normalized in MERCHANT_ALIASES:
        return MERCHANT_ALIASES[normalized]

    return normalized


def should_generate_recurring_insight(category: MerchantCategory) -> bool:
    """
    Determine if we should generate recurring habit insights for this category

    Returns False for essential categories (groceries, utilities, healthcare)
    Returns True for discretionary categories
    """
    spending_type = get_spending_type(category)

    # Don't generate recurring insights for essential spending
    # People NEED groceries, utilities, healthcare
    if spending_type == SpendingType.ESSENTIAL:
        return False

    # Don't generate for smart spending (we'll praise them separately)
    if spending_type == SpendingType.SMART:
        return False

    return True
