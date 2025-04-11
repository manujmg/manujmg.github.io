import sqlite3
from recipes import RECIPES

def initialize_db(db_path="recipes.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS random_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    ''')
 
    all_recipe_data = []
    for recipe_name, steps in RECIPES.items():
        title = recipe_name.title()  # e.g., "Butter Chicken"
        instructions_str = "\n".join(steps)
        all_recipe_data.append((title, instructions_str, title))

    cursor.executemany("""
    INSERT INTO random_recipes (title, instructions)
    SELECT ?, ?
    WHERE NOT EXISTS (
        SELECT 1 FROM random_recipes WHERE title = ?
    )
    """, all_recipe_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized with sample recipes.")

