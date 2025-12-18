import weaviate
import os
import re
import weaviate.classes as wvc
from dotenv import load_dotenv
from src.enrichment import ContentEnricher

load_dotenv()

# --- HELPER FUNCTIONS ---
def get_sentences(text):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text_semantic(text, min_chars=800, max_chars=1500):
    if not text: return []
    
    print('TOTAL NUMBER OF CHARS: ', len(text))

    raw_paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks_data = []
    current_block = []
    current_char_count = 0
    
    # Phase 1: Group
    for i, para in enumerate(raw_paragraphs):
        para_len = len(para)
        if current_block and (current_char_count + para_len > max_chars):
            chunks_data.append({
                "paragraphs": current_block,
                "start_idx": i - len(current_block),
                "end_idx": i - 1
            })
            current_block = [para]
            current_char_count = para_len
        else:
            current_block.append(para)
            current_char_count += para_len

    if current_block:
         chunks_data.append({
                "paragraphs": current_block,
                "start_idx": len(raw_paragraphs) - len(current_block),
                "end_idx": len(raw_paragraphs) - 1
            })

    # Phase 2: Context
    final_chunks = []
    for data in chunks_data:
        block_text = "\n\n".join(data["paragraphs"])
        
        pre_context = ""
        if data["start_idx"] > 0:
            prev_para = raw_paragraphs[data["start_idx"] - 1]
            sentences = get_sentences(prev_para)
            if sentences: pre_context = f"[Context: ...{sentences[-1]}]"

        post_context = ""
        if data["end_idx"] < len(raw_paragraphs) - 1:
            next_para = raw_paragraphs[data["end_idx"] + 1]
            sentences = get_sentences(next_para)
            if sentences: post_context = f"[Context: {sentences[0]}...]"

        full_chunk = block_text
        if pre_context: full_chunk = f"{pre_context}\n\n{full_chunk}"
        if post_context: full_chunk = f"{full_chunk}\n\n{post_context}"
            
        final_chunks.append(full_chunk)

    return final_chunks

# --- MAIN ---
def ingest_data():
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    
    client = weaviate.connect_to_local(
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
    )
    enricher = ContentEnricher()
    total_cost = 0.0
    collection_name = "EQxReport"

    try:
        # 1. Reset & Create Schema (UPDATED)
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
        
        client.collections.create(
            name=collection_name,
            # Note: Weaviate v4 handles vectorizer config slightly differently now, 
            # but usually 'vectorizer_config' still works with warnings. 
            # If strictly v4, we often use 'vectorizer_config' argument with Configure.Vectorizer...
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            
            properties=[
                wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="summary", data_type=wvc.config.DataType.TEXT),
                
                # --- UPDATED METADATA SCHEMA ---
                wvc.config.Property(name="country", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="iso_code", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="region", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="income_group", data_type=wvc.config.DataType.TEXT), # New
                
                wvc.config.Property(name="eqx_rank", data_type=wvc.config.DataType.INT),
                wvc.config.Property(name="eqx_year", data_type=wvc.config.DataType.INT),      # New
                
                wvc.config.Property(name="themes", data_type=wvc.config.DataType.TEXT_ARRAY),
                wvc.config.Property(name="other_countries_mentioned", data_type=wvc.config.DataType.TEXT_ARRAY), # New
                
                wvc.config.Property(name="chunk_index", data_type=wvc.config.DataType.INT),
                wvc.config.Property(name="total_chunks", data_type=wvc.config.DataType.INT),
            ]
        )

        # 2. Process Files
        data_dir = "data"
        collection = client.collections.get(collection_name)
        
        for filename in os.listdir(data_dir):
            if not filename.endswith(".txt") or filename == "summary.txt":
                continue 

            print(f"\n--- Processing {filename} ---")
            with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()

            # Metadata
            metadata, meta_stats = enricher.extract_metadata(content)
            summary, sum_stats = enricher.generate_summary(content)
            total_cost += (meta_stats.get('cost',0) + sum_stats.get('cost',0))
            
            # Chunking
            chunks = chunk_text_semantic(content, min_chars=200, max_chars=500)
            total_chunks = len(chunks)
            print(f"  > Generated {total_chunks} chunks.")

            # Upload
            if not debug_mode:
                with collection.batch.dynamic() as batch:
                    for i, chunk in enumerate(chunks):
                        batch.add_object(
                            properties={
                                "text": chunk,
                                "summary": summary,
                                
                                # --- MAPPING NEW FIELDS ---
                                "country": metadata.country,
                                "iso_code": metadata.iso_code,
                                "region": metadata.region,
                                "income_group": metadata.income_group, # New
                                
                                "eqx_rank": metadata.eqx_rank,
                                "eqx_year": metadata.eqx_year,         # New
                                
                                "themes": metadata.themes,
                                "other_countries_mentioned": metadata.other_countries_mentioned, # New
                                
                                "chunk_index": i,
                                "total_chunks": total_chunks,
                            }
                        )
                print(f"  > Uploaded {total_chunks} objects.")
            else:
                print("  > [DEBUG] Skipping Upload.")

        print(f"\nTotal Cost: ${total_cost:.4f}")

    finally:
        client.close()

if __name__ == "__main__":
    ingest_data()