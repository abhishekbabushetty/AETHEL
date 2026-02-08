import streamlit as st
import logging
import logging.config
import yaml
from pathlib import Path
from core.config import settings

# Setup Logging
def setup_logging():
    log_path = Path("meaning_engine/logging.yaml")
    if log_path.exists():
        with open(log_path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        # Fallback if running from root
        logging.basicConfig(level=logging.INFO)

setup_logging()
logger = logging.getLogger("meaning_engine")

st.set_page_config(page_title="Meaning Engine", page_icon="🧠", layout="wide")

st.title("🧠 Meaning Engine")
st.markdown("**Universal Semantic Layer** | _Preserving Knowledge, Not Compressing It_")

st.sidebar.header("System Status")
st.sidebar.success(f"System: {settings.SYSTEM_NAME}")
st.sidebar.info(f"Version: {settings.VERSION}")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ingestion Mode", "Universal")
with col2:
    st.metric("Chunking Strategy", "Hierarchical")
with col3:
    st.metric("Memory backend", "Qdrant Vector DB")

st.markdown("---")
st.write("### 🚀 Phase 1: Ingestion Test")

# --- Interactive Testing Layer ---
uploaded_file = st.file_uploader("Upload any file (PDF, Image, Audio)", type=["pdf", "png", "jpg", "mp3", "mp4"])

if uploaded_file:
    with st.status("Processing...", expanded=True) as status:
        # 1. Save temp file
        temp_dir = Path("input")
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        status.write(f"Saved to {temp_path}")
        
        # 2. Init Pipeline Components
        from core.ingestion.loader import UniversalLoader
        from core.processing.cleaner import TextCleaner
        from core.processing.chunker import HierarchicalChunker
        from core.embeddings.embedder import Embedder
        from core.embeddings.vector_store import VectorStore
        
        loader = UniversalLoader()
        cleaner = TextCleaner()
        chunker = HierarchicalChunker()
        # Initialize Embedder/VectorStore inside try block in case containers aren't ready
        
        # 3. Stream & Display
        st.subheader("Processing Pipeline")
        
        all_chunks = []
        
        try:
            embedder = Embedder()
            vector_store = VectorStore()
            
            for chunk in loader.load(temp_path):
                # A. Clean
                clean_chunk = cleaner.process_chunk(chunk)
                
                # B. Chunk (Hierarchy)
                hierarchical_chunks = chunker.chunk(clean_chunk)
                all_chunks.extend(hierarchical_chunks)
            
            # C. Embed & Index (Batch Process for speed)
            if all_chunks:
                with st.spinner(f"Embedding {len(all_chunks)} chunks..."):
                    texts = [c["content"] for c in all_chunks]
                    vectors = embedder.embed(texts)
                    
                    vector_store.upsert(all_chunks, vectors)
                    
                st.success(f"Indexed {len(all_chunks)} chunks to Memory!")
            
            status.update(label="Processing Complete!", state="complete", expanded=False)
            
            # --- Visualization ---
            tab1, tab2, tab3 = st.tabs(["🔬 Micro (Embeddings)", "📖 Meso (Context)", "🧠 Search Test"])
            
            with tab1:
                st.caption(f"Micro Chunks (< {settings.CHUNK_MICRO} chars)")
                micros = [c for c in all_chunks if c['level'] == 'micro']
                for c in micros[:10]: # Limit display
                    st.info(f"**{c['chunk_id']}**: {c['content']}")
            
            with tab2:
                st.caption(f"Meso Chunks (Sections)")
                mesos = [c for c in all_chunks if c['level'] == 'meso']
                for c in mesos[:5]:
                    with st.expander(c['chunk_id']):
                        st.write(c['content'])
            
            with tab3:
                st.write("Test your RAG memory immediately.")
                query = st.text_input("Ask a question about this doc:")
                if query:
                    q_vec = embedder.embed([query])[0]
                    results = vector_store.search(q_vec, limit=3)
                    for res in results:
                        st.success(f"Score: {res['score']:.2f}")
                        st.markdown(f"> {res['content']}")

        except Exception as e:
            st.error(f"Pipeline Error: {e}")
            logger.error(e)
            
        except Exception as e:
            st.error(f"Pipeline Error: {e}")
            logger.error(e)
