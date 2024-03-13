import openai
from openai import AzureOpenAI
#from dotenv import load_dotenv
import os

# Load the environment variables from .env.local file
#load_dotenv(dotenv_path='.env.local')

# Access the variables using os.getenv
azure_api_key = os.getenv('azure_api_key')
azure_endpoint = os.getenv('azure_endpoint')
model = os.getenv('model')
apiVersion = os.getenv('apiVersion')  # Corrected typo

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=azure_api_key,
    azure_endpoint =azure_endpoint,
    api_version=apiVersion  # Corrected typo
)




system_prompt = """
  
"""

def generate_streaming_response(user_message):
    print('in generate_streaming_response')        
    try:                
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": user_message}],
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stream=True
        )
        # Iterate over the stream
        for chunk in stream:
            # Check if there are any choices
            if chunk.choices:
                # Access the first `Choice` object
                choice = chunk.choices[0]

                # Access the `ChoiceDelta` object
                choice_delta = choice.delta

                # Access the `content` property
                content = choice_delta.content                

                # Format the message as a server-sent event
                yield f"data: {content}\n\n"
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
    except openai.OpenAIError as e:
        print("An error occurred")
    except Exception as e:
        print(e)

        
    
def generate_response(user_message):
    response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6, 
        )
       
    # Extract the relevant data from the response
    # This is an example, adjust according to your actual response structure
    extracted_data = {
        "response": response.choices[0].message.content,  # Adjust based on actual response structure            
    }
    return extracted_data
