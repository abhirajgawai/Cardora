"""
Password Hashing and Verification Utilities

Compare to .NET:
    - Like using IPasswordHasher<User> in ASP.NET Core Identity
    - Or Microsoft.AspNetCore.Identity.PasswordHasher

In .NET you might do:
    var passwordHasher = new PasswordHasher<User>();
    var hashedPassword = passwordHasher.HashPassword(user, password);
    var result = passwordHasher.VerifyHashedPassword(user, hashedPassword, password);

In Python with passlib:
    hash_password(password)  → Hash a password
    verify_password(plain, hashed)  → Verify password against hash
"""

from passlib.context import CryptContext

# ═══════════════════════════════════════════════════════════════════
# PASSWORD CONTEXT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
# Compare to .NET: Like configuring PasswordHasherOptions
# We use bcrypt algorithm which is secure and industry-standard
# - "bcrypt" is the hashing algorithm (same as BCrypt.Net in .NET)
# - deprecated="auto" automatically handles upgrading old hashes

pwd_context = CryptContext(
    schemes=["bcrypt"],  # Hashing algorithm
    deprecated="auto"     # Auto-upgrade deprecated hashes
)

# ═══════════════════════════════════════════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Compare to .NET:
        var hasher = new PasswordHasher<User>();
        string hashed = hasher.HashPassword(user, "MyPassword123!");

    Args:
        password: Plain-text password to hash

    Returns:
        Hashed password (safe to store in database)

    Example:
        >>> hashed = hash_password("MySecurePassword123!")
        >>> print(hashed)
        $2b$12$KIXxl234abc...  # bcrypt hash (60 chars)

    Security Notes:
        - Uses bcrypt with automatic salt generation
        - Cost factor is set to 12 rounds (secure default)
        - Never store plain-text passwords!
        - Each call generates a different hash (due to random salt)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.

    Compare to .NET:
        var hasher = new PasswordHasher<User>();
        var result = hasher.VerifyHashedPassword(user, hashedPassword, password);
        bool isValid = (result == PasswordVerificationResult.Success);

    Args:
        plain_password: The password user entered (plain-text)
        hashed_password: The hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("MyPassword123!")
        >>> verify_password("MyPassword123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False

    Security Notes:
        - Time-constant comparison (prevents timing attacks)
        - Safe against rainbow table attacks (bcrypt uses salt)
        - Never returns the password, only True/False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════
"""
# When user registers:
from app.auth.password import hash_password

user = User(
    email="john@example.com",
    hashed_password=hash_password("UserPassword123!"),  # Hash before storing
    full_name="John Doe"
)
db.add(user)
db.commit()

# When user logs in:
from app.auth.password import verify_password

user = db.query(User).filter(User.email == "john@example.com").first()
if user and verify_password("UserPassword123!", user.hashed_password):
    print("Login successful!")
else:
    print("Invalid credentials")


# Compare to .NET:
// Registration
var passwordHasher = new PasswordHasher<User>();
var user = new User
{
    Email = "john@example.com",
    HashedPassword = passwordHasher.HashPassword(null, "UserPassword123!"),
    FullName = "John Doe"
};
db.Users.Add(user);
db.SaveChanges();

// Login
var user = db.Users.FirstOrDefault(u => u.Email == "john@example.com");
var result = passwordHasher.VerifyHashedPassword(user, user.HashedPassword, "UserPassword123!");
if (result == PasswordVerificationResult.Success)
{
    Console.WriteLine("Login successful!");
}
"""
