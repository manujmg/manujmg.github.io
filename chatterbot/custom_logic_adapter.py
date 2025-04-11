import sqlite3
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement

def get_random_recipe_by_protein(db_path, protein):
    """
    Look for rows in 'random_recipes' table whose title or instructions
    contain the given protein (case-insensitive).
    Return one random match, or None if none found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, instructions
        FROM random_recipes
        WHERE LOWER(title) LIKE '%' || ? || '%'
           OR LOWER(instructions) LIKE '%' || ? || '%'
        ORDER BY RANDOM() LIMIT 1
    """, (protein.lower(), protein.lower()))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None

def format_recipe_steps(title, instructions):
    """
    Convert instructions into a multiline step format.
    """
    lines = [f"Here is a random {title} recipe:"]
    steps = instructions.strip().split("\n")
    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}")
    return "\n".join(lines)

class EnhancedRecipeAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.known_proteins = ["chicken", "beef", "turkey", "fish", "salmon"]
        self.last_protein = None
        self.db_path = "recipes.db"
        self.pending_question = False

    def can_process(self, statement):
        text = statement.text.lower()

        # If waiting for user yes/no, that overrides everything
        if self.pending_question:
            return True

        # If user says "other", "other recipe", or "another recipe"
        if "other recipe" in text or "another recipe" in text or text.strip() == "other":
            return True

        # If user says "recipe" plus one of our known proteins
        if "recipe" in text and any(prot in text for prot in self.known_proteins):
            return True

        return False

    def process(self, input_statement, additional_response_selection_parameters=None):
        text = input_statement.text.lower()

        # If we previously asked “Do you want the same protein or random?” => parse yes/no
        if self.pending_question:
            return self.handle_pending_question(text)

        # “other recipe” / “another recipe” / “other”
        if "other recipe" in text or "another recipe" in text or text.strip() == "other":
            if self.last_protein:
                response_text = (
                    f"I recall you wanted a {self.last_protein} recipe. "
                    "Do you want another random recipe with the same protein? (Yes/No)"
                )
            else:
                response_text = (
                    "We haven't talked about a specific protein yet. "
                    "Should I pick a random recipe from the entire DB? (Yes/No)"
                )
            self.pending_question = True
            return Statement(text=response_text, confidence=1.0)

        # e.g. “chicken recipe”, “beef recipe”, “fish recipe”
        matched_protein = None
        for p in self.known_proteins:
            if p in text:
                matched_protein = p
                break

        if matched_protein:
            title, instructions = get_random_recipe_by_protein(self.db_path, matched_protein)
            if title and instructions:
                self.last_protein = matched_protein
                return Statement(
                    text=format_recipe_steps(title, instructions),
                    confidence=1.0
                )
            else:
                return Statement(
                    text=f"Sorry, I couldn't find any {matched_protein} recipes in the database.",
                    confidence=1.0
                )

        # fallback if none matched
        return Statement(text="", confidence=0.0)

    def handle_pending_question(self, user_text):
        self.pending_question = False
        user_text = user_text.strip().lower()

        # yes => same protein
        if any(word in user_text for word in ["yes", "same", "sure"]):
            if self.last_protein:
                title, instructions = get_random_recipe_by_protein(self.db_path, self.last_protein)
                if title and instructions:
                    return Statement(text=format_recipe_steps(title, instructions), confidence=1.0)
                else:
                    return Statement(
                        text=f"Sorry, I couldn't find more {self.last_protein} recipes in the DB.",
                        confidence=1.0
                    )
            else:
                # no last protein => fully random
                return self.get_random_recipe_stmt()

        # no => different => random
        elif any(word in user_text for word in ["no", "different", "new"]):
            return self.get_random_recipe_stmt()

        # user typed something else => re-ask
        else:
            self.pending_question = True
            return Statement(
                text="I wasn't sure if you wanted the same protein or a random recipe. Please say 'yes' or 'no.'",
                confidence=1.0
            )

    def get_random_recipe_stmt(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, instructions FROM random_recipes ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            title, instructions = row
            return Statement(text=format_recipe_steps(title, instructions), confidence=1.0)
        else:
            return Statement(text="No recipes found in the database!", confidence=1.0)

