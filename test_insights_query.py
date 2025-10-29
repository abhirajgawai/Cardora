"""
Quick test to check if insights and insight_transactions tables exist and have data
"""

from app.core.database import get_db, SessionLocal
from app.models.insight import Insight, InsightTransaction
from app.models.transaction import Transaction
from uuid import UUID

# Create a database session
db = SessionLocal()

try:
    # Test 1: Check if insights table exists and has data
    print("=" * 60)
    print("TEST 1: Checking insights table")
    print("=" * 60)

    insights = db.query(Insight).all()
    print(f"Found {len(insights)} insights in database")

    for insight in insights:
        print(f"\nInsight ID: {insight.id}")
        print(f"  User ID: {insight.user_id} (type: {type(insight.user_id)})")
        print(f"  Type: {insight.insight_type}")
        print(f"  Title: {insight.title}")

    # Test 2: Check if insight_transactions table exists
    print("\n" + "=" * 60)
    print("TEST 2: Checking insight_transactions table")
    print("=" * 60)

    insight_txns = db.query(InsightTransaction).all()
    print(f"Found {len(insight_txns)} insight-transaction links in database")

    for it in insight_txns[:5]:  # Show first 5
        print(f"\nLink ID: {it.id}")
        print(f"  Insight ID: {it.insight_id}")
        print(f"  Transaction ID: {it.transaction_id}")

    # Test 3: Try to query specific insight with transactions
    if insights:
        test_insight_id = insights[0].id
        print("\n" + "=" * 60)
        print(f"TEST 3: Querying insight {test_insight_id} with transactions")
        print("=" * 60)

        # Get linked transactions
        insight_transactions = db.query(InsightTransaction).filter(
            InsightTransaction.insight_id == test_insight_id
        ).all()

        print(f"Found {len(insight_transactions)} linked transaction records")

        # Get actual transactions
        transaction_ids = [it.transaction_id for it in insight_transactions]

        if transaction_ids:
            transactions = db.query(Transaction).filter(
                Transaction.id.in_(transaction_ids)
            ).all()

            print(f"Found {len(transactions)} actual transactions")

            for txn in transactions[:3]:  # Show first 3
                print(f"\n  Transaction: {txn.merchant_name} - ${txn.amount}")
        else:
            print("No transaction IDs found!")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
