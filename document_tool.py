import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


load_dotenv()


DATA_DIR = Path(".")
VECTOR_DB_DIR = "chroma_db"


def load_pdfs():

    documents = []

    for pdf_file in DATA_DIR.glob("*.pdf"):

        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        filename = pdf_file.name.lower()

        # --------------------------------
        # Identify document type
        # --------------------------------

        if "northstar" in filename:

            source_type = "customer_agreement"

        
            customer = "Northstar Logistics"
            priority = 5

        elif "lumenworks" in filename:

            source_type = "customer_agreement"
            customer = "LumenWorks"
            priority = 5

        elif "deprecated" in filename:

            source_type = "deprecated_policy"
            customer = None
            priority = 1

        elif "cancellation" in filename:

            source_type = "current_sop"
            customer = None
            priority = 4

        elif "current" in filename:

            source_type = "current_policy"
            customer = None
            priority = 4

        elif "product" in filename:

            source_type = "product_documentation"
            customer = None
            priority = 3

        else:

            source_type = "unknown"
            customer = None
            priority = 0

        # --------------------------------
        # Add metadata to every page
        # --------------------------------

        for doc in docs:

            doc.metadata["source_file"] = pdf_file.name
            doc.metadata["source_type"] = source_type
            doc.metadata["customer"] = customer
            doc.metadata["priority"] = priority

            documents.append(doc)

    return documents


def create_vector_database():

    documents = load_pdfs()

    print(f"Loaded {len(documents)} PDF pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # Temporary check
    print("\nTEST METADATA:")
    print(chunks[0].metadata)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR,
        collection_name="parcelpilot_documents"
    )

    print("\nVector database created.")

    return vectorstore


def search_documents(query, k=8, user_role="support"):

    if user_role not in {"support", "manager"}:

        return []

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name="parcelpilot_documents"
    )

    results = vectorstore.similarity_search(
        query,
        k=k
    )
    priority_order = {
        "customer_agreement": 5,
        "current_sop": 4,
        "current_policy": 4,
        "product_documentation": 3,
        "deprecated_policy": 1,
        "unknown": 0
    }
    # Sort by authority
    # --------------------------------------------------

    results = sorted(
        results,
        key=lambda doc: priority_order.get(
            doc.metadata.get("source_type", "unknown"),
            0
        ),
        reverse=True
    )

    return results


if __name__ == "__main__":

    create_vector_database()