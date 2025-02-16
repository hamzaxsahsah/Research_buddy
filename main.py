import requests
import pandas as pd
import time
import random
from datetime import datetime
import os
import json
from urllib.parse import quote

class ResearchScraper:
    def __init__(self, debug=True):
        self.debug = debug
        self.base_folder = "research_papers"
        self.create_folders()
        
        # Semantic Scholar API endpoint
        self.semantic_scholar_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.semantic_scholar_headers = {
            'User-Agent': 'Research Project (your-email@domain.com)'
        }
        
        # arXiv API endpoint
        self.arxiv_url = "http://export.arxiv.org/api/query"
        
        # Core.ac.uk API endpoint (you'll need to register for an API key)
        self.core_url = "https://core.ac.uk/api-v2/search"
        # self.core_api_key = "YOUR_CORE_API_KEY"  # Uncomment and add your key
        
    def log(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def create_folders(self):
        folders = [
            self.base_folder,
            f"{self.base_folder}/semantic_scholar",
            f"{self.base_folder}/arxiv",
            f"{self.base_folder}/core"
        ]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def scrape_semantic_scholar(self, query, limit=100):
        """Scrape papers from Semantic Scholar API"""
        papers = []
        offset = 0
        page_size = 20
        
        while offset < limit:
            try:
                self.log(f"Querying Semantic Scholar (offset: {offset})")
                params = {
                    'query': query,
                    'limit': page_size,
                    'offset': offset,
                    'fields': 'title,authors,year,url,abstract,venue'
                }
                
                response = requests.get(
                    self.semantic_scholar_url,
                    headers=self.semantic_scholar_headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        for paper in data['data']:
                            papers.append({
                                'title': paper.get('title', ''),
                                'authors': ', '.join([author.get('name', '') for author in paper.get('authors', [])]),
                                'year': paper.get('year', ''),
                                'url': paper.get('url', ''),
                                'abstract': paper.get('abstract', ''),
                                'venue': paper.get('venue', ''),
                                'source': 'Semantic Scholar'
                            })
                    
                    if len(data.get('data', [])) < page_size:
                        break
                else:
                    self.log(f"Error: Semantic Scholar API returned status {response.status_code}")
                    break
                
                offset += page_size
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                self.log(f"Error querying Semantic Scholar: {str(e)}")
                break
        
        return pd.DataFrame(papers)

    def scrape_arxiv(self, query, max_results=100):
        """Scrape papers from arXiv API"""
        papers = []
        
        try:
            self.log(f"Querying arXiv")
            params = {
                'search_query': f'all:{quote(query)}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'lastUpdatedDate',
                'sortOrder': 'descending'
            }
            
            response = requests.get(self.arxiv_url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'xml')
                entries = soup.find_all('entry')
                
                for entry in entries:
                    papers.append({
                        'title': entry.title.text.strip(),
                        'authors': ', '.join([author.find('name').text.strip() for author in entry.find_all('author')]),
                        'year': entry.published.text[:4],
                        'url': entry.find('link', attrs={'type': 'text/html'})['href'],
                        'abstract': entry.summary.text.strip(),
                        'source': 'arXiv'
                    })
            else:
                self.log(f"Error: arXiv API returned status {response.status_code}")
                
        except Exception as e:
            self.log(f"Error querying arXiv: {str(e)}")
        
        return pd.DataFrame(papers)

    def filter_relevant_papers(self, df, keywords):
        """Filter papers based on relevant keywords"""
        if df.empty:
            return df
            
        pattern = '|'.join(map(str.lower, keywords))
        mask = (
            df['title'].str.lower().str.contains(pattern, na=False) |
            df['abstract'].str.lower().str.contains(pattern, na=False)
        )
        return df[mask]

    def save_results(self, df, filename):
        """Save results to multiple formats"""
        if df.empty:
            self.log("No results to save")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_path = f"{self.base_folder}/{filename}_{timestamp}"
        
        # Save as CSV
        df.to_csv(f"{base_path}.csv", index=False, encoding='utf-8')
        
        # Save as Excel
        df.to_excel(f"{base_path}.xlsx", index=False)
        
        # Save as JSON
        df.to_json(f"{base_path}.json", orient='records', indent=2)
        
        self.log(f"Results saved to {base_path}.[csv/xlsx/json]")
        
        # Generate summary report
        with open(f"{base_path}_summary.txt", 'w', encoding='utf-8') as f:
            f.write(f"Research Paper Summary\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total papers found: {len(df)}\n")
            f.write(f"Papers by source:\n")
            for source, count in df['source'].value_counts().items():
                f.write(f"- {source}: {count}\n")
            f.write(f"\nYears covered: {df['year'].min()} to {df['year'].max()}\n")

def main():
    scraper = ResearchScraper(debug=True)
    
    # Define search parameters
    search_query = "blockchain artificial intelligence smart contracts autonomous systems"
    keywords = [
        'blockchain', 'artificial intelligence', 'AI', 
        'smart contracts', 'autonomous systems'
    ]
    
    # Collect papers from different sources
    semantic_scholar_papers = scraper.scrape_semantic_scholar(search_query)
    print(f"Semantic Scholar papers found: {len(semantic_scholar_papers)}")
    
    arxiv_papers = scraper.scrape_arxiv(search_query)
    print(f"arXiv papers found: {len(arxiv_papers)}")
    
    # Combine all papers
    all_papers = pd.concat([semantic_scholar_papers, arxiv_papers], ignore_index=True)
    print(f"Total papers found: {len(all_papers)}")
    
    if not all_papers.empty:
        # Remove duplicates
        all_papers.drop_duplicates(subset=['title'], inplace=True)
        print(f"Papers after removing duplicates: {len(all_papers)}")
        
        # Filter relevant papers
        relevant_papers = scraper.filter_relevant_papers(all_papers, keywords)
        print(f"Relevant papers: {len(relevant_papers)}")
        
        # Save results
        scraper.save_results(relevant_papers, 'blockchain_ai_research')
    else:
        print("No papers found. Check debug logs for details.")

if __name__ == "__main__":
    main()