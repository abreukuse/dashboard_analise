mkdir -p ~/.streamlit/
echo "[theme]
base="light"
primaryColor=’#1fa8a9’
secondaryBackgroundColor=’#f0f6f6’
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml

