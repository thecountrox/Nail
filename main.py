import ollama
import os

REMOTE_OLLAMA_HOST = "http://192.168.1.15:11434"

os.environ["OLLAMA_HOST"] = REMOTE_OLLAMA_HOST

DEFAULT_MODEL = "gemma3:1b"

def stream_response_from_remote(prompt: str, model_name: str = DEFAULT_MODEL):

    print(f"Connecting to remote Ollama at: {REMOTE_OLLAMA_HOST}")
    print(f"Using model: {model_name}")
    print(f"Prompt: '{prompt}'\n")

    try:
        client = ollama.Client()

        messages = [{'role': 'user', 'content': prompt}]

        full_response_content = ""
        print("Streaming Response:\n")
        for chunk in client.chat(model=model_name, messages=messages, stream=True):
            if chunk.get('message') and chunk['message'].get('content'):
                content_part = chunk['message']['content']
                print(content_part, end='', flush=True)
                full_response_content += content_part
        print("\n\n--- End of Stream ---")
        return full_response_content

    except ollama.ResponseError as e:
        print(f"\nError from Ollama API: {e}")
        if "connection refused" in str(e).lower() or "failed to connect" in str(e).lower():
            print("Troubleshooting Tip: The Ollama server might not be running or is not accessible at the specified host and port.")
            print("Ensure `OLLAMA_HOST=0.0.0.0` is set on the remote server and firewall allows port 11434.")
        elif "model '" in str(e).lower() and "' not found" in str(e).lower():
            print(f"Troubleshooting Tip: The model '{model_name}' might not be pulled on the remote Ollama server.")
            print(f"Run `ollama pull {model_name}` on your remote server.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check your remote server's status and network connectivity.")


def stream_multi_turn_conversation_remote(model_name: str = DEFAULT_MODEL):
    """
    Conducts a multi-turn conversation with a remote Ollama instance, streaming responses.
    """
    print(f"Starting multi-turn chat with remote Ollama at {REMOTE_OLLAMA_HOST} using model: {model_name}")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    messages = []
    client = ollama.Client()

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Ending conversation.")
            break

        messages.append({'role': 'user', 'content': user_input})

        print("AI (streaming): ", end='', flush=True)
        assistant_response_content = ""
        try:
            for chunk in client.chat(model=model_name, messages=messages, stream=True):
                if chunk.get('message') and chunk['message'].get('content'):
                    content_part = chunk['message']['content']
                    print(content_part, end='', flush=True)
                    assistant_response_content += content_part
            print() 
            messages.append({'role': 'assistant', 'content': assistant_response_content})

        except ollama.ResponseError as e:
            print(f"\nError during chat: {e}")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            break


if __name__ == "__main__":

    # Example 1: Single turn streaming
    print("\n--- Running Single Turn Streaming Example ---")
    prompt_single = "Tell me a detailed story about a sentient AI discovering the beauty of nature."
    stream_response_from_remote(prompt=prompt_single)

    # Example 2: Multi-turn conversational streaming
    print("\n--- Running Multi-Turn Conversational Streaming Example ---")
    stream_multi_turn_conversation_remote()
