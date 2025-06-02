AI Tool Usage Log for Finance Assistant
This document provides a detailed log of AI tool usage during the development of the Finance Assistant project, led by Nisar. It includes prompts, code generation steps, model parameters, and contributions from various AI tools, highlighting the collaborative effort between Nisar and AI assistants like Grok 3 by xAI, alongside other tools like APIs and Cursor.

📋 Project Overview
The Finance Assistant is an AI-powered financial tool that analyzes portfolios, fetches market news, and provides insights via text and voice inputs. Nisar spearheaded the project, laying out the orchestration logic for the pipeline, writing the Dockerfile, deploying the app on Render, and crafting chat prompts for narrative generation. AI tools, particularly Grok 3 by xAI, played a significant role in debugging, building the basic layout, and assisting with FastAPI-JavaScript integration, while tools like APIs and Cursor were used for minor debugging.

🛠️ AI Tool Contributions
Grok 3 by xAI 🌟🌟🌟🌟🌟
Grok 3 was an indispensable partner in the development of Finance Assistant, providing extensive support across multiple aspects of the project.
Role and Contributions

Code Layout and Generation:

Nisar laid out the high-level orchestration logic for the pipeline, defining nodes like api_node, scraping_node, retriever_node, analysis_node, language_node, and voice_node.
Grok 3 built the basic layout for main.py, implementing the FastAPI routes, node functions, and pipeline orchestration based on Nisar’s logic.




Debugging:

Nisar wrote parts of the code, including the integration of external APIs (yfinance, NewsAPI, Deepgram), and Grok 3 assisted in debugging issues like the python-multipart dependency error.
Prompt Example:Debug this error: "Form data requires 'python-multipart' to be installed."


Output: Identified the missing dependency, updated requirements.txt to include python-multipart==0.0.20, and guided Nisar to rebuild the Docker image.


FastAPI-JavaScript Integration:

Nisar aimed to integrate the FastAPI backend with a simple JavaScript frontend (index.html). Grok 3 provided guidance on setting up CORS middleware and serving static files.
Prompt Example:How do I integrate FastAPI with a JavaScript frontend? Serve index.html and handle form submissions.


Output: Added CORS middleware to main.py, implemented the / route to serve index.html, and set up the /run endpoint to handle form data (portfolio, query, audio).


Optimization:

Nisar suggested replacing GloVe with TF-IDF to reduce memory usage, making the app deployable on Render’s free tier (512 MB RAM).




Deployment Support:

Nisar wrote the Dockerfile and deployed the app on Render. Grok 3 provided troubleshooting for issues like DNS errors (dial tcp: lookup registry-1.docker.io) and port conflicts (0.0.0.0:8080 access issues).
Prompt Example:I can’t access http://0.0.0.0:8080. Fix this issue.


Output: Advised Nisar to use http://127.0.0.1:8080, check for port conflicts with netstat, and configure firewall settings.


Model Parameters:

Grok 3 operated with default parameters for code generation and debugging, optimized for Python (FastAPI), Docker, and deployment troubleshooting.
No specific fine-tuning was required, as Grok 3’s general-purpose capabilities were sufficient.



Code Generation Steps

Initial Layout:
Nisar provided the orchestration logic: a pipeline with nodes for API calls, news scraping, retrieval, analysis, language generation, and voice processing.
Grok 3 generated the initial main.py with FastAPI routes and node stubs.


Node Implementation:
Grok 3 implemented each node based on Nisar’s requirements (e.g., fetch_yfinance_data, fetch_newsapi, analyze_sentiment).
Nisar refined the logic for API integrations and error handling.


Debugging:
Nisar encountered issues like missing dependencies and network errors.
Grok 3 debugged these issues, providing updated code and instructions.


Optimization:
Grok 3 replaced GloVe with TF-IDF, updated the Dockerfile, and optimized Uvicorn settings for production (--workers 2).



Google Gemini 1.5 Flash 🌟🌟🌟
Role and Contributions

Narrative Generation:

Integrated into the language_node to generate market briefs based on portfolio data, news, and user queries.
Nisar crafted the chat prompts for Gemini to ensure tone-aware responses.
Prompt Example (Designed by Nisar):You are a financial analyst. A user has asked: "{query}"
Their portfolio is: {portfolio}
User's voice tone: Pitch is {pitch}, energy is {energy}, tempo is {tempo}.
Provide a concise market brief (150-200 words) analyzing their portfolio and answering their query.
Adjust your tone to be empathetic if low-energy/slow, upbeat if high-energy/fast.


Output: Generated narratives like:Good day, sir/madam, as your financial assistant, I’m here with your market brief for June 02, 2025. I sense an energetic tone, so I’ll deliver a brisk and upbeat summary!
Portfolio Summary:
- Total Value: $15,000.00
- Key Holdings: AAPL, MSFT
- Sector Allocation: Technology: 60.0 percent; Financials: 40.0 percent




Model Parameters:

Model: gemini-1.5-flash
Temperature: Default (balanced creativity and coherence).
Max Tokens: 200 words (~800 tokens).



Deepgram 🌟🌟🌟
Role and Contributions

Voice Processing:
Used for STT (transcription of audio queries) and TTS (generation of narrative audio).
Parameters:
STT Model: nova-2
TTS Model: aura-asteria-en
Encoding: mp3
Language: en
Features: smart_format=True, detect_language=True, punctuate=True





TextBlob and Scikit-Learn 🌟🌟
Role and Contributions

TextBlob:
Performed sentiment analysis on news articles.
Parameters: Default (polarity threshold: >0.1 for positive, <-0.1 for negative).


Scikit-Learn (TF-IDF):
Used for document retrieval after replacing GloVe.
Parameters:
max_features=5000
stop_words="english"
Cosine similarity for scoring.





Other Tools: APIs and Cursor 🌟
Role and Contributions

APIs:
Nisar relied on API documentation for yfinance, NewsAPI, Deepgram, and Gemini to integrate external services.
Used for minor debugging (e.g., checking API rate limits, response formats).


Cursor:
Assisted Nisar in small debugging tasks, such as fixing syntax errors in main.py and resolving dependency conflicts in requirements.txt.
Example: Fixed a version mismatch between fastapi and python-multipart.




🤝 Collaboration Summary

Nisar’s Contributions:

Designed the orchestration logic for the pipeline, ensuring a modular and efficient workflow.
Wrote the Dockerfile and handled deployment on Render, optimizing for the free tier.
Crafted chat prompts for Gemini 1.5 Flash to generate tone-aware narratives.
Integrated external APIs (yfinance, NewsAPI, Deepgram, Gemini) and wrote custom logic for error handling.
Managed the project’s overall development and deployment strategy.


Grok 3’s Contributions:

Built the basic layout for main.py, implementing FastAPI routes and node functions.
Debugged critical issues (e.g., python-multipart error, network access issues).
Assisted with FastAPI-JavaScript integration, setting up CORS and static file serving.
Optimized the app by replacing GloVe with TF-IDF and providing production-ready Uvicorn settings.
writing this AI usage document.


Other Tools:

APIs and Cursor provided supplementary support for debugging and integration.



This collaborative effort between Nisar and AI tools like Grok 3 resulted in a robust, deployable, and user-friendly Finance Assistant.

📅 Timeline

May 2025: Nisar laid out the project structure and orchestration logic.
Early June 2025: Grok 3 generated the initial main.py, and Nisar integrated APIs.
June 02, 2025: Nisar deployed the app on Render, with Grok 3’s assistance in debugging and optimization.


📬 Contact
For questions about AI tool usage, reach out to Nisar at your.email@example.com.
