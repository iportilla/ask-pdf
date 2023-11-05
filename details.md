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

## #7 - #13 details:
This section creates embeddings for a set of text chunks using the **OpenAIEmbeddings** model and then building a **FAISS** index from these embeddings. It allows users to ask questions about a PDF document.

**#7** creates an instance of the **OpenAIEmbeddings** class, which is a pre-trained sentence encoder model that can encode text into high-dimensional vector representations.

**#8** creates a **FAISS** index from a list of text chunks and their corresponding embeddings. **FAISS** is a library for efficient similarity search and clustering of high-dimensional vectors. The from_texts() function is a utility function provided by **FAISS** that creates an index from a list of text chunks and their corresponding embeddings. The chunks argument is a list of text chunks, and the embeddings argument is the pre-trained sentence encoder model that was created in the previous line.

The resulting **knowledge_base** object is a **FAISS index** that can be used to perform similarity search on the text chunks.

**#10** uses the similarity_search() method of the **knowledge_base** object to find the most similar text chunks in the PDF document to the user's question. The resulting **docs** variable is a list of text chunks that are most similar to the user's question.

**#11** creates an instance of the **OpenAI language model** and load a pre-trained question-answering model called chain. The **chain model** is a pipeline that takes a question and a set of documents as input and returns the most likely answer to the question based on the information in the documents. See [LangChain Stuff chain Documentation](https://python.langchain.com/docs/modules/chains/document/stuff), this chain is well-suited for applications where documents are small and only a few are passed in for most calls.

**#12** These lines use the **run()** method of the **chain** object to run the question-answering pipeline on the user's question and the text chunks in the PDF document. The resulting **response** variable is a **dictionary** containing the answer to the user's question and other information about the question-answering process.

The **with get_openai_callback() as cb:** statement is used to capture the logs and metrics generated by the **OpenAI API** during the question-answering process. The **cb variable** is a callback object that can be used to access these logs and metrics. The **print(cb)** statement is used to print the logs and metrics to the console.

See [GitHub Copilot](https://github.com/features/copilot) to learn how to chat with your code.

## Contributing

This repository is for educational purposes only and is not intended to receive further contributions. It is supposed to be used as support material for the YouTube tutorial that shows how to build the project.


