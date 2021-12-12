DIALECT = "postgresql"
DRIVER = "psycopg2"
HOST = "127.0.0.1"
PORT = 5432
USERNAME = "postgres"
PASSWORD = "root1234"
DB = "postgres"

# dialect + driver://username:passwor@host:port/database
DB_URI = f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"
