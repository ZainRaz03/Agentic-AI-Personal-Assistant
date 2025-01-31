
### GitHub Repository Description:

Advanced Multi-Agent AI System built with Phidata, featuring specialized agents for PDF processing, query handling, information retrieval, and more. Designed for efficiency and scalability in AI operations.

### README.md Content:

# Advanced Multi-Agent AI System

This repository contains the implementation of an advanced multi-agent AI system developed using Phidata. The system integrates various specialized agents, each designed to handle specific tasks such as PDF processing, query handling, personalized responses, file searching, code generation, and fetching the latest news and job updates. This project showcases the integration of Google's Gemini model, PythonTools, Google Search, and other Phidata tools to create a robust, efficient, and scalable AI solution.

## Features

- **PDF Processing Agent**: Analyzes and extracts data from PDF files using PyPDF2 and stores the information in a ChromaDB collection.
- **Query Agent**: Performs deep content searches and data retrieval from indexed documents.
- **Zain Info Agent**: Provides responses based on a detailed knowledge base about an individual's professional and educational background.
- **File Search Agent**: Efficiently locates files across directories using Python's `os` module.
- **Python Generator Agent**: Automates Python code generation based on dynamic queries and saves scripts locally, aiding in code management and deployment.
- **Job/News Search Agent**: Uses real-time queries to source the latest news and job postings, leveraging the Google Search tool.
- **Supervisor Agent**: Coordinates all other agents, intelligently routing queries to the appropriate agent for optimized task handling.

## System Architecture

The system is built on a modular architecture, allowing each agent to operate independently yet cohesively under the supervision of a central Supervisor Agent. This design facilitates easy maintenance, scalability, and enhancement of individual components without impacting the overall system performance.

## Technologies Used

- **Phidata**: For creating and managing AI agents.
- **Google's Gemini Model**: For natural language understanding and generation.
- **PythonTools and Google Search**: Built into Phidata, used for executing Python scripts and performing internet searches.
- **ChromaDB**: For data persistence and retrieval.
- **PyPDF2**: For PDF file processing.
- **Streamlit**: For creating and managing the web interface.

## Setup and Installation

1. **Clone the Repository**
  
   git clone https://github.com/yourusername/multi-agent-ai-system.git
   cd multi-agent-ai-system
  

2. **Install Dependencies**

   pip install -r requirements.txt
   

3. **Environment Variables**
   Set up the necessary environment variables in a `.env` file or your environment:
   
   API_KEY='Your_API_Key_Here'
   

4. **Run the Application**
   
   streamlit run app.py
   

## Contributing

Contributions to enhance the functionality, improve the usability, or provide additional features are welcome. Please fork the repository and submit pull requests with a detailed description of the changes and their benefits.



This README provides a comprehensive overview of your project, including its features, setup instructions, technology stack, and how to contribute, ensuring that anyone visiting your repository can understand and use your project effectively. Adjust the repository link, email, and any specific instructions as needed.
