from finquery_engine import FinQueryEngine

if __name__ == "__main__":
    engine = FinQueryEngine()

    print("\nWelcome to FinQuery! 🧮")
    print("You can ask things like:")
    print(" - Show me total revenue")
    print(" - Show me revenue growth")
    print(" - Show me total assets")
    print(" - Show me cash and equivalents\n")

    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break

        result = engine.query(q)
        print("\nResult:")
        print(result)
        print("-" * 50)


