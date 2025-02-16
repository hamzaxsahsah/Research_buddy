# Research Paper Scraper

## Overview
The **ResearchScraper** is a Python-based tool designed to fetch research papers from multiple sources, including:

- **Semantic Scholar**
- **arXiv**
- (Optional) **Core.ac.uk** (Requires API Key)

The scraper allows users to search for academic papers using specific keywords, filter relevant results, and save them in multiple formats (CSV, Excel, JSON).

## Features
- **Automated Research Paper Retrieval**: Fetches papers based on a given query.
- **Multi-Source Integration**: Gathers data from multiple APIs.
- **Filtering Mechanism**: Filters results based on relevant keywords.
- **Data Export**: Saves results in CSV, Excel, and JSON formats.
- **Logging System**: Provides debug logs for tracking progress and issues.

## Prerequisites
### Required Libraries
Ensure you have the following Python libraries installed:
```bash
pip install requests pandas beautifulsoup4 openpyxl
```

### API Keys (If Using Core.ac.uk)
- Register for an API key at [Core.ac.uk](https://core.ac.uk/).
- Uncomment and set `self.core_api_key` in the script.

## Usage
### Running the Scraper
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/research-scraper.git
   cd research-scraper
   ```
2. Run the script:
   ```bash
   python research_scraper.py
   ```

### Modifying the Search Query
Edit the `main()` function in the script:
```python
search_query = "blockchain artificial intelligence smart contracts autonomous systems"
keywords = ['blockchain', 'artificial intelligence', 'AI', 'smart contracts', 'autonomous systems']
```
Modify the `search_query` and `keywords` list as needed.

## Output
- **Saved Files**: The results are saved in `research_papers/` with timestamped filenames.
- **Summary Report**: A text file summarizing the fetched research papers.

## Future Enhancements
- Add support for more research paper sources.
- Implement additional filtering and ranking mechanisms.
- Enhance error handling and API rate limit management.

## License
This project is licensed under the MIT License.

