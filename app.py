import os
import openai  # Updated import statement
from dotenv import load_dotenv
import chainlit as cl

print("all_ok!")

load_dotenv() 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Corrected typo

openai.api_key = OPENAI_API_KEY  # Set the API key

print("client has created")

template = """SQL tables (and columns):
* Customers(customer_id, signup_date)
* Streaming(customer_id, video_id, watch_date, watch_minutes)

A well-written SQL query that {input}:
```"""

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": ["```"],
}

@cl.step(type="llm", language="sql")  # Removed 'root' argument
async def text_to_sql(text: str):
    # Create a ChatGeneration to enable the prompt playground
    generation = cl.ChatGeneration(
        provider="openai",  # Corrected provider reference
        messages=[
            {
                "role": "user",
                "content": template.format(input=text),
            }
        ],
        settings=settings,
        variables={"input": text},
    )
    print(generation.messages)

    # Call OpenAI
    response = await openai.ChatCompletion.acreate(
        model=settings["model"],
        messages=generation.messages,
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"],
        top_p=settings["top_p"],
        frequency_penalty=settings["frequency_penalty"],
        presence_penalty=settings["presence_penalty"],
        stop=settings["stop"],
    )

    current_step = cl.context.current_step

    for choice in response.choices:
        if token := choice.message.get("content", ""):
            await current_step.stream_token(token)

    generation.completion = current_step.output

    current_step.generation = generation

@cl.on_message
async def main(message: cl.Message):
    await text_to_sql(message.content)