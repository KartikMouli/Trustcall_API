import psycopg2
from urllib.parse import urlparse
from faker import Faker
import random
import os
import environ
from datetime import datetime

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# Parse the DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment")

parsed_db_url = urlparse(DATABASE_URL)

DB_SETTINGS = {
    "dbname": parsed_db_url.path[1:], 
    "user": parsed_db_url.username,
    "password": parsed_db_url.password,
    "host": parsed_db_url.hostname,
    "port": parsed_db_url.port or 5432,
}


# Establish connection to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        exit(1)


# Populate dummy data
def populate_data():
    faker = Faker('en_IN')  # Set the locale to Indian
    conn = connect_db()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute(
        """
        TRUNCATE TABLE base_user, base_contact, base_spamrecord, base_globalphonebook, base_spamreport RESTART IDENTITY CASCADE;
        """
    )

    # Create dummy users with default blank values for extra fields
    for _ in range(100):
        phone_number = '+91' + faker.phone_number()[3:15]  # Ensuring the phone number starts with +91
        email = faker.email()  # Ensure that email is generated

        # If email is None or empty, provide a fallback email
        if not email:
            email = faker.user_name() + "@example.com"

        # Hash the password for security
        password = "password123"  # Using a default password for now
        # Inside your loop, add the date_joined
        date_joined = datetime.now()

        username = faker.user_name()
        first_name = faker.first_name()  # Generating first name
        last_name = faker.last_name()  # Generating last name
        is_superuser = False  # Default to False
        is_staff = False  # Default to False
        is_active = True  # Default to True

        cursor.execute(
            """
    INSERT INTO base_user (username, phone_number, email, email_address, password, first_name, last_name, is_superuser, is_staff, is_active,date_joined)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);
    """,
            (
                username,
                phone_number,
                email,
                email,
                password,
                first_name,
                last_name,
                is_superuser,
                is_staff,
                is_active,
                date_joined,
            ),
        )

    print("Dummy data populated successfully 1")

    # Create dummy contacts with default blank values
    for _ in range(200):
        user_id = random.randint(1, 100)
        phone_number = '+91' + faker.phone_number()[3:15]  # Ensuring the phone number starts with +91
        name = faker.name()
        cursor.execute(
            """
            INSERT INTO base_contact (user_id, phone_number, name)
            VALUES (%s, %s, %s);
            """,
            (user_id, phone_number, name),
        )

    print("Dummy data populated successfully 2")

    # Create dummy spam records
    for _ in range(50):
        phone_number = '+91' + faker.phone_number()[3:15]  # Ensuring the phone number starts with +91
        spam_count = random.randint(1, 10)
        last_reported = datetime.now()
        cursor.execute(
            """
            INSERT INTO base_spamrecord (phone_number, spam_count,last_reported)
            VALUES (%s, %s,%s);
            """,
            (phone_number, spam_count, last_reported),
        )

    print("Dummy data populated successfully 3")

    # Create dummy global phonebook entries
    for _ in range(150):
        phone_number = '+91' + faker.phone_number()[3:15]  # Ensuring the phone number starts with +91
        name = faker.name()
        is_spam = faker.boolean(chance_of_getting_true=20)  # 20% chance of being spam
        cursor.execute(
            """
            INSERT INTO base_globalphonebook (phone_number, name, is_spam)
            VALUES (%s, %s, %s);
            """,
            (phone_number, name, is_spam),
        )

    print("Dummy data populated successfully 4")    

    # Create dummy spam reports
    for _ in range(100):
        user_id = random.randint(1, 100)  # Select a random user
        user_cursor = conn.cursor()
        user_cursor.execute("SELECT username FROM base_user WHERE id = %s", (user_id,))
        user = user_cursor.fetchone()

        phone_number = '+91' + faker.phone_number()[3:15]  # Ensuring the phone number starts with +91
        reported_at = datetime.now()

        cursor.execute(
            """
            INSERT INTO base_spamreport (user_id, phone_number, reported_at)
            VALUES (%s, %s, %s);
            """,
            (user_id, phone_number, reported_at),
        )
    

    conn.commit()
    cursor.close()
    conn.close()
    print("Dummy data populated successfully 5")


if __name__ == "__main__":
    populate_data()
