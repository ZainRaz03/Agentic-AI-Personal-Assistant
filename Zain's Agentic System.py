import os
from phi.agent import Agent, RunResponse
from phi.model.google import Gemini
import chromadb
from chromadb.config import Settings
import PyPDF2
import google.generativeai as genai
import streamlit as st
from phi.tools.python import PythonTools
from phi.tools.googlesearch import GoogleSearch
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('API_KEY')
genai.configure(api_key=os.getenv('API_KEY'))

gemini_model = Gemini(id="gemini-1.5-flash")


client = chromadb.Client(Settings(persist_directory="./chromadb"))
try:
    collection = client.get_collection("pdf_chunks")
except:
    collection = client.create_collection(name="pdf_chunks")

class BaseAgent(Agent):
    def __init__(self, name, model, tools=None, description=None, instructions=None, show_tool_calls=False, debug_mode=False):
        super().__init__(
            name=name, 
            model=model,
            tools=tools,
            description=description,
            instructions=instructions,
            show_tool_calls=show_tool_calls,
            debug_mode=debug_mode
        )

    def print_response(self, message):
        return super().print_response(message)


class PDFProcessingAgent(BaseAgent):
    def __init__(self, name, model, collection):
        super().__init__(name, model)
        self.collection = collection

    def process_pdf_files(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory, filename)
                with open(file_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
                        for chunk_id, chunk_text in enumerate(chunks):
                            self.collection.add(
                                documents=[chunk_text],
                                ids=[f"{filename}_{chunk_id}"],
                                metadatas=[{"filename": filename, "page": page_num}]
                            )

class SummaryAgent(BaseAgent):
    def __init__(self, name, model):
        super().__init__(name, model)

    def generate_summary(self, documents, query_text):
        prompt = f"Based on the following relevant text chunks, provide a coherent summary responding to the query '{query_text}':\n\n"
        prompt += "\n".join(f"- {doc}" for doc in documents)
        return self.run(prompt)


class QueryAgent(BaseAgent):
    def __init__(self, name, model, collection, summary_agent, pdf_agent):
        super().__init__(name, model)
        self.collection = collection
        self.summary_agent = summary_agent
        self.pdf_agent = pdf_agent

    def query_pdf_chunks(self, query_text, n_results):
        self.pdf_agent.process_pdf_files("pdf_files")
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        documents = []

        if "documents" in results and results["documents"]:
            for doc_list in results["documents"]:
                for document, metadata in zip(doc_list, results["metadatas"][results["documents"].index(doc_list)]):
                    documents.append(document)
            return self.summary_agent.generate_summary(documents, query_text)

        return "No results found for the query."


class GeneralQueryAgent(BaseAgent):
    def __init__(self, name, model):
        super().__init__(name, model)

    def handle_query(self, query):
        return self.run(f"Handling general query about: {query}")

ZAIN_KNOWLEDGE = """
Here is the information about Zain Raza:

Current Education:
- Institution: PUCIT
- Program: Bachelor's in Computer Science
- Timeline: 2021 - Present
- Current Semester: 8th
- CGPA: 3.93
- Location: Lahore, Pakistan
- Notable Courses: Data Structures, Algorithms, Database Systems, Web Development, Software Engineering

Previous Education:
1. Intermediate (FSc Pre-Engineering)
   - Institution: PGC
   - Duration: 2019 - 2021
   - Percentage: 99%
   - Major Subjects: Physics, Chemistry, Mathematics

2. Matriculation
   - Institution: DPS
   - Completion: 2019
   - Percentage: 98%
   - Major Subjects: Science, Mathematics, Computer Science

Skills:
1. Programming Languages:
   - Python (Advanced, 2 years)
   - Java (Intermediate, 1 year)
   - JavaScript (Intermediate, 1.5 years)

2. Frameworks:
   - React (Intermediate, 1 year)
   - Django (Beginner, 0.5 years)

Projects:
1. E-commerce Platform
   - Technologies: React, Node.js, MongoDB
   - Role: Full Stack Developer
   - Duration: 3 months
   - Description: Developed a full-stack e-commerce platform with user authentication and payment integration

2. Student Management System
   - Technologies: Python, Django, PostgreSQL
   - Role: Backend Developer
   - Duration: 2 months
   - Description: Created a system for managing student records and course registrations
"""


class ZainInfoAgent(BaseAgent):
    def __init__(self, name, model, knowledge_base):
        super().__init__(name, model)
        self.knowledge_base = knowledge_base

    def handle_query(self, query):
        prompt = f"Query about Zain Raza: '{query}'\n\nInformation about Zain Raza:\n{self.knowledge_base}\n"
        prompt += "Please provide a detailed and relevant answer based on the knowledge base."
        return self.run(prompt)


class FileSearchAgent(BaseAgent):
    def __init__(self, name, model):
        super().__init__(name, model)

    def search_file(self, file_name, root_folder="C:/"):
        result_paths = []
        for root, dirs, files in os.walk(root_folder):
            if file_name in files:
                result_paths.append(os.path.join(root, file_name))

        if result_paths:
            return self.run(f"Just explain the following path in words for the File found at: {', '.join(result_paths)}")
        return self.print_response("File not found.")
    

class PythonGeneratorAgent(BaseAgent):
    def __init__(self, name, model):
        super().__init__(name=name, model=model, tools=[PythonTools()], show_tool_calls=False)

    def generate_code(self, query):
        response = self.run(f"{query} and save it in local directory as well. Only give name of the file that is saved in local directory and tell its location.")
        return response

class JobNewsSearchAgent(BaseAgent):
    def __init__(self, name, model):
        super().__init__(
            name=name,
            model=model,
            tools=[GoogleSearch()],
            description="You are a news agent that helps users find the latest news.",
            instructions=[
                "Given a topic by the user, respond with 4 latest news items about that topic.",
                "Search for 10 news items and select the top 4 unique items and also give the website links.",
                "Search in English.",
            ],
            show_tool_calls=True,
            debug_mode=True
        )

    def search_news(self, query):
        return self.run(query, markdown=True)


class SupervisorAgent(BaseAgent):
    def __init__(self, name, model, general_query_agent, query_agent, zain_info_agent, 
                 file_search_agent, python_generator_agent, job_news_agent):
        super().__init__(name, model)
        self.general_query_agent = general_query_agent
        self.query_agent = query_agent
        self.zain_info_agent = zain_info_agent
        self.file_search_agent = file_search_agent
        self.python_generator_agent = python_generator_agent
        self.job_news_agent = job_news_agent

    def route_query(self, query, selected_model):
        if selected_model == 'ZainInfoAgent':
            return self.zain_info_agent.handle_query(query)
        elif selected_model == 'QueryAgent':
            return self.query_agent.query_pdf_chunks(query, 3)
        elif selected_model == 'FileSearchAgent':
            return self.file_search_agent.search_file(query)
        elif selected_model == 'PythonGeneratorAgent':
            return self.python_generator_agent.generate_code(query)
        elif selected_model == 'JobNewsSearchAgent':
            return self.job_news_agent.search_news(query)
        else:
            return self.general_query_agent.handle_query(query)


pdf_agent = PDFProcessingAgent("PDF Processing Agent", gemini_model, collection)
summary_agent = SummaryAgent("Summary Agent", gemini_model)
query_agent = QueryAgent("Query Agent", gemini_model, collection, summary_agent, pdf_agent)
zain_info_agent = ZainInfoAgent("Zain Info Agent", gemini_model, ZAIN_KNOWLEDGE)
general_query_agent = GeneralQueryAgent("General Query Agent", gemini_model)
file_search_agent = FileSearchAgent("File Search Agent", gemini_model)
python_generator_agent = PythonGeneratorAgent("Python Generator Agent", gemini_model)
job_news_agent = JobNewsSearchAgent("Job/News Search Agent", gemini_model)


# Example Queries
# print(supervisor_agent.route_query("Tell me about Babar Azam"))
# print(supervisor_agent.route_query("What is Zain's CGPA?"))
# print(supervisor_agent.route_query("CPP.pdf"))
# print(supervisor_agent.route_query("Types of variables in C++."))

supervisor_agent = SupervisorAgent(
    "Supervisor Agent", 
    gemini_model,
    general_query_agent,
    query_agent,
    zain_info_agent,
    file_search_agent,
    python_generator_agent,
    job_news_agent
)

agents_dict = {
    "FileSearchAgent": file_search_agent,
    "QueryAgent": query_agent,
    "ZainInfoAgent": zain_info_agent,
    "GeneralQueryAgent": general_query_agent,
    "PythonGeneratorAgent": python_generator_agent,
    "JobNewsSearchAgent": job_news_agent
}




# ---------- Streamlit UI ----------
st.title("Zain's Agentic AI System 🔥")

agent_options = {
    "File Finder": "FileSearchAgent",
    "Resume Information": "QueryAgent",
    "Zain Info": "ZainInfoAgent",
    "General Query": "GeneralQueryAgent",
    "Python Code Generator": "PythonGeneratorAgent",
    "Job/News Search": "JobNewsSearchAgent"
}

selected_agent = st.selectbox("Choose an Agent", list(agent_options.keys()))
query_text = st.text_input("Enter your query")

if st.button("Submit"):
    agent_name = agent_options[selected_agent]
    response = supervisor_agent.route_query(query_text, agent_name)
    if isinstance(response, str):
        if "Saved:" in response:
            clean_response = f"INFO     {response}"
            if "Running" in response:
                file_path = response.split("Saved: ")[1].split("\n")[0]
                clean_response = f"INFO     Saved: {file_path}\nINFO     Running {file_path}"
        else:
            clean_response = response
    else:
        clean_response = response.content if hasattr(response, 'content') else str(response)
    st.write("### Response:")
    st.write(clean_response)