mkdir -p ~/.streamlit/

echo "[theme]
base='light'
primaryColor = '#33ecf6'
backgroundColor = ‘#EFEDE8’
secondaryBackgroundColor = '#f0f6f6'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml