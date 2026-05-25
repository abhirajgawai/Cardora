"""
Merchant Categories Configuration

Defines merchant categories and patterns for context-aware insights.
This helps distinguish essential spending from discretionary and provide relevant advice.
"""

from typing import Dict, List, Set
from enum import Enum


class MerchantCategory(str, Enum):
    """Merchant spending categories"""
    GROCERIES = "groceries"
    PUBLIC_TRANSPORT = "public_transport"
    RIDE_SHARING = "ride_sharing"
    FUEL = "fuel"
    DINING_OUT = "dining_out"
    FAST_FOOD = "fast_food"
    COFFEE_SHOP = "coffee_shop"
    FOOD_DELIVERY = "food_delivery"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    UNKNOWN = "unknown"


class SpendingType(str, Enum):
    """Type of spending for insight generation"""
    ESSENTIAL = "essential"
    SMART = "smart"
    SEMI_DISCRETIONARY = "semi_discretionary"
    DISCRETIONARY = "discretionary"


MERCHANT_PATTERNS: Dict[MerchantCategory, List[str]] = {
    MerchantCategory.GROCERIES: [
        "ntuc", "fairprice", "ntuc fairprice", "cold storage", "sheng siong", "giant", "prime",
        "market", "supermarket", "grocery", "mart", "minimart", "cheers",
        "7-eleven", "7 eleven"
    ],

    MerchantCategory.PUBLIC_TRANSPORT: [
        "smrt", "mrt", "lta", "bus", "ezlink", "transitlink", "sbs", "busmrt",
    ],

    MerchantCategory.RIDE_SHARING: [
        "grab", "gojek", "tada", "ryde", "comfort", "citi cab", "premier taxi"
    ],

    MerchantCategory.FUEL: [
        "shell", "esso", "caltex", "spc", "petrol", "fuel", "gas station"
    ],

    MerchantCategory.DINING_OUT: [
        "restaurant", "cafe", "bistro", "grill", "steakhouse", "sushi",
        "ramen", "hotpot", "buffet", "seafood", "pizzeria", "diner",
        "izakaya", "kopitiam", "hawker", "food court"
    ],

    MerchantCategory.FAST_FOOD: [
        "mcdonald", "kfc", "burger king", "subway", "pizza hut", "domino",
        "texas chicken", "jollibee", "popeyes", "wendy", "mos burger"
    ],

    MerchantCategory.COFFEE_SHOP: [
        "starbucks", "coffee bean", "costa coffee", "dunkin", "tim horton",
        "toast box", "ya kun", "killiney", "coffee", "cafe"
    ],

    MerchantCategory.FOOD_DELIVERY: [
        "grab food", "grabfood", "foodpanda", "deliveroo", "food delivery"
    ],

    MerchantCategory.ENTERTAINMENT: [
        "cinema", "cathay", "gv", "shaw", "golden village", "theater",
        "steam", "playstation", "nintendo", "xbox", "spotify", "netflix",
        "disney", "hbo", "gaming", "karaoke", "ktv"
    ],

    MerchantCategory.SHOPPING: [
        "uniqlo", "h&m", "zara", "cotton on", "nike", "adidas",
        "challenger", "courts", "best denki", "harvey norman",
        "lazada", "shopee", "amazon", "qoo10", "taobao"
    ],

    MerchantCategory.UTILITIES: [
        "sp services", "utility", "electricity", "water", "gas bill",
        "singtel", "starhub", "m1", "circles", "gomo", "phone bill", "telco"
    ],

    MerchantCategory.HEALTHCARE: [
        "clinic", "hospital", "pharmacy", "guardian", "watsons", "unity",
        "dentist", "dental", "medical", "health", "doctor"
    ],

    MerchantCategory.LIFESTYLE: [
        "gym", "fitness", "yoga", "spa", "salon", "barber", "hair",
        "nail", "massage", "wellness"
    ],
}


CATEGORY_SPENDING_TYPE: Dict[MerchantCategory, SpendingType] = {
    MerchantCategory.GROCERIES: SpendingType.ESSENTIAL,
    MerchantCategory.UTILITIES: SpendingType.ESSENTIAL,
    MerchantCategory.HEALTHCARE: SpendingType.ESSENTIAL,
    MerchantCategory.EDUCATION: SpendingType.ESSENTIAL,

    MerchantCategory.PUBLIC_TRANSPORT: SpendingType.SMART,

    MerchantCategory.RIDE_SHARING: SpendingType.DISCRETIONARY,
    MerchantCategory.COFFEE_SHOP: SpendingType.DISCRETIONARY,
    MerchantCategory.FOOD_DELIVERY: SpendingType.DISCRETIONARY,
    MerchantCategory.ENTERTAINMENT: SpendingType.DISCRETIONARY,
    MerchantCategory.SHOPPING: SpendingType.DISCRETIONARY,
    MerchantCategory.LIFESTYLE: SpendingType.DISCRETIONARY,

    MerchantCategory.DINING_OUT: SpendingType.SEMI_DISCRETIONARY,
    MerchantCategory.FAST_FOOD: SpendingType.SEMI_DISCRETIONARY,
    MerchantCategory.FUEL: SpendingType.SEMI_DISCRETIONARY,
}


MERCHANT_ALIASES: Dict[str, str] = {
    "ntuc fairprice": "ntuc fairprice",
    "ntuc fp": "ntuc fairprice",
    "fairprice": "ntuc fairprice",
    "fair price": "ntuc fairprice",
    "ntuc": "ntuc fairprice",

    "grab": "grab",
    "grab rides": "grab",
    "grab ride": "grab",
    "grab transport": "grab",
    "grab car": "grab",

    "smrt": "public transport",
    "mrt": "public transport",
    "bus": "public transport",
    "busmrt": "public transport",
    "sbs transit": "public transport",
    "transitlink": "public transport",
    "ezlink": "public transport",

    "starbucks": "starbucks",
    "coffee bean": "coffee bean",
    "costa coffee": "costa coffee",

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

    name = merchant_name.lower()


    name = re.sub(r'\b(inc|llc|corp|company|ltd|limited|pte|singapore)\b', '', name)
    name = name.strip()

    if name in MERCHANT_ALIASES:
        return MERCHANT_ALIASES[name]

    words = name.split()
    if len(words) == 0:
        return "unknown"

    if len(words) == 1:
        return words[0]

    stop_words = {"the", "and", "or", "at", "of"}
    meaningful_words = [w for w in words if w not in stop_words]

    if len(meaningful_words) >= 2:
        normalized = ' '.join(meaningful_words[:2])
    else:
        normalized = meaningful_words[0] if meaningful_words else words[0]

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

    if spending_type == SpendingType.ESSENTIAL:
        return False

    if spending_type == SpendingType.SMART:
        return False

    return True
