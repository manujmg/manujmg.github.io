import os
import yaml
import sqlite3
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from custom_logic_adapter import EnhancedRecipeAdapter

def get_random_recipe(db_path="recipes.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, instructions FROM random_recipes ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        title, instructions = row
        return f"Try this recipe: {title}\nInstructions:\n{instructions}"
    else:
        return "No random recipes found in the database."

def main():
    # If an old chatbot.sqlite3 exists, remove it so we start fresh
    if os.path.exists("chatbot.sqlite3"):
        print("Removing old chatbot.sqlite3 to avoid leftover training data.")
        os.remove("chatbot.sqlite3")

    # Create ChatBot
    chatbot = ChatBot(
        "PersonalCookerAssistant",
        storage_adapter="chatterbot.storage.SQLStorageAdapter",
        database_uri="sqlite:///chatbot.sqlite3",
        logic_adapters=[
            # IMPORTANT: Custom logic adapter FIRST
            {'import_path': 'custom_logic_adapter.EnhancedRecipeAdapter'},
            {'import_path': 'chatterbot.logic.MathematicalEvaluation'},
            # BestMatch LAST to avoid overshadowing
            {'import_path': 'chatterbot.logic.BestMatch'}
        ]
    )

    # Minimal training for smalltalk/greetings
    data_dir = "data"
    trainer = ListTrainer(chatbot)

    for filename in os.listdir(data_dir):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            file_path = os.path.join(data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = yaml.safe_load(f)
                if conversation_data and isinstance(conversation_data, list):
                    for pair in conversation_data:
                        if isinstance(pair, list) and len(pair) == 2:
                            trainer.train(pair)

    print("Chatbot training complete!")
    print("Please ensure you have run init_db.py so your DB has your recipes.")
    print("Ask for 'chicken recipe', 'beef recipe', etc., or type 'random recipe'!\n")

    while True:
        try:
            user_input = input("You: ")
            if not user_input.strip():
                continue

            # Intercept "random recipe" queries
            if "random recipe" in user_input.lower() or "random idea" in user_input.lower():
                # Reset last_protein so "other" won't recall an old protein
                for adapter in chatbot.logic_adapters:
                    if isinstance(adapter, EnhancedRecipeAdapter):
                        adapter.last_protein = None

                # Print a random recipe from the entire DB
                recipe = get_random_recipe("recipes.db")
                print("Assistant:", recipe)
            else:
                # Otherwise, let the chatbot process it
                response = chatbot.get_response(user_input)
                print("Assistant:", response)

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()

