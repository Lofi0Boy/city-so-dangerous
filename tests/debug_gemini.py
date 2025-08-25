import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

# Simple test to see what Gemini returns
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

message = HumanMessage(content=[
    {"type": "text", "text": """Analyze this test. Return ONLY valid JSON with this structure:
{
  "hazards": {
    "FIRE": {
      "degree_of_risk": "LOW",
      "description": "No fire visible"
    }
  }
}"""}
])

response = llm.invoke([message])
print("Raw response:")
print(repr(response.content))
print("\nFormatted response:")
print(response.content)