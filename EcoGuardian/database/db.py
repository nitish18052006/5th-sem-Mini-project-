import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash


def get_server_connection(app):
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"]
    )


def get_connection(app):
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DATABASE"]
    )


def init_db(app):

    try:
        server_conn = get_server_connection(app)
        server_cursor = server_conn.cursor()

        database_name = app.config["MYSQL_DATABASE"]

        server_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}`"
        )

        server_cursor.close()
        server_conn.close()

        conn = get_connection(app)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                eco_points INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS awareness (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                category VARCHAR(100) NOT NULL,
                summary TEXT,
                content TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                description TEXT,
                location VARCHAR(255),
                severity VARCHAR(30),
                priority_score INT DEFAULT 0,
                status VARCHAR(30) DEFAULT 'Submitted',
                image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option_a VARCHAR(255),
                option_b VARCHAR(255),
                option_c VARCHAR(255),
                option_d VARCHAR(255),
                correct_answer VARCHAR(1)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                score INT,
                total INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                points INT DEFAULT 10,
                difficulty VARCHAR(30) DEFAULT 'Easy'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenge_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                challenge_id INT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, challenge_id),
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (challenge_id)
                    REFERENCES challenges(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_id INT NOT NULL,
                user_id INT NOT NULL,
                rating INT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id)
                    REFERENCES reports(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            ("admin@ecoguardian.com",)
        )

        admin = cursor.fetchone()

        if not admin:
            password = generate_password_hash("Admin@123")

            cursor.execute("""
                INSERT INTO users
                (name, email, password, role, eco_points)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                "EcoGuardian Admin",
                "admin@ecoguardian.com",
                password,
                "admin",
                0
            ))

        seed_awareness(cursor)
        seed_quiz(cursor)
        seed_challenges(cursor)

        conn.commit()

        cursor.close()
        conn.close()

        print("Database initialized successfully.")

    except Error as e:
        print("Database error:", e)


def seed_awareness(cursor):

    cursor.execute(
        "SELECT COUNT(*) FROM awareness"
    )

    count = cursor.fetchone()[0]

    if count > 0:
        return

    articles = [

        (
            "Plastic Pollution",
            "Plastic",
            "Plastic waste is one of the major environmental problems.",
            "Plastic pollution occurs when plastic materials accumulate "
            "in the environment. Reduce single-use plastics, reuse "
            "materials and recycle whenever possible."
        ),

        (
            "Water Conservation",
            "Water",
            "Water is a valuable natural resource.",
            "Water conservation means using water carefully and preventing "
            "unnecessary wastage. Repair leaking taps and use water "
            "efficiently."
        ),

        (
            "Air Pollution",
            "Air",
            "Air pollution affects humans, animals and plants.",
            "Air pollution is caused by vehicles, industries, burning "
            "waste and other activities. Public transportation, clean "
            "energy and tree planting can help reduce pollution."
        ),

        (
            "Waste Management",
            "Waste",
            "Proper waste management helps maintain a clean environment.",
            "Separate waste into recyclable, organic and non-recyclable "
            "categories. Follow the principles of reduce, reuse and recycle."
        ),

        (
            "Deforestation",
            "Forest",
            "Forests are important for biodiversity and climate balance.",
            "Deforestation destroys habitats and contributes to climate "
            "change. Protect forests and participate in tree plantation "
            "activities."
        ),

        (
            "Renewable Energy",
            "Energy",
            "Renewable energy reduces dependence on fossil fuels.",
            "Solar, wind and hydropower are examples of renewable energy. "
            "Using energy efficiently can reduce environmental impact."
        )
    ]

    cursor.executemany("""
        INSERT INTO awareness
        (title, category, summary, content)
        VALUES (%s, %s, %s, %s)
    """, articles)


def seed_quiz(cursor):

    cursor.execute(
        "SELECT COUNT(*) FROM quiz_questions"
    )

    count = cursor.fetchone()[0]

    if count > 0:
        return

    questions = [

        (
            "Which practice helps reduce plastic pollution?",
            "Using more plastic bags",
            "Using reusable bags",
            "Burning plastic",
            "Throwing plastic in rivers",
            "B"
        ),

        (
            "Which is a renewable source of energy?",
            "Coal",
            "Petrol",
            "Solar energy",
            "Diesel",
            "C"
        ),

        (
            "Which method saves water?",
            "Leaving taps running",
            "Repairing leaking taps",
            "Wasting drinking water",
            "Using water unnecessarily",
            "B"
        ),

        (
            "What does recycling mean?",
            "Throwing waste away",
            "Burning all waste",
            "Processing waste into reusable materials",
            "Dumping waste",
            "C"
        ),

        (
            "Which activity can cause air pollution?",
            "Tree planting",
            "Vehicle emissions",
            "Rainwater harvesting",
            "Recycling",
            "B"
        ),

        (
            "Which gas is commonly associated with climate change?",
            "Oxygen",
            "Carbon dioxide",
            "Helium",
            "Neon",
            "B"
        ),

        (
            "What is the first step in the waste hierarchy?",
            "Reduce",
            "Burn",
            "Dump",
            "Ignore",
            "A"
        ),

        (
            "Which activity helps protect forests?",
            "Illegal logging",
            "Planting trees",
            "Forest burning",
            "Destroying habitats",
            "B"
        )
    ]

    cursor.executemany("""
        INSERT INTO quiz_questions
        (
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, questions)


def seed_challenges(cursor):

    cursor.execute(
        "SELECT COUNT(*) FROM challenges"
    )

    count = cursor.fetchone()[0]

    if count > 0:
        return

    challenges = [

        (
            "Plastic-Free Day",
            "Avoid single-use plastic products for one complete day.",
            20,
            "Easy"
        ),

        (
            "Plant a Tree",
            "Plant or maintain a tree and help increase green cover.",
            30,
            "Medium"
        ),

        (
            "Save Water",
            "Reduce unnecessary water usage throughout the day.",
            20,
            "Easy"
        ),

        (
            "Use Public Transport",
            "Use public transportation instead of a private vehicle.",
            25,
            "Medium"
        ),

        (
            "Recycle Waste",
            "Separate recyclable waste and send it for recycling.",
            20,
            "Easy"
        ),

        (
            "Energy Saver",
            "Switch off unnecessary lights and electrical appliances.",
            15,
            "Easy"
        )
    ]

    cursor.executemany("""
        INSERT INTO challenges
        (title, description, points, difficulty)
        VALUES (%s, %s, %s, %s)
    """, challenges)