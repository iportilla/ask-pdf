"""
Ask PDF — Upload a PDF or Excel file and ask questions about its content.

Architecture overview:
  1. Extract raw text from the uploaded file (PyPDF2 for .pdf, pandas for .xlsx).
  2. Split text into overlapping chunks so each fits within the model's context.
  3. Embed every chunk with the selected provider's embedding model and index
     them in FAISS.
  4. At query time, find the most relevant chunks via cosine similarity.
  5. Feed those chunks + the user's question into a chat model to produce an
     answer.

LLM/embeddings provider is selectable at runtime (sidebar): OpenAI (cloud),
Azure OpenAI / AI Foundry, or a local Ollama model — see
build_llm_and_embeddings() / render_provider_sidebar().
"""

import os

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader

# LangChain packages (modular, >=0.3 ecosystem)
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback
from langchain_ollama import OllamaLLM, OllamaEmbeddings


PROVIDER_OPENAI = "OpenAI (cloud)"
PROVIDER_AZURE = "Azure OpenAI / AI Foundry"
PROVIDER_OLLAMA = "Ollama (local)"
PROVIDERS = [PROVIDER_OPENAI, PROVIDER_AZURE, PROVIDER_OLLAMA]


def build_llm_and_embeddings(provider: str, config: dict):
    """Return (llm, embeddings) for the selected provider."""

    if provider == PROVIDER_OPENAI:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        embeddings = OpenAIEmbeddings()
        return llm, embeddings

    if provider == PROVIDER_AZURE:
        llm = AzureChatOpenAI(
            azure_endpoint=config["azure_endpoint"],
            api_key=config["azure_api_key"],
            api_version=config["azure_api_version"],
            azure_deployment=config["azure_llm_deployment"],
            temperature=0,
        )
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=config["azure_endpoint"],
            api_key=config["azure_api_key"],
            api_version=config["azure_api_version"],
            azure_deployment=config["azure_embedding_deployment"],
        )
        return llm, embeddings

    if provider == PROVIDER_OLLAMA:
        llm = OllamaLLM(model=config["ollama_model"], base_url=config["ollama_base_url"])
        embeddings = OllamaEmbeddings(
            model=config["ollama_embedding_model"], base_url=config["ollama_base_url"]
        )
        return llm, embeddings

    raise ValueError(f"Unknown provider: {provider}")


def render_provider_sidebar():
    """Let the user pick an LLM/embeddings provider and its settings.

    Every field defaults from an environment variable (see .env.sample) so the
    app still works with zero clicks if .env is already configured -- the
    sidebar is only there to override or fill in gaps at runtime.
    """
    st.sidebar.header("LLM Provider")
    provider = st.sidebar.selectbox("Where should questions be answered?", PROVIDERS)

    config = {}
    if provider == PROVIDER_AZURE:
        config["azure_endpoint"] = st.sidebar.text_input(
            "Azure endpoint", value=os.getenv("AZURE_OPENAI_ENDPOINT", "")
        )
        config["azure_api_key"] = st.sidebar.text_input(
            "Azure API key", value=os.getenv("AZURE_OPENAI_API_KEY", ""), type="password"
        )
        config["azure_api_version"] = st.sidebar.text_input(
            "API version", value=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        config["azure_llm_deployment"] = st.sidebar.text_input(
            "Chat deployment name", value=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT", "")
        )
        config["azure_embedding_deployment"] = st.sidebar.text_input(
            "Embedding deployment name", value=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
        )
    elif provider == PROVIDER_OLLAMA:
        config["ollama_base_url"] = st.sidebar.text_input(
            "Ollama server URL", value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        config["ollama_model"] = st.sidebar.text_input(
            "Chat model", value=os.getenv("OLLAMA_MODEL", "llama3")
        )
        config["ollama_embedding_model"] = st.sidebar.text_input(
            "Embedding model", value=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        )

    return provider, config


def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_excel(file):
    # Read every sheet and flatten it to plain text (CSV-style) so it can be
    # chunked and embedded the same way PDF text is.
    sheets = pd.read_excel(file, sheet_name=None, engine="openpyxl")
    text = ""
    for sheet_name, df in sheets.items():
        text += f"\nSheet: {sheet_name}\n"
        text += df.to_csv(index=False)
    return text


def get_chunk_config(text_length):
    # Scale chunk size/overlap up for larger documents (e.g. big spreadsheets
    # or multi-page PDFs) so more surrounding context (like column headers or
    # neighboring rows) survives each chunk boundary. Small docs keep the
    # original tight defaults, which are cheaper/faster to embed.
    if text_length > 100_000:
        return 2000, 400
    elif text_length > 20_000:
        return 1500, 300
    return 1000, 200


def main():
    """Entry point for the Streamlit application."""

    # Load environment variables – expects provider credentials in a .env file
    load_dotenv()

    # ── Streamlit page setup ────────────────────────────────────────────
    st.set_page_config(page_title="Ask your PDF")
    st.header("Ask your PDF or Excel file 💬")

    provider, provider_config = render_provider_sidebar()

    # ── Step 1: file upload ─────────────────────────────────────────────
    uploaded_file = st.file_uploader("Upload your PDF or Excel file", type=["pdf", "xlsx"])

    if uploaded_file is not None:
        # ── Step 2: extract text ────────────────────────────────────────
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif file_name.endswith(".xlsx"):
            text = extract_text_from_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a PDF or an .xlsx file.")
            return

        if not text.strip():
            st.warning("No extractable text found in this file.")
            return

        try:
            llm, embeddings = build_llm_and_embeddings(provider, provider_config)
        except Exception as exc:
            st.error(f"Could not initialize {provider}: {exc}")
            return

        # ── Step 3: split text into overlapping chunks ──────────────────
        # Overlap ensures that context at chunk boundaries is preserved;
        # larger files get bigger chunks with proportionally more overlap.
        chunk_size, chunk_overlap = get_chunk_config(len(text))
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)

        # ── Step 4: embed chunks & build a FAISS vector index ───────────
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        # ── Step 5: accept the user's question ──────────────────────────
        user_question = st.text_input("Ask a question about your file:")
        if user_question:
            # Retrieve the most semantically relevant chunks
            docs = knowledge_base.similarity_search(user_question)

            # ── Step 6: run the QA chain ────────────────────────────────
            chain = load_qa_chain(llm, chain_type="stuff")

            # Track token usage / cost with the OpenAI callback -- this only
            # populates for OpenAI/Azure OpenAI responses; Ollama responses
            # don't carry OpenAI-shaped usage metadata, so it prints zero
            # (harmless, not a bug).
            with get_openai_callback() as cb:
                response = chain.invoke({"input_documents": docs, "question": user_question})
                print(cb)  # log token usage to the console

            # Display the model's answer
            st.write(response["output_text"])


if __name__ == "__main__":
    main()
