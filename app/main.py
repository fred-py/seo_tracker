from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from openai import OpenAI
from .db import init_db
from .models import Location, OrganicRank
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()
openai_client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))


@app.get("/", include_in_schema=False)
def docs_redirect_controller():
    """Redirect for fastapi documententioon - Disable this on production"""
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}

@app.get("/some_endpoint")
def some_function():
    """
    Implement hyrachical dependency injection
    You can also have dependencies injected into
    other dependencies to create a hierarchical dependency
    graph, which is extremely useful for building cached
    authentication and authorization flows,
    nested data retrieval logic, or complex decision trees
    when implementing your application’s business logic.
    As an example, you can reuse the same database session
    creation or user fetching functions across different
    parts of your API,
    Page 57 
    """
    pass

"""@app.get("/chat")
def chat_controller(prompt: str = "Haha yeah buddy"):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an SEO Optimisation Assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    statement = response.choices[0].message.content
    return {"statement": statement}
"""
