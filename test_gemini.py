from dotenv import load_dotenv                             # load_dotenv reads the .env file
from langchain_google_genai import ChatGoogleGenerativeAI  # LangChain's wrapper for Gemini models

load_dotenv()                                              # puts GOOGLE_API_KEY into environment variables

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")     # create the model; the key is found automatically
reply = llm.invoke("Say hello in one short sentence.")     # send one question to Gemini
print(reply.content)                                       # print the answer text