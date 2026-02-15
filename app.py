"""
Ask PDF — Upload a PDF and ask questions about its content using OpenAI.

Architecture overview:
  1. Extract raw text from the uploaded PDF (PyPDF2).
  2. Split text into overlapping chunks so each fits within the model's context.
  3. Embed every chunk with OpenAI's embedding model and index them in FAISS.
  4. At query time, find the most relevant chunks via cosine similarity.
  5. Feed those chunks + the user's question into a chat model to produce an answer.
"""

from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader

# LangChain packages (modular, >=0.3 ecosystem)
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback


def main():
    """Entry point for the Streamlit application."""

    # Load environment variables – expects OPENAI_API_KEY in a .env file
    load_dotenv()

    # ── Streamlit page setup ────────────────────────────────────────────
    st.set_page_config(page_title="Ask your PDF")
    st.header("Ask your PDF 💬")

    # ── Step 1: PDF upload ──────────────────────────────────────────────
    pdf = st.file_uploader("Upload your PDF", type="pdf")

    if pdf is not None:
        # ── Step 2: Extract text from every page ────────────────────────
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # ── Step 3: Split text into overlapping chunks ──────────────────
        # Overlap ensures that context at chunk boundaries is preserved.
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)

        # ── Step 4: Embed chunks & build a FAISS vector index ───────────
        # Each chunk is converted to a vector via OpenAI embeddings and
        # stored in a local FAISS index for fast nearest-neighbour search.
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        # ── Step 5: Accept the user's question ──────────────────────────
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            # Retrieve the most semantically relevant chunks
            docs = knowledge_base.similarity_search(user_question)

            # ── Step 6: Run the QA chain ────────────────────────────────
            # ChatOpenAI uses the Chat Completions API (gpt-4o-mini is
            # fast, cheap, and capable for document Q&A tasks).
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            chain = load_qa_chain(llm, chain_type="stuff")

            # Track token usage / cost with the OpenAI callback
            with get_openai_callback() as cb:
                response = chain.invoke(
                    {"input_documents": docs, "question": user_question}
                )
                print(cb)  # log token usage to the console

            # Display the model's answer
            st.write(response["output_text"])


if __name__ == "__main__":
    main()
