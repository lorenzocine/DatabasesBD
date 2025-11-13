import mysql.connector
from mysql.connector import Error, connect
import pandas as pd


def get_db_credentials():
    print("Welcome to the MotoGP Database Setup and Query Interface!")
    print("Please provide your MySQL credentials.")
    user = input("Enter your MySQL username: ").strip()
    password = input("Enter your MySQL password: ").strip()
    return user, password


user, password = get_db_credentials()


def create_database(host: str, user: str, password: str, database_name: str):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created or already exists.")
    except Error as e:
        print(f"Error during database creation: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def drop_all_tables(host: str, user: str, password: str, database_name: str):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database_name)
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            print(f"Table '{table_name}' dropped.")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("All tables dropped successfully.")
    except Error as e:
        print(f"Error dropping tables: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def create_tables(host: str, user: str, password: str, database_name: str):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database_name)
        cursor = conn.cursor()
        tables = {
            "Rider": """
                CREATE TABLE IF NOT EXISTS Rider (
                    Rider_ID INT PRIMARY KEY,
                    Name VARCHAR(100),
                    Second_Places INT,
                    Third_Places INT,
                    Victories INT,
                    Fastest_Lap_2022 INT,
                    World_Championships INT,
                    Country VARCHAR(50),
                    Pole_Positions_1974_2022 INT
                );
            """,
            "Race": """
                CREATE TABLE IF NOT EXISTS Race (
                    Race_ID INT PRIMARY KEY,
                    Class VARCHAR(50),
                    Track VARCHAR(50),
                    Times INT
                );
            """,
            "Team": """
                CREATE TABLE IF NOT EXISTS Team (
                    Team_ID INT,
                    Constructor VARCHAR(100),
                    Class VARCHAR(50),
                    Rider_ID INT NOT NULL,
                    PRIMARY KEY (Team_ID, Rider_ID),
                    FOREIGN KEY (Rider_ID) REFERENCES Rider(Rider_ID)
                );
            """,
            "Participates": """
                CREATE TABLE IF NOT EXISTS Participates (
                    Rider_ID INT,
                    Race_ID INT,
                    PRIMARY KEY (Rider_ID, Race_ID),
                    FOREIGN KEY (Rider_ID) REFERENCES Rider(Rider_ID),
                    FOREIGN KEY (Race_ID) REFERENCES Race(Race_ID)
                );
            """,
            "Ranking": """
                CREATE TABLE IF NOT EXISTS Ranking (
                    Season INT,
                    Position INT,
                    Points INT,
                    Rider_ID INT,
                    Race_ID INT,
                    FOREIGN KEY (Rider_ID) REFERENCES Rider(Rider_ID),
                    FOREIGN KEY (Race_ID) REFERENCES Race(Race_ID)
                );
            """
        }
        for table_name, query in tables.items():
            cursor.execute(query)
            print(f"Table '{table_name}' created or already exists.")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def populate_tables(host: str, user: str, password: str, database_name: str, file_paths: dict):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database_name)
        cursor = conn.cursor()
        for table_name, file_path in file_paths.items():
            df = pd.read_csv(file_path, delimiter=';')
            df = df.where(pd.notnull(df), None)
            if table_name == "Team":
                df = df.dropna(subset=['Team_ID'])
            if table_name == "Participates":
                df = df.dropna(subset=['Race_ID'])
            columns = ', '.join([f"`{col}`" for col in df.columns])
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            data = [tuple(None if pd.isna(value) else value for value in row) for row in df.itertuples(index=False)]
            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"Table '{table_name}' populated successfully.")
    except Error as e:
        print(f"Error populating table '{table_name}': {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


QUERIES = {
    "Top 5 riders by race victories": {
        "query": """
            SELECT Name, Victories
            FROM Rider
            ORDER BY Victories DESC
            LIMIT 5;
        """,
        "description": "Find the top 5 riders with the most career victories.",
        "riddle": "I have a handle but no door. I can move water but not hold it. What am I?",
        "answer": "bucket"
    },
    "Nationality Insights" : {
    "query": """
        SELECT 
            Country,
            COUNT(Rider_ID) AS Total_Riders,
            SUM(Victories) AS Total_Victories,
            SUM(Second_Places) AS Total_Second_Places,
            SUM(Third_Places) AS Total_Third_Places,
            SUM(World_Championships) AS Total_World_Championships
        FROM Rider
        GROUP BY Country;
    """,
    "description": "Analyze riders' nationalities with their victories and championships.",
    "riddle": "I unite people from different places under one banner, yet I am no flag. What am I?",
    "answer": "nation"
    },
    "Constructor with the most victories": {
        "query": """
            SELECT T.Constructor, SUM(R.Victories) AS Total_Victories
            FROM Team T
            INNER JOIN Rider R ON T.Rider_ID = R.Rider_ID
            GROUP BY T.Constructor
            ORDER BY Total_Victories DESC
            LIMIT 1;
        """,
        "description": "Identify the constructor with the most victories.",
        "riddle": "I build machines, but I am not a person. What am I?",
        "answer": "factory"
    },
    "Top Riders by Combined Podium Finishes" : {
    "query": """
        SELECT 
            R.Name,
            (R.Victories + R.Second_Places + R.Third_Places) AS Total_Podiums,
            R.World_Championships AS Championships
        FROM Rider R
        WHERE (R.Victories + R.Second_Places + R.Third_Places) > 0
        ORDER BY Total_Podiums DESC, Championships DESC
        LIMIT 5;
    """,
    "description": "Identify the top riders based on their combined podium finishes and championships.",
    "riddle": "I stand on the steps of glory, but I am not a staircase. What am I?",
    "answer": "podium"
    },
    "Top 3 riders by second-place finishes": {
        "query": """
            SELECT Name, Second_Places
            FROM Rider
            ORDER BY Second_Places DESC
            LIMIT 3;
        """,
        "description": "See the top 3 riders with the most second-place finishes.",
        "riddle": "I am second but never the first. What am I?",
        "answer": "silver"
    },
    "Correlation between championships and victories": {
        "query": """
            SELECT R.Name, R.World_Championships, SUM(R.Victories) AS Total_Victories
            FROM Rider R
            GROUP BY R.Name, R.World_Championships
            HAVING R.World_Championships > 0
            ORDER BY Total_Victories DESC
            LIMIT 20;
        """,
        "description": "Explore the relationship between championships and victories.",
        "riddle": "I show connections but have no wires. What am I?",
        "answer": "graph"
    },
    "Rider Performance Score" : {
    "query": """
        SELECT 
            R.Name,
            (R.Victories * 25 + R.Second_Places * 20 + R.Third_Places * 16) AS Performance_Score,
            R.Victories,
            R.Second_Places,
            R.Third_Places
        FROM 
            Rider R
        WHERE 
            R.Victories > 0 OR R.Second_Places > 0 OR R.Third_Places > 0
        ORDER BY 
            Performance_Score DESC
        LIMIT 10;
    """,
    "description": "Estimate rider performance scores based on podium finishes.",
    "riddle": "I weigh the worth of wins, seconds, and thirds, but I am no scale. What am I?",
    "answer": "score"
},
"Tracks with Most Distinct Classes" : {
    "query": """
        SELECT 
            R.Track,
            COUNT(DISTINCT R.Class) AS Distinct_Classes
        FROM 
            Race R
        GROUP BY 
            R.Track
        ORDER BY 
            Distinct_Classes DESC
        LIMIT 3;
    """,
    "description": "Identify the tracks that host the highest number of distinct race classes.",
    "riddle": "I hold races for all classes, yet I am not a school. What am I?",
    "answer": "track"
}
}

MAIN_RIDDLE = {
    "question": "I contain many secrets, yet I am unlocked by a single key. What am I?",
    "answer": "database"
}


def run_query(query, host, user, password, database_name):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database_name)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        print(f"{' | '.join(column_names)}")
        print("-" * (len(column_names) * 15))
        for row in results:
            print(" | ".join(map(str, row)))
    except Error as e:
        print(f"Error executing query: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def main():
    create_database(host='localhost', user=user, password=password, database_name='project')
    drop_all_tables(host='localhost', user=user, password=password, database_name='project')
    create_tables(host='localhost', user=user, password=password, database_name='project')

    file_paths = {
        "Rider": r"C:\Users\test\Desktop\Databases & Big Data\Project\MotoGP Finali\rider table.csv",
        "Race": r"C:\Users\test\Desktop\Databases & Big Data\Project\MotoGP Finali\consolidated_race_table .csv",
        "Team": r"C:\Users\test\Desktop\Databases & Big Data\Project\MotoGP Finali\team table.csv",
        "Participates": r"C:\Users\test\Desktop\Databases & Big Data\Project\MotoGP Finali\participates table.csv",
        "Ranking": r"C:\Users\test\Desktop\Databases & Big Data\Project\MotoGP Finali\ranking table.csv"
    }
    populate_tables(host='localhost', user=user, password=password, database_name='project', file_paths=file_paths)

    print("Database setup complete.")
    print("Solve the riddle to unlock the query interface.")
    main_answer = input(f"{MAIN_RIDDLE['question']}\nYour answer: ").strip().lower()
    if main_answer != MAIN_RIDDLE["answer"]:
        print("Incorrect answer. Exiting.")
        return
    print("Correct! The menu of queries is now unlocked.")
    while True:
        print("\nAvailable Queries:")
        for i, (name, details) in enumerate(QUERIES.items(), start=1):
            print(f"{i}. {details['description']}")
        choice = input("Select a query by entering its number (or type 'exit' to quit): ").strip()
        if choice.lower() == "exit":
            print("Goodbye!")
            break
        if not choice.isdigit() or int(choice) not in range(1, len(QUERIES) + 1):
            print("Invalid choice. Try again.")
            continue
        query_name = list(QUERIES.keys())[int(choice) - 1]
        query_details = QUERIES[query_name]
        print(f"Solve the riddle: {query_details['riddle']}")
        answer = input("Your answer: ").strip().lower()
        if answer == query_details["answer"]:
            print("Correct! Executing the query...")
            run_query(query_details["query"], host='localhost', user=user, password=password, database_name='project')
        else:
            print("Incorrect answer. Try again.")

if __name__ == "__main__":
    main()