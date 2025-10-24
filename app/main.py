# FastAPI application entry point
# This is similar to Program.cs in ASP.NET Core

from fastapi import FastAPI
from app.routers import auth, users, credit_cards, categories, statements, transactions, analytics

# Create the FastAPI application instance
# Similar to: var app = WebApplication.CreateBuilder(args).Build();
app = FastAPI(
    title="Cardora API",
    description="Credit Card Statement Analyzer with AI-Powered PDF Extraction",
    version="1.0.0"
)

# Register routers (like app.MapControllers() in .NET)
# Compare to .NET: app.MapControllerRoute(...)

# Authentication & Users
app.include_router(auth.router)
app.include_router(users.router)

# Feature 3: AI-Powered Statement Upload
app.include_router(credit_cards.router)  # Manage credit cards
app.include_router(categories.router)  # Transaction categories
app.include_router(statements.router)  # PDF upload & extraction (MAIN FEATURE)
app.include_router(transactions.router)  # View & manage transactions

# Analytics - The Real Value!
app.include_router(analytics.router)  # Spending analysis across cards and time

# Root endpoint - GET /
# The @app.get() decorator is like [HttpGet("/")] attribute in C#
@app.get("/")
def root():
    """
    Root endpoint - returns a welcome message

    In C# this would be:
    [HttpGet("/")]
    public IActionResult Root()
    {
        return Ok(new { message = "Welcome to Cardora API" });
    }
    """
    return {
        "message": "Welcome to Cardora API",
        "version": "1.0.0"
    }

# Health check endpoint - GET /health
@app.get("/health")
def health_check():
    """
    Health check endpoint
    Returns the API status
    """
    return {
        "status": "healthy",
        "service": "Cardora API"
    }
