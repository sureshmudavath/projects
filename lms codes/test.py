import string
import random
import unittest
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

class LibraryManagementSystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Check if the current version of chromedriver exists
        # and if it doesn't exist, download it automatically,
        # then add chromedriver to path
        chromedriver_autoinstaller.install()
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)  # seconds
        cls.base_url = "http://localhost:5000"

    def test_navigation_to_home(self):
        driver = self.driver
        driver.get(f"{self.base_url}/")
        
        # Check that the home page has loaded by finding a specific header or element
        _main = driver.find_element(By.TAG_NAME, "main")
        self.assertIn("Get Started", _main.text)

    def test_navigation_to_about(self):
        driver = self.driver
        driver.get(f"{self.base_url}/about")
        
        # Check that the About page has loaded by finding a specific header or element
        h2 = driver.find_element(By.TAG_NAME, "h2")
        self.assertIn("About Us", h2.text)

    def test_navigation_to_contact(self):
        driver = self.driver
        driver.get(f"{self.base_url}/contact")
        
        # Check that the About page has loaded by finding a specific header or element
        h2 = driver.find_element(By.TAG_NAME, "h2")
        self.assertIn("Contact Us", h2.text)

    def test_register_librarian(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Confirm login by checking for redirection to login page after successful registration
        message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "h2"))
        )
        self.assertIn("Forgot Password?", driver.page_source)

    def test_login_librarian(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for librarian login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        self.assertIn("Add Book", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    def test_librarian_available_books(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for librarian login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        driver.get(f"{self.base_url}/librarian/available/books") # Available books
        self.assertIn("Search books available in inventory", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    def test_librarian_borrow_history(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for librarian login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        driver.get(f"{self.base_url}/librarian/borrows") # Borrow History
        self.assertIn("Search patron borrows", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout


    def test_librarian_profile(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for librarian login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "librarian-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        driver.get(f"{self.base_url}/librarian/profile") # Profile
        self.assertIn("Save Changes", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    def test_register_patron(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Confirm login by checking for redirection to login page after successful registration
        message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "h2"))
        )
        self.assertIn("Forgot Password?", driver.page_source)

    def test_login_patron(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for patron login
        driver.find_element(By.NAME, "email").send_keys(ex)
        driver.find_element(By.NAME, "password").send_keys(x)
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        self.assertIn("History", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    def test_patron_borrow_history(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for patron login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        driver.get(f"{self.base_url}/patron/history") # history
        self.assertIn("Recent Borrow History", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    def test_patron_profile(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register")
        
        # Fill out the registration form
        driver.find_element(By.ID, "name").send_keys(x:=generate_random_string())
        driver.find_element(By.ID, "email").send_keys(ex:=f"{x}@example.com")
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "confirm_password").send_keys(x)
        driver.find_element(By.ID, "phone").send_keys("+1 123 456 7890")
        driver.find_element(By.ID, "institution").send_keys(f"{x} university")
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()


        # Input for patron login
        driver.find_element(By.ID, "email").send_keys(ex)
        driver.find_element(By.ID, "password").send_keys(x)
        driver.find_element(By.ID, "patron-role").click()
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Verify login by checking for a specific element that only appears on the dashboard
        dashboard_text = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        driver.get(f"{self.base_url}/patron/profile") # Profile
        self.assertIn("Save Changes", driver.page_source)
        driver.get(f"{self.base_url}/logout") # Logout

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
