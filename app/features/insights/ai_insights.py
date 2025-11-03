"""
AI-Powered Insights Service using Gemini API

Generates personalized financial insights using Google Gemini AI.
Uses aggregated transaction summary (not raw transactions) to reduce cost.

Cost Analysis:
- Raw transactions: ~50,000 tokens × $0.00025/token = $12.50 per insight
- Aggregated summary: ~500 tokens × $0.00025/token = $0.175 per insight
- Savings: 100x cheaper! ✨

Expected Usage:
- 100 users × 1 statement/month = 100 insights/month
- 100 × $0.175 = $17.50/month
- Annual: $210/year

Algorithm:
1. Get transaction summary from StatisticsEngine
2. Build AI prompt with financial analysis guidelines
3. Call Gemini API to generate personalized insight
4. Parse and validate response
5. Return insight data for database storage
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

import google.generativeai as genai

from app.features.transactions.models import Transaction
from app.features.insights.models import Insight, InsightTransaction
from app.features.insights.statistics_engine import StatisticsEngine
from app.core.config import settings


class AIInsightsService:
    """
    AI-powered financial insights using Gemini API

    Features:
    - Personalized spending analysis
    - Actionable financial advice
    - Cost-optimized using aggregated data
    - Friendly, non-judgmental tone
    """

    # Gemini model to use (using stable 2.5-flash model)
    # Note: Using different model than PDF extraction due to API compatibility
    MODEL_NAME = "models/gemini-2.5-flash"

    def __init__(self, db: Session):
        self.db = db
        self._configure_gemini()

    def _configure_gemini(self):
        """Configure Gemini API with key from environment"""
        api_key = settings.GEMINI_API_KEY

        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not configured! "
                "Please set it in .env file. "
                "Get API key from: https://makersuite.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)
        print("[AI INSIGHTS] Gemini AI configured successfully")

    def generate_insight(
        self,
        user_id: str,
        transactions: List[Transaction],
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None,
        existing_insight_types: Optional[set] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate AI-powered personalized insight

        Args:
            user_id: UUID of the user
            transactions: List of user transactions
            date_range: Optional tuple of (earliest_date, latest_date)
            statement_periods: Optional list of (month, year) tuples

        Returns:
            Dict with insight data or None if generation fails
            {
                "insight_type": "ai_personalized",
                "title": "Your coffee spending is 40% of dining expenses",
                "description": "Over the past 3 months, you've spent $180 on coffee...",
                "impact_score": 8,
                "potential_savings": 50.00,
                "transaction_ids": [list of relevant transaction UUIDs]
            }
        """

        print(f"\n{'='*60}")
        print(f"[AI INSIGHTS] Starting AI insight generation")
        print(f"[AI INSIGHTS] Total transactions: {len(transactions)}")
        print(f"{'='*60}\n")

        if len(transactions) < 10:
            print(f"[AI INSIGHTS] NOT ENOUGH TRANSACTIONS - Need at least 10, got {len(transactions)}")
            return None

        try:
            # Step 1: Generate aggregated summary using StatisticsEngine
            print("[AI INSIGHTS] Generating transaction summary with StatisticsEngine...")
            stats_engine = StatisticsEngine(transactions, user_id)
            summary = stats_engine.generate_summary()

            print(f"[AI INSIGHTS] Summary generated successfully:")
            print(f"[AI INSIGHTS]   - Total spent: ${summary['overview']['total_spent']}")
            print(f"[AI INSIGHTS]   - Transaction count: {summary['overview']['transaction_count']}")
            print(f"[AI INSIGHTS]   - Date range: {summary['overview']['date_range']}")
            print(f"[AI INSIGHTS]   - Top categories: {len(summary['categories'])}")
            print(f"[AI INSIGHTS]   - Top merchants: {len(summary['top_merchants'])}")

            # Step 2: Build AI prompt
            prompt = self._build_prompt(summary, existing_insight_types or set())

            # Step 3: Call Gemini API
            print("[AI INSIGHTS] Calling Gemini API...")

            # Use exact configuration that worked in tests - hardcoded model name
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            response = model.generate_content(prompt)

            print("[AI INSIGHTS] Gemini API response received")

            # Step 4: Debug response structure
            print(f"[AI INSIGHTS DEBUG] Response candidates: {len(response.candidates) if response.candidates else 0}")
            if response.candidates:
                candidate = response.candidates[0]
                print(f"[AI INSIGHTS DEBUG] Finish reason: {candidate.finish_reason}")
                print(f"[AI INSIGHTS DEBUG] Has content: {candidate.content is not None}")
                if candidate.content:
                    print(f"[AI INSIGHTS DEBUG] Parts count: {len(candidate.content.parts) if candidate.content.parts else 0}")

                # Check safety ratings
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    print(f"[AI INSIGHTS DEBUG] Safety ratings: {candidate.safety_ratings}")

            # Check response validity
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else None
                print(f"[AI INSIGHTS] ERROR: No valid response from Gemini (finish_reason: {finish_reason})")
                print(f"[AI INSIGHTS] Finish reason codes: 1=STOP (success), 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION")

                # Check for safety issues
                if finish_reason == 3:  # SAFETY
                    print("[AI INSIGHTS] Response blocked by safety filters")
                    print("[AI INSIGHTS] Prompt may contain sensitive financial data")
                elif finish_reason == 2:  # MAX_TOKENS
                    print("[AI INSIGHTS] Response truncated - max tokens reached")
                    print("[AI INSIGHTS] This is unusual for such a short response")

                return None

            # Parse response
            insight_data = self._parse_response(response.text)

            if not insight_data:
                print("[AI INSIGHTS] Failed to parse AI response")
                return None

            # Step 5: Find relevant transactions for this insight
            # Use the top spending categories/merchants mentioned in the insight
            relevant_txn_ids = self._find_relevant_transactions(
                transactions,
                insight_data,
                summary
            )

            # Step 6: Return complete insight data
            result = {
                "insight_type": "ai_personalized",
                "title": insight_data["title"],
                "description": insight_data["description"],
                "impact_score": insight_data.get("impact_score", 8),  # Default to high impact
                "potential_savings": insight_data.get("potential_savings"),
                "transaction_ids": relevant_txn_ids
            }

            print(f"[AI INSIGHTS] Successfully generated AI insight:")
            print(f"[AI INSIGHTS]   Title: {result['title']}")
            print(f"[AI INSIGHTS]   Impact Score: {result['impact_score']}")
            print(f"[AI INSIGHTS]   Linked Transactions: {len(result['transaction_ids'])}")

            return result

        except Exception as e:
            print(f"[AI INSIGHTS] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _build_prompt(self, summary: Dict[str, Any], existing_insight_types: set) -> str:
        """
        Build Gemini prompt for financial insight generation

        Args:
            summary: Aggregated transaction summary from StatisticsEngine
            existing_insight_types: Set of insight types already generated

        Returns:
            Formatted prompt string for Gemini API
        """

        # Convert summary to clean JSON string
        summary_json = json.dumps(summary, indent=2)

        # Map insight types to topics to avoid
        topics_to_avoid = []
        if "weekend_spending" in existing_insight_types:
            topics_to_avoid.append("weekend vs weekday spending patterns")
        if "transport_savings" in existing_insight_types:
            topics_to_avoid.append("ride-sharing vs public transport")
        if "smart_spending_praise" in existing_insight_types:
            topics_to_avoid.append("public transport usage praise")
        if "subscription_detection" in existing_insight_types:
            topics_to_avoid.append("recurring subscriptions")
        if "recurring_habit" in existing_insight_types:
            topics_to_avoid.append("recurring merchant habits")

        # Build avoidance instruction
        avoid_instruction = ""
        if topics_to_avoid:
            topics_list = ", ".join(topics_to_avoid)
            avoid_instruction = f"\n\nIMPORTANT: We already have insights about {topics_list}. Generate a DIFFERENT insight focusing on other spending patterns."

        prompt = f"""Analyze this spending data:

{summary_json}
{avoid_instruction}

Generate a financial insight as JSON with fields: title, description, impact_score, potential_savings, key_category."""

        return prompt

    def _parse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse Gemini API response

        Args:
            response_text: Raw text from Gemini API

        Returns:
            Parsed insight dict or None if parsing fails
        """

        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Remove ```json
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Remove ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Remove trailing ```

            cleaned = cleaned.strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Validate required fields
            if not data.get("title") or not data.get("description"):
                print("[AI INSIGHTS] Missing required fields in response")
                return None

            # Ensure impact_score is in valid range (1-10)
            if "impact_score" in data:
                data["impact_score"] = max(1, min(10, int(data.get("impact_score", 8))))
            else:
                data["impact_score"] = 8  # Default high impact

            return data

        except json.JSONDecodeError as e:
            print(f"[AI INSIGHTS] JSON parsing error: {str(e)}")
            print(f"[AI INSIGHTS] Raw response: {response_text[:200]}...")
            return None
        except Exception as e:
            print(f"[AI INSIGHTS] Unexpected error parsing response: {str(e)}")
            return None

    def _find_relevant_transactions(
        self,
        transactions: List[Transaction],
        insight_data: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> List[str]:
        """
        Find transactions most relevant to the AI insight

        Strategy:
        1. If insight mentions a specific category, return top transactions from that category
        2. Otherwise, return top 20 transactions by amount (to show biggest expenses)

        Args:
            transactions: All user transactions
            insight_data: Parsed AI insight data
            summary: Transaction summary from StatisticsEngine

        Returns:
            List of transaction UUIDs
        """

        key_category = insight_data.get("key_category")

        # If AI mentioned a specific category, filter by that
        if key_category:
            relevant_txns = [
                txn for txn in transactions
                if txn.category and txn.category.name == key_category
            ]
            # Sort by amount (descending) and take top 20
            relevant_txns.sort(key=lambda x: x.amount, reverse=True)
            return [str(txn.id) for txn in relevant_txns[:20]]

        # Otherwise, return top 20 transactions by amount
        sorted_txns = sorted(transactions, key=lambda x: x.amount, reverse=True)
        return [str(txn.id) for txn in sorted_txns[:20]]

    def save_insight(
        self,
        user_id: str,
        insight_data: Dict[str, Any]
    ) -> Insight:
        """
        Save AI insight to database with linked transactions

        Args:
            user_id: User UUID
            insight_data: Insight data dict from generate_insight()

        Returns:
            Created Insight object
        """

        print(f"[AI INSIGHTS] Saving AI insight to database")

        # Create insight record
        insight = Insight(
            user_id=user_id,
            insight_type=insight_data["insight_type"],
            title=insight_data["title"],
            description=insight_data["description"],
            impact_score=insight_data["impact_score"],
            potential_savings=insight_data.get("potential_savings")
        )

        self.db.add(insight)
        self.db.flush()  # Get insight ID

        # Link transactions
        for txn_id in insight_data["transaction_ids"]:
            insight_txn = InsightTransaction(
                insight_id=insight.id,
                transaction_id=txn_id
            )
            self.db.add(insight_txn)

        self.db.commit()
        self.db.refresh(insight)

        print(f"[AI INSIGHTS] Saved insight: {insight.id}")
        return insight
