import streamlit as st
import requests
import configparser
import logging
from logging.handlers import RotatingFileHandler

# Setup logging for Streamlit (same as before)
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    # File handler with rotation (max 1MB per file, keeps 3 backups)
    handler = RotatingFileHandler('streamlit_script.log', maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(handler)

# Load configuration settings from a file
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Fetch data from a public API
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return []

# Filter and log titles containing any of the specified keywords or all titles if no keywords are provided
def filter_and_log_titles(data, keywords):
    filtered_titles = []
    type_counts = {"string": 0, "integer": 0, "other": 0}  # Track type counts

    for item in data:
        title = item.get('title', '')  # Use .get() to avoid KeyError
        if not keywords or any(keyword in title for keyword in keywords):
            filtered_titles.append(title)
            title_type = check_type(title)
            
            # Increment the corresponding type count
            if title_type in type_counts:
                type_counts[title_type] += 1
            
            # Log each matching title
            logging.info(f"Filtered Title: '{title}' (Type: {title_type})")
    
    # Log the counts of each type
    logging.info(f"Type Counts: Strings={type_counts['string']}, Integers={type_counts['integer']}, Others={type_counts['other']}")
    
    return filtered_titles, type_counts

# Check the type of an item and return whether it is an integer
def check_type(item):
    if isinstance(item, str):
        return "string"
    elif isinstance(item, int):
        return "integer"
    else:
        return "other"

# Streamlit interface for the app
def main():
    setup_logging()  # Initialize logging

    st.title("API Data Fetch and Filter")
    
    # Load configuration
    config_file = "dev.conf"
    config = load_config(config_file)

    # Fetch configurations
    url = config.get("api", "url")
    keywords = config.get("filter", "keywords").split(",")
    keywords = [kw.strip() for kw in keywords if kw.strip()]  # Clean up whitespace and remove empty strings

    # Input for custom keywords
    custom_keywords = st.text_input("Enter keywords (comma-separated):", value=", ".join(keywords))
    keywords = [kw.strip() for kw in custom_keywords.split(",") if kw.strip()]

    # Button to trigger data fetching
    if st.button('Fetch Data'):
        # Fetch data from the API
        st.info(f"Fetching data from URL: {url}")
        data = fetch_data(url)

        if not data:
            st.error("No data retrieved.")
            return
        
        if not keywords:
            st.info("No valid keywords provided. Fetching all titles.")

        # Process data with filtering and logging
        filtered_titles, type_counts = filter_and_log_titles(data, keywords)

        # Display filtered titles
        if filtered_titles:
            st.write(f"Found {len(filtered_titles)} filtered titles:")
            for title in filtered_titles:
                title_type = check_type(title)
                st.write(f"- {title} (Type: {title_type})")
        else:
            st.write("No titles found.")
        
        # Display type counts
        st.write(f"Type Counts: Strings={type_counts['string']}, Integers={type_counts['integer']}, Others={type_counts['other']}")

if __name__ == "__main__":
    main()
