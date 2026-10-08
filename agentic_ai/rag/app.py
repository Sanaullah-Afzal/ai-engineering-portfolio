from src.trag.data_loader import load_all_documents
from src.trag.vector_store import FaissVectorStore
from src.trag.search import RAGSearch

if __name__ == "__main__":
    # docs = load_all_documents("data") # data is directiry name

    vector_store = FaissVectorStore("faiss_store") # path name
    # vector_store.build_from_documents(docs)
    # we do not nned to build it every time, once we have it we can just load them
    vector_store.load()
    # print(vector_store.query("What skill set Sanaullah have", top_k=3))


    rag_search = RAGSearch()
    query = "What is his experience in Huawei?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)