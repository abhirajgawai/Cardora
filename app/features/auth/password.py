"""
Password Hashing and Verification Utilities

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
# ═══════════════════════════════════════════════════════════════════

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

        var hasher = new PasswordHasher<User>();
        string hashed = hasher.HashPassword(user, "MyPassword123!");

    Args:
        password: Plain-text password to hash

    Returns:
        Hashed password (safe to store in database)

    Example:
        >>> hashed = hash_password("MySecurePassword123!")
        >>> print(hashed)

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
# ═══════════════════════════════════════════════════════════════════
"""
from app.features.auth.password import hash_password

user = User(
    email="john@example.com",
    full_name="John Doe"
)
db.add(user)
db.commit()

from app.features.auth.password import verify_password

user = db.query(User).filter(User.email == "john@example.com").first()
if user and verify_password("UserPassword123!", user.hashed_password):
    print("Login successful!")
else:
    print("Invalid credentials")


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
