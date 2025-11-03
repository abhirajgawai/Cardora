"""
Seed Default Categories for Cardora

Inserts 8 system-wide default categories that all users can use.

Compare to .NET:
    // In EF Core, you'd use:
    public class SeedData
    {
        public static void Initialize(AppDbContext context)
        {
            if (context.Categories.Any()) return;  // Already seeded

            var categories = new[]
            {
                new Category { Name = "Groceries", Icon = "🛒", Color = "#4CAF50" },
                // ...
            };

            context.Categories.AddRange(categories);
            context.SaveChanges();
        }
    }

In SQLAlchemy, we manually insert using sessions.
"""

import sys
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.features.categories.models import Category


# Default system categories (user_id = NULL for system-wide)
DEFAULT_CATEGORIES = [
    # ===== EXISTING CATEGORIES (8) =====
    {
        "name": "Groceries",
        "icon": "🛒",
        "color": "#4CAF50",  # Green
        "is_custom": False
    },
    {
        "name": "Dining",
        "icon": "🍽️",
        "color": "#FF9800",  # Orange
        "is_custom": False
    },
    {
        "name": "Transport",
        "icon": "🚗",
        "color": "#2196F3",  # Blue
        "is_custom": False
    },
    {
        "name": "Shopping",
        "icon": "🛍️",
        "color": "#E91E63",  # Pink
        "is_custom": False
    },
    {
        "name": "Entertainment",
        "icon": "🎬",
        "color": "#9C27B0",  # Purple
        "is_custom": False
    },
    {
        "name": "Bills & Utilities",
        "icon": "💡",
        "color": "#607D8B",  # Blue Grey
        "is_custom": False
    },
    {
        "name": "Healthcare",
        "icon": "🏥",
        "color": "#F44336",  # Red
        "is_custom": False
    },
    {
        "name": "Others",
        "icon": "📦",
        "color": "#9E9E9E",  # Grey
        "is_custom": False
    },

    # ===== NEW CATEGORIES (13) =====
    # Daily Essentials
    {
        "name": "Gas & Fuel",
        "icon": "⛽",
        "color": "#FF5722",  # Deep Orange
        "is_custom": False
    },

    # Bills & Services
    {
        "name": "Insurance",
        "icon": "🛡️",
        "color": "#3F51B5",  # Indigo
        "is_custom": False
    },
    {
        "name": "Subscriptions & Services",
        "icon": "📱",
        "color": "#00BCD4",  # Cyan
        "is_custom": False
    },

    # Shopping
    {
        "name": "Online Shopping",
        "icon": "📦",
        "color": "#FF6F00",  # Amber Dark
        "is_custom": False
    },
    {
        "name": "Clothing & Accessories",
        "icon": "👕",
        "color": "#E91E63",  # Pink (similar to Shopping)
        "is_custom": False
    },
    {
        "name": "Electronics",
        "icon": "💻",
        "color": "#607D8B",  # Blue Grey
        "is_custom": False
    },

    # Health & Wellness
    {
        "name": "Fitness & Gym",
        "icon": "💪",
        "color": "#FF9800",  # Orange
        "is_custom": False
    },
    {
        "name": "Beauty & Personal Care",
        "icon": "💇",
        "color": "#E91E63",  # Pink
        "is_custom": False
    },

    # Lifestyle
    {
        "name": "Pets",
        "icon": "🐾",
        "color": "#8BC34A",  # Light Green
        "is_custom": False
    },

    # Travel
    {
        "name": "Flights & Travel Bookings",
        "icon": "✈️",
        "color": "#2196F3",  # Blue
        "is_custom": False
    },
    {
        "name": "Hotels & Accommodation",
        "icon": "🏨",
        "color": "#00BCD4",  # Cyan
        "is_custom": False
    },

    # Other
    {
        "name": "Home & Garden",
        "icon": "🏡",
        "color": "#8BC34A",  # Light Green
        "is_custom": False
    },
    {
        "name": "Education & Learning",
        "icon": "📚",
        "color": "#3F51B5",  # Indigo
        "is_custom": False
    }
]


def seed_categories(db: Session):
    """
    Seed default system categories

    System categories have user_id = NULL, making them available to ALL users.
    """

    print("=" * 70)
    print("SEEDING DEFAULT CATEGORIES")
    print("=" * 70)

    # Check if categories already exist
    existing_count = db.query(Category).filter(
        Category.user_id == None,  # System categories
        Category.is_custom == False
    ).count()

    if existing_count > 0:
        print(f"\nFound {existing_count} existing system categories.")
        print(f"Checking for new categories to add...")
    else:
        print(f"\nNo existing categories found.")

    print(f"\nProcessing {len(DEFAULT_CATEGORIES)} categories...")

    # Insert each category
    inserted_count = 0
    for category_data in DEFAULT_CATEGORIES:
        # Check if category with this name already exists
        existing = db.query(Category).filter(
            Category.name == category_data["name"],
            Category.user_id == None
        ).first()

        if existing:
            print(f"  [SKIP] {category_data['name']} already exists")
            continue

        # Create new category
        category = Category(
            user_id=None,  # NULL = system category
            name=category_data["name"],
            icon=category_data["icon"],
            color=category_data["color"],
            is_custom=category_data["is_custom"]
        )

        db.add(category)
        inserted_count += 1
        print(f"  [OK] Added: {category_data['name']} ({category_data['color']})")

    # Commit all insertions
    db.commit()

    print(f"\nSuccessfully inserted {inserted_count} categories!")
    print("=" * 70)

    # Verify categories
    print("\nVerification - All system categories:")
    categories = db.query(Category).filter(
        Category.user_id == None
    ).order_by(Category.name).all()

    for cat in categories:
        print(f"  {cat.name:<25} {cat.color}")

    print("\n" + "=" * 70)
    print("SEEDING COMPLETE!")
    print("=" * 70)
    print("\nCategories are now available to all users!")
    print("\nUser can also create custom categories:")
    print("  - POST /categories (future endpoint)")
    print("  - Custom categories have user_id = specific user UUID")
    print("  - Custom categories are private to that user")
    print("=" * 70)

    return True


def main():
    """Run seed script"""
    print("\nConnecting to database...")

    db = SessionLocal()

    try:
        success = seed_categories(db)
        return 0 if success else 1

    except Exception as e:
        print(f"\nERROR: Failed to seed categories!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure database tables are created (run create_tables.py)")
        print("2. Check database connection in .env")
        print("3. Verify PostgreSQL is running")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
