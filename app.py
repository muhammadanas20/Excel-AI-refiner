import streamlit as st
import pandas as pd
import subprocess
import sys
from io import BytesIO
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Config ---
st.set_page_config(
    page_title="📊 Free Excel AI Refiner",
    page_icon="📊",
    layout="wide",
)

# --- Debugging Setup ---
def log_error(error, context=""):
    """Log errors with context for debugging."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    st.error(f"⚠️ Error: {str(error)}")

# --- Check Ollama Installation ---
def is_ollama_installed():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "version" in result.stdout.lower()
    except Exception as e:
        log_error(e, "checking Ollama installation")
        return False

# --- Local AI Processing (Ollama) ---
@lru_cache(maxsize=10)  # Cache responses to avoid repeated calls
def query_ollama(prompt: str, data: str, model: str = "llama2") -> str:
    """Query a local Ollama model for data processing."""
    try:
        cmd = [
            "ollama", "run", model,
            f"Data:\n{data}\n\nInstruction:\n{prompt}\nRespond in CSV format only."
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # Give enough time for response
        )
        if result.returncode != 0:
            raise RuntimeError(f"Ollama error: {result.stderr}")
        return result.stdout
    except Exception as e:
        log_error(e, "querying Ollama")
        raise

# --- Pandas Fallback (No AI) ---
def pandas_fallback(df: pd.DataFrame, prompt: str) -> pd.DataFrame:
    """Basic data transformations if AI fails."""
    try:
        if "remove empty" in prompt.lower():
            return df.dropna()
        elif "summarize" in prompt.lower():
            return df.describe()
        elif "uppercase" in prompt.lower():
            return df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
        else:
            return df  # Default: return original data
    except Exception as e:
        log_error(e, "pandas fallback")
        return df

# --- Main App Logic ---
def main():
    st.title("📊 Free Forever Excel AI Refiner")
    st.markdown("Clean and transform Excel files using **local AI** (Ollama) or basic Pandas.")

    # --- File Upload ---
    uploaded_file = st.file_uploader(
        "Upload Excel File (XLSX)",
        type=["xlsx", "xls"],
        help="Supports .xlsx and .xls files",
    )

    # --- AI / Manual Mode Toggle ---
    use_ai = st.checkbox(
        "Enable AI Processing (Requires Ollama)",
        value=False,
        help="Uncheck to use basic Pandas functions only",
    )

    # --- User Instructions ---
    prompt = st.text_area(
        "What should AI do with your data?",
        placeholder="Example: 'Remove empty rows', 'Convert names to uppercase', 'Summarize sales data'",
        height=100,
    )

    if uploaded_file and prompt:
        try:
            # --- Read Excel File ---
            df = pd.read_excel(uploaded_file)
            if df.empty:
                st.warning("Uploaded file is empty!")
                return

            # --- Process Data ---
            with st.spinner("Processing data..."):
                if use_ai and is_ollama_installed():
                    st.info("Using **Ollama AI** for processing...")
                    raw_data = df.to_csv(index=False)
                    ai_response = query_ollama(prompt, raw_data)
                    
                    try:
                        # Parse AI response as CSV
                        processed_df = pd.read_csv(BytesIO(ai_response.encode()))
                        st.success("✅ AI Processing Complete!")
                    except Exception as e:
                        log_error(e, "parsing AI response")
                        st.warning("AI response was not valid CSV. Falling back to Pandas.")
                        processed_df = pandas_fallback(df, prompt)
                else:
                    st.info("Using **Pandas** for basic transformations...")
                    processed_df = pandas_fallback(df, prompt)

            # --- Display Results ---
            st.subheader("Processed Data")
            st.dataframe(processed_df)

            # --- Download Button ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                processed_df.to_excel(writer, index=False)
            st.download_button(
                "📥 Download Processed Excel",
                data=output.getvalue(),
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            log_error(e, "main processing")
            st.error("Failed to process data. Check logs for details.")

# --- Run App ---
if __name__ == "__main__":
    main()