# Langchain Ask PDF (Tutorial)

>You may find the step-by-step video tutorial to build this application [on Youtube](https://youtu.be/wUAUdEw5oxM) and corresponding [GitHub repository](https://github.com/alejandro-ao/langchain-ask-pdf).

![See example](docs/PDF-LangChain.jpg?raw=true "Title")

This is a Python application that allows you to load a PDF and ask questions about it using natural language. The application uses a LLM to generate a response about your PDF. The LLM will not answer questions unrelated to the document.

## How it works

The application reads the PDF and splits the text into smaller chunks that can be then fed into a LLM. It uses OpenAI embeddings to create vector representations of the chunks. The application then finds the chunks that are semantically similar to the question that the user asked and feeds those chunks to the LLM to generate a response.

The application uses Streamlit to create the GUI and Langchain to deal with the LLM.


## Installation

To install the repository, please clone this repository and install the requirements:

```
pip install -r requirements.txt
```

You will also need to add your OpenAI API key to the `.env` file.

## Usage

To use the application, run the `main.py` file with the streamlit CLI (after having installed streamlit): 

```
streamlit run app.py
```

## CodiumAI Explaination

See [codium.ai](https://codium.ai/) for details.

## Code Analysis

### Inputs
- No direct inputs to the function `main()`. However, the function relies on the user uploading a PDF file and providing a question about the PDF.
___

### Flow
1. The function loads the environment variables using `load_dotenv()`.
2. The page configuration is set using `st.set_page_config()`.
3. The header "Ask your PDF 💬" is displayed using `st.header()`.
4. The user is prompted to upload a PDF file using `st.file_uploader()`.
5. If a PDF file is uploaded, the text is extracted from the PDF using `PdfReader` and `page.extract_text()`.
6. The extracted text is split into chunks using `CharacterTextSplitter`.
7. Embeddings are created using `OpenAIEmbeddings`.
8. A knowledge base is created using `FAISS.from_texts()`.
9. The user is prompted to ask a question about the PDF using `st.text_input()`.
10. If a question is provided, similarity search is performed on the knowledge base using `knowledge_base.similarity_search()`.
11. A question answering chain is loaded using `load_qa_chain()`.
12. The question answering chain is run with the input documents and user question using `chain.run()`.
13. The response is displayed using `st.write()`.
___

### Outputs
- The function does not have any direct outputs. However, the response to the user's question about the PDF is displayed using `st.write()`.
___

## LangChain
Learn how to use [LangChain](https://python.langchain.com/docs/get_started/introduction)  as a framework for developing applications powered by language models.

## FAISS
[FAISS](https://faiss.ai/index.html) is a library for efficient similarity search and clustering of dense vectors.

## Contributing

This repository is for educational purposes only and is not intended to receive further contributions. It is supposed to be used as support material for the YouTube tutorial that shows how to build the project.


