import json
from langchain_community.chat_models import ChatOpenAI
from pymongo import MongoClient
from langchain.schema import HumanMessage

# === Setup your Llama3 LLM endpoint ===
llm = ChatOpenAI(
    base_url="http://172.29.160.1:1234/v1",
    api_key="sk-no-key-needed",  # dummy or real if needed
    model="dolphin3.0-llama3.1-8b"
)

# === Setup MongoDB ===
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db["mycollection"]
except Exception:
    print("MongoDB connection failed, using mock data.")
    collection = None

def process_natural_language_query(user_query):
    # Craft prompt for chat messages
    prompt_messages = [
        HumanMessage(content=(
            "Translate the following natural language query into a valid MongoDB find query dictionary (only JSON object):\n"
            f"{user_query}\n"
            "Answer ONLY with the MongoDB query dictionary in JSON format."
        ))
    ]

    # Invoke the chat completions API
    response = llm.invoke(prompt_messages)
    mongo_query_json_str = response.content.strip()
    print(f"DEBUG: Generated MongoDB query JSON string:\n{mongo_query_json_str}")

    try:
        query_dict = json.loads(mongo_query_json_str)

        if collection is not None:
            # Detect if the LLM's output signals a count request
            # For example, your LLM outputs {"count": true}
            if isinstance(query_dict, dict) and query_dict.get("count") is True:
                count = collection.count_documents({})
                return {"totalUsers": count}

            # Otherwise, assume normal find query
            results_cursor = collection.find(query_dict)
            results = list(results_cursor)
            if not results:
                return "No matching records found."
            return results
        else:
            # Mock data if no MongoDB connection
            return [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]

    except json.JSONDecodeError:
        return f"Error decoding MongoDB query JSON: {mongo_query_json_str}"
    except Exception as e:
        return f"Error processing query: {str(e)}"


def main():
    print("Welcome! Enter your natural language query (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break

        response = process_natural_language_query(user_input)
        print("AI Response:", response)

if __name__ == "__main__":
    main()
