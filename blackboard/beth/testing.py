import time
import chromadb.utils.embedding_functions as embedding_functions

ef = embedding_functions.InstructorEmbeddingFunction(
    model_name="hkunlp/instructor-xl", 
    device="cuda"
)

docs = []
for i in range(1000):
    docs.append(f"this is a document with id {i}")

start_time = time.perf_counter()
embeddings = ef(docs)
end_time = time.perf_counter()
print(f"Elapsed time: {end_time - start_time} seconds")