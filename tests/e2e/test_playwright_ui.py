"""
Playwright E2E tests for FastAPI Calculator UI
Tests the complete user flow through the web interface
Integrated with existing test infrastructure from conftest.py
"""
import pytest
import re
from playwright.sync_api import Page, expect
from faker import Faker

fake = Faker()

# Use the fastapi_server fixture from conftest.py to get the base URL
@pytest.fixture
def base_url(fastapi_server: str) -> str:
    """Returns the FastAPI server base URL from the existing fixture"""
    return fastapi_server.rstrip("/")


# ======================================================================================
# Test Home Page
# ======================================================================================
class TestHomePage:
    """Test cases for the home/landing page"""

    @pytest.mark.e2e
    def test_home_page_loads(self, page: Page, base_url: str):
        """Test that the home page loads successfully"""
        page.goto(base_url)
        expect(page).to_have_url(base_url + "/")
        # Check that page loaded (not specific to avoid coupling to home page content)
        expect(page.locator("body")).to_be_visible()


# ======================================================================================
# Test User Registration
# ======================================================================================
class TestUserRegistration:
    """Test cases for user registration flow"""

    @pytest.mark.e2e
    def test_registration_page_loads(self, page: Page, base_url: str):
        """Test that registration page has all required form elements"""
        page.goto(f"{base_url}/register")
        
        # Check all form fields exist based on register.html
        expect(page.locator("#username")).to_be_visible()
        expect(page.locator("#email")).to_be_visible()
        expect(page.locator("#first_name")).to_be_visible()
        expect(page.locator("#last_name")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator("#confirm_password")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    @pytest.mark.e2e
    def test_successful_registration(self, page: Page, base_url: str):
        """Test successful user registration flow"""
        page.goto(f"{base_url}/register")
        
        # Generate unique test user data
        test_user = {
            "username": f"testuser_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        # Fill registration form using exact IDs from register.html
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        
        # Submit form
        page.locator("button[type='submit']").click()
        
        # Should show success message and redirect to login
        expect(page.locator("#successAlert")).to_be_visible(timeout=5000)
        expect(page.locator("#successMessage")).to_contain_text("Registration successful")
        
        # Wait for redirect to login page
        page.wait_for_url(re.compile(".*/login"), timeout=10000)

    @pytest.mark.e2e
    def test_registration_password_mismatch(self, page: Page, base_url: str):
        """Test registration fails when passwords don't match"""
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"testuser_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill("SecurePass123!")
        page.locator("#confirm_password").fill("DifferentPass123!")
        
        page.locator("button[type='submit']").click()
        
        # Should show error message
        expect(page.locator("#errorAlert")).to_be_visible(timeout=5000)
        expect(page.locator("#errorMessage")).to_contain_text("do not match", flags=re.IGNORECASE)

    @pytest.mark.e2e
    def test_registration_duplicate_username(self, page: Page, base_url: str):
        """Test registration fails with duplicate username"""
        page.goto(f"{base_url}/register")
        
        # Create first user
        test_user = {
            "username": f"duplicate_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        
        # Wait for success
        expect(page.locator("#successAlert")).to_be_visible(timeout=5000)
        
        # Try to register again with same username but different email
        page.goto(f"{base_url}/register")
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(fake.email())
        page.locator("#first_name").fill(fake.first_name())
        page.locator("#last_name").fill(fake.last_name())
        page.locator("#password").fill("SecurePass123!")
        page.locator("#confirm_password").fill("SecurePass123!")
        page.locator("button[type='submit']").click()
        
        # Should show error
        expect(page.locator("#errorAlert")).to_be_visible(timeout=5000)

    @pytest.mark.e2e
    def test_registration_invalid_email(self, page: Page, base_url: str):
        """Test registration validates email format"""
        page.goto(f"{base_url}/register")
        
        page.locator("#username").fill(f"testuser_{fake.random_number(digits=8)}")
        page.locator("#email").fill("not-a-valid-email")
        page.locator("#first_name").fill(fake.first_name())
        page.locator("#last_name").fill(fake.last_name())
        page.locator("#password").fill("SecurePass123!")
        page.locator("#confirm_password").fill("SecurePass123!")
        page.locator("button[type='submit']").click()
        
        # Should show error for invalid email
        expect(page.locator("#errorAlert")).to_be_visible(timeout=5000)


# ======================================================================================
# Test User Login
# ======================================================================================
class TestUserLogin:
    """Test cases for user login flow"""

    @pytest.mark.e2e
    def test_login_page_loads(self, page: Page, base_url: str):
        """Test that login page has all required elements"""
        page.goto(f"{base_url}/login")
        
        # Check form fields based on login.html
        expect(page.locator("#username")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator("#remember")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    @pytest.mark.e2e
    def test_successful_login(self, page: Page, base_url: str):
        """Test successful user login and redirect to dashboard"""
        # First register a user
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"logintest_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        
        # Wait for registration success
        page.wait_for_timeout(2000)
        
        # Now login
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        
        # Should show success and redirect to dashboard
        expect(page.locator("#successAlert")).to_be_visible(timeout=5000)
        page.wait_for_url(re.compile(".*/dashboard"), timeout=10000)
        
        # Verify we're on dashboard
        expect(page.locator("#userWelcome")).to_contain_text(test_user["username"])

    @pytest.mark.e2e
    def test_login_wrong_password(self, page: Page, base_url: str):
        """Test login fails with incorrect password"""
        # Register user first
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"wrongpass_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
        
        # Try to login with wrong password
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill("WrongPassword123!")
        page.locator("button[type='submit']").click()
        
        # Should show error
        expect(page.locator("#errorAlert")).to_be_visible(timeout=5000)

    @pytest.mark.e2e
    def test_login_nonexistent_user(self, page: Page, base_url: str):
        """Test login fails with non-existent username"""
        page.goto(f"{base_url}/login")
        
        page.locator("#username").fill("nonexistentuser12345")
        page.locator("#password").fill("SomePassword123!")
        page.locator("button[type='submit']").click()
        
        # Should show error
        expect(page.locator("#errorAlert")).to_be_visible(timeout=5000)


# ======================================================================================
# Test Dashboard and Calculator Operations
# ======================================================================================
class TestDashboard:
    """Test cases for dashboard functionality"""

    @pytest.fixture
    def logged_in_page(self, page: Page, base_url: str):
        """Fixture to provide a logged-in session"""
        # Register user
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"dashtest_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
        
        # Login
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_url(re.compile(".*/dashboard"), timeout=10000)
        
        return page

    @pytest.mark.e2e
    def test_dashboard_loads_authenticated(self, logged_in_page: Page):
        """Test that dashboard loads for authenticated users"""
        expect(logged_in_page.locator("#userWelcome")).to_be_visible()
        expect(logged_in_page.locator("#calculationForm")).to_be_visible()
        expect(logged_in_page.locator("#calculationsTable")).to_be_visible()

    @pytest.mark.e2e
    def test_dashboard_redirects_unauthenticated(self, page: Page, base_url: str):
        """Test that unauthenticated users cannot access dashboard"""
        page.goto(f"{base_url}/dashboard")
        
        # Should redirect to login
        page.wait_for_url(re.compile(".*/login"), timeout=5000)

    @pytest.mark.e2e
    def test_logout_functionality(self, logged_in_page: Page, base_url: str):
        """Test user logout"""
        # Click logout button
        logged_in_page.locator("#logoutBtn").click()
        
        # Confirm logout in dialog
        logged_in_page.on("dialog", lambda dialog: dialog.accept())
        logged_in_page.locator("#logoutBtn").click()
        
        # Should redirect to login
        logged_in_page.wait_for_url(re.compile(".*/login"), timeout=5000)


# ======================================================================================
# Test Calculator Operations
# ======================================================================================
class TestCalculatorOperations:
    """Test cases for calculator operations through the UI"""

    @pytest.fixture
    def logged_in_page(self, page: Page, base_url: str):
        """Fixture to provide a logged-in session"""
        # Register and login
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"calctest_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
        
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_url(re.compile(".*/dashboard"), timeout=10000)
        
        return page

    @pytest.mark.e2e
    def test_addition_calculation(self, logged_in_page: Page):
        """Test addition operation through UI"""
        # Select addition from dropdown
        logged_in_page.locator("#calcType").select_option("addition")
        
        # Enter numbers
        logged_in_page.locator("#calcInputs").fill("10,5")
        
        # Submit
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        # Should show success message
        expect(logged_in_page.locator("#successAlert")).to_be_visible(timeout=5000)
        
        # Wait for table to update
        logged_in_page.wait_for_timeout(1000)
        
        # Check result appears in history table
        expect(logged_in_page.locator("#calculationsTable")).to_contain_text("15")

    @pytest.mark.e2e
    def test_subtraction_calculation(self, logged_in_page: Page):
        """Test subtraction operation through UI"""
        logged_in_page.locator("#calcType").select_option("subtraction")
        logged_in_page.locator("#calcInputs").fill("20,8")
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        expect(logged_in_page.locator("#successAlert")).to_be_visible(timeout=5000)
        logged_in_page.wait_for_timeout(1000)
        expect(logged_in_page.locator("#calculationsTable")).to_contain_text("12")

    @pytest.mark.e2e
    def test_multiplication_calculation(self, logged_in_page: Page):
        """Test multiplication operation through UI"""
        logged_in_page.locator("#calcType").select_option("multiplication")
        logged_in_page.locator("#calcInputs").fill("6,7")
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        expect(logged_in_page.locator("#successAlert")).to_be_visible(timeout=5000)
        logged_in_page.wait_for_timeout(1000)
        expect(logged_in_page.locator("#calculationsTable")).to_contain_text("42")

    @pytest.mark.e2e
    def test_division_calculation(self, logged_in_page: Page):
        """Test division operation through UI"""
        logged_in_page.locator("#calcType").select_option("division")
        logged_in_page.locator("#calcInputs").fill("100,4")
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        expect(logged_in_page.locator("#successAlert")).to_be_visible(timeout=5000)
        logged_in_page.wait_for_timeout(1000)
        expect(logged_in_page.locator("#calculationsTable")).to_contain_text("25")

    @pytest.mark.e2e
    def test_invalid_input_validation(self, logged_in_page: Page):
        """Test that invalid inputs show error"""
        logged_in_page.locator("#calcType").select_option("addition")
        logged_in_page.locator("#calcInputs").fill("5")  # Only one number
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        # Should show error for insufficient inputs
        expect(logged_in_page.locator("#errorAlert")).to_be_visible(timeout=5000)


# ======================================================================================
# Test Calculation History Management
# ======================================================================================
class TestCalculationHistory:
    """Test cases for calculation history CRUD operations"""

    @pytest.fixture
    def logged_in_page(self, page: Page, base_url: str):
        """Fixture to provide a logged-in session"""
        page.goto(f"{base_url}/register")
        
        test_user = {
            "username": f"histtest_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
        
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_url(re.compile(".*/dashboard"), timeout=10000)
        
        return page

    @pytest.mark.e2e
    def test_calculation_appears_in_history(self, logged_in_page: Page):
        """Test that new calculations appear in history table"""
        # Perform a calculation
        logged_in_page.locator("#calcType").select_option("addition")
        logged_in_page.locator("#calcInputs").fill("15,3")
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        
        logged_in_page.wait_for_timeout(1000)
        
        # Check history table contains the calculation
        table = logged_in_page.locator("#calculationsTable")
        expect(table).to_contain_text("addition", flags=re.IGNORECASE)
        expect(table).to_contain_text("15")
        expect(table).to_contain_text("3")
        expect(table).to_contain_text("18")

    @pytest.mark.e2e
    def test_delete_calculation_from_history(self, logged_in_page: Page):
        """Test deleting a calculation from history"""
        # Create a calculation
        logged_in_page.locator("#calcType").select_option("subtraction")
        logged_in_page.locator("#calcInputs").fill("8,2")
        logged_in_page.locator("#calculationForm button[type='submit']").click()
        logged_in_page.wait_for_timeout(1000)
        
        # Handle the confirmation dialog
        logged_in_page.on("dialog", lambda dialog: dialog.accept())
        
        # Click delete button
        delete_button = logged_in_page.locator(".delete-calc").first
        delete_button.click()
        
        # Should show success message
        expect(logged_in_page.locator("#successAlert")).to_be_visible(timeout=5000)

    @pytest.mark.e2e
    def test_empty_history_message(self, logged_in_page: Page):
        """Test that empty history shows appropriate message"""
        # On a fresh login, history should be empty or show message
        table = logged_in_page.locator("#calculationsTable")
        
        # Either shows "No calculations found" or has no rows
        content = table.text_content()
        # This will pass if either no calculations exist or message is shown
        assert "No calculations" in content or content.strip() == ""


# ======================================================================================
# Test Responsive Design
# ======================================================================================
@pytest.mark.e2e
class TestResponsiveness:
    """Test cases for responsive design across different viewports"""

    def test_mobile_viewport_login(self, page: Page, base_url: str):
        """Test that login page works on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{base_url}/login")
        
        expect(page.locator("#username")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    def test_tablet_viewport_dashboard(self, page: Page, base_url: str):
        """Test that dashboard works on tablet viewport"""
        page.set_viewport_size({"width": 768, "height": 1024})
        
        # Quick register and login
        page.goto(f"{base_url}/register")
        test_user = {
            "username": f"tablet_{fake.random_number(digits=8)}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": "SecurePass123!"
        }
        
        page.locator("#username").fill(test_user["username"])
        page.locator("#email").fill(test_user["email"])
        page.locator("#first_name").fill(test_user["first_name"])
        page.locator("#last_name").fill(test_user["last_name"])
        page.locator("#password").fill(test_user["password"])
        page.locator("#confirm_password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
        
        page.goto(f"{base_url}/login")
        page.locator("#username").fill(test_user["username"])
        page.locator("#password").fill(test_user["password"])
        page.locator("button[type='submit']").click()
        page.wait_for_url(re.compile(".*/dashboard"), timeout=10000)
        
        # Check dashboard elements are visible
        expect(page.locator("#calculationForm")).to_be_visible()
        expect(page.locator("#calculationsTable")).to_be_visible()
