from faker import Faker
from datetime import datetime
import random
import psycopg2
from urllib.parse import urlparse
import os
import environ

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

# Generate and populate dummy data
def populate_data():
    faker = Faker('en_IN')  # Set locale to Indian
    conn = connect_db()
    cursor = conn.cursor()

    # Clear existing data from tables
    cursor.execute(
        """
        TRUNCATE TABLE base_user, base_contact, base_spamreport RESTART IDENTITY CASCADE;
        """
    )

    # Populate User table
    for _ in range(100):
        phone_number = '+91' + faker.msisdn()[3:13]  # Ensure phone number starts with +91
        email = faker.email() or f"{faker.user_name()}@example.com"  # Fallback email if empty
        username = faker.user_name()
        first_name = faker.first_name()
        last_name = faker.last_name()
        is_superuser = False  # Default value
        is_staff = False  # Default value
        is_active = True  # Default value
        date_joined = datetime.now()

        cursor.execute(
            """
            INSERT INTO base_user (username, phone_number, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                username,
                phone_number,
                email,
                "password123",  # Default password for testing purposes
                first_name,
                last_name,
                is_superuser,
                is_staff,
                is_active,
                date_joined,
            ),
        )
    print("Dummy Users populated successfully.")

    # Populate Contact table
    for _ in range(200):
        owner_id = random.randint(1, 100)  # Assuming user IDs range from 1 to 100
        phone_number = '+91' + faker.msisdn()[3:13]
        name = faker.name()

        cursor.execute(
            """
            INSERT INTO base_contact (owner_id, phone_number, name)
            VALUES (%s, %s, %s);
            """,
            (owner_id, phone_number, name),
        )
    print("Dummy Contacts populated successfully.")

    # Populate SpamReport table
    for _ in range(100):
        reporter_id = random.randint(1, 100)  # Assuming user IDs range from 1 to 100
        phone_number = '+91' + faker.msisdn()[3:13]
        timestamp = datetime.now()

        cursor.execute(
            """
            INSERT INTO base_spamreport (reporter_id, phone_number, timestamp)
            VALUES (%s, %s, %s);
            """,
            (reporter_id, phone_number, timestamp),
        )
    print("Dummy Spam Reports populated successfully.")

    conn.commit()
    cursor.close()
    conn.close()
    print("All dummy data populated successfully.")


if __name__ == "__main__":
    populate_data()
