"""
Seed Default Categories for Cardora

Inserts 8 system-wide default categories that all users can use.

    // In EF Core, you'd use:
    public class SeedData
    {
        public static void Initialize(AppDbContext context)
        {
            if (context.Categories.Any()) return;  // Already seeded

            var categories = new[]
            {
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


DEFAULT_CATEGORIES = [
    {
        "name": "Groceries",
        "icon": "🛒",
        "is_custom": False
    },
    {
        "name": "Dining",
        "icon": "🍽️",
        "is_custom": False
    },
    {
        "name": "Transport",
        "icon": "🚗",
        "is_custom": False
    },
    {
        "name": "Shopping",
        "icon": "🛍️",
        "is_custom": False
    },
    {
        "name": "Entertainment",
        "icon": "🎬",
        "is_custom": False
    },
    {
        "name": "Bills & Utilities",
        "icon": "💡",
        "is_custom": False
    },
    {
        "name": "Healthcare",
        "icon": "🏥",
        "is_custom": False
    },
    {
        "name": "Others",
        "icon": "📦",
        "is_custom": False
    },

    {
        "name": "Gas & Fuel",
        "icon": "⛽",
        "is_custom": False
    },

    {
        "name": "Insurance",
        "icon": "🛡️",
        "is_custom": False
    },
    {
        "name": "Subscriptions & Services",
        "icon": "📱",
        "is_custom": False
    },

    {
        "name": "Online Shopping",
        "icon": "📦",
        "is_custom": False
    },
    {
        "name": "Clothing & Accessories",
        "icon": "👕",
        "is_custom": False
    },
    {
        "name": "Electronics",
        "icon": "💻",
        "is_custom": False
    },

    {
        "name": "Fitness & Gym",
        "icon": "💪",
        "is_custom": False
    },
    {
        "name": "Beauty & Personal Care",
        "icon": "💇",
        "is_custom": False
    },

    {
        "name": "Pets",
        "icon": "🐾",
        "is_custom": False
    },

    {
        "name": "Flights & Travel Bookings",
        "icon": "✈️",
        "is_custom": False
    },
    {
        "name": "Hotels & Accommodation",
        "icon": "🏨",
        "is_custom": False
    },

    {
        "name": "Home & Garden",
        "icon": "🏡",
        "is_custom": False
    },
    {
        "name": "Education & Learning",
        "icon": "📚",
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

    existing_count = db.query(Category).filter(
        Category.is_custom == False
    ).count()

    if existing_count > 0:
        print(f"\nFound {existing_count} existing system categories.")
        print(f"Checking for new categories to add...")
    else:
        print(f"\nNo existing categories found.")

    print(f"\nProcessing {len(DEFAULT_CATEGORIES)} categories...")

    inserted_count = 0
    for category_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(
            Category.name == category_data["name"],
            Category.user_id == None
        ).first()

        if existing:
            print(f"  [SKIP] {category_data['name']} already exists")
            continue

        category = Category(
            name=category_data["name"],
            icon=category_data["icon"],
            color=category_data.get("color"),
            is_custom=category_data["is_custom"],
        )

        db.add(category)
        inserted_count += 1
        print(f"  [OK] Added: {category_data['name']}")

    db.commit()

    print(f"\nSuccessfully inserted {inserted_count} categories!")
    print("=" * 70)

    print("\nVerification - All system categories:")
    categories = db.query(Category).filter(
        Category.user_id == None
    ).order_by(Category.name).all()

    for cat in categories:
        print(f"  {cat.name}")

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
