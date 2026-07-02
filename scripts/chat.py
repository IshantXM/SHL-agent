import requests
import json

def main():
    url = "http://127.0.0.1:8000/chat"
    history = []
    
    print("=" * 60)
    print("SHL Assessment Recommendation Agent Chat")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            history.append({"role": "user", "content": user_input})
            
            # Send history to the local API server
            response = requests.post(url, json={"messages": history})
            response.raise_for_status()
            
            data = response.json()
            reply = data.get("reply", "")
            recs = data.get("recommendations", [])
            
            print(f"\nAgent: {reply}")
            if recs:
                print("\nRecommended Assessments:")
                for idx, r in enumerate(recs, 1):
                    print(f"  {idx}. {r['name']}")
                    print(f"     URL: {r['url']}")
                    
            # Keep the agent's reply in the message history
            history.append({"role": "assistant", "content": reply})
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: Could not reach the API server. Make sure `python -m uvicorn app.main:app --reload` is running. Details: {e}")

if __name__ == "__main__":
    main()
