"""Commands For postgresql"""

CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password TEXT,
        email VARCHAR(50) UNIQUE
    )
"""

CREATE_TABLE_MOVIES = """
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title VARCHAR(25),
        genre VARCHAR(15),
        rating float
    )
"""

CREATE_TABLE_RENTALS = """
    CREATE TABLE IF NOT EXISTS rentals (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT,
        rental_duration FLOAT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
    );
"""

INSERT_INTO_USERS = """
    INSERT INTO users (username, password, email) 
    VALUES ($1, $2, $3) 
    RETURNING username, password, email
"""

INSERT_INTO_MOVIES = """
    INSERT INTO movies (title, genre, rating) 
    VALUES ($1, $2, $3) 
    RETURNING title, genre, rating
"""

INSERT_INTO_RENTALS = """
    INSERT INTO rentals (user_id, movie_id, rental_duration) 
    VALUES ($1, $2, $3) 
    RETURNING user_id, movie_id, rental_duration
"""

SELECT_USER_BY_USERNAME = """
    SELECT * FROM users WHERE username = $1
"""

SELECT_USER_BY_EMAIL = """
    SELECT * FROM users WHERE email = $1
"""

SELECT_ALL_FROM_MOVIES = """
    SELECT * FROM movies
"""

SELECT_RENTALS_BY_USER = """
    SELECT rentals.id, rentals.user_id, rentals.movie_id, rentals.rental_duration, 
           movies.title AS movie_title, users.username AS user_username
    FROM rentals
    JOIN movies ON rentals.movie_id = movies.id
    JOIN users ON rentals.user_id = users.id
    WHERE users.username = $1;
"""

SELECT_ALL_FROM_RENTALS = """
    SELECT * FROM rentals
"""
