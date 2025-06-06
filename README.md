# 📊 Free Forever Excel AI Refiner

A privacy-focused Streamlit app that cleans/transforms Excel files using **local AI (Ollama)** or basic Pandas operations.

![Demo](https://via.placeholder.com/800x400?text=Excel+AI+Refiner+Demo) *(Replace with actual screenshot later)*

## 🌟 Features
- **No Cloud Costs** - Uses local AI via Ollama
- **Privacy First** - Data never leaves your computer
- **Fallback Mode** - Works with just Pandas if no AI available
- **Supports**:
  - Remove empty rows
  - Text normalization (uppercase, etc.)
  - Basic data summaries
  - Custom AI transformations (if Ollama installed)

## 🛠️ Installation

### 1. Install Ollama (For AI Features)
```bash
# On macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows (Powershell)
irm https://ollama.ai/install.sh | iex
## 🎨 Customizing Colors

If colors don't appear:
1. Edit `.streamlit/config.toml`
2. Use **uppercase** hex codes (e.g., `#FF0000` instead of `#ff0000`)
3. Restart Streamlit with:
   ```bash
   streamlit run app.py --server.enableCORS=false
   
---

### **💡 Pro Tip: Validate Your Config**
Add this to `app.py` to debug:
```python
import streamlit as st

# Display active config (debug)
st.write("Current theme config:", st.get_theme())