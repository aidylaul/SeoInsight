"""
SEO Analysis Engine
Core functionality for analyzing website SEO tags and generating feedback
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List


def normalize_url(url: str) -> str:
    """Normalize URL by adding protocol if missing"""
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url


def get_url_variations(url: str) -> List[str]:
    """Get URL variations for flexible matching"""
    normalized = normalize_url(url)
    variations = [
        url,  # Original
        normalized,  # With protocol
        url.replace('https://', '').replace('http://', '') if url.startswith(('http://', 'https://')) else url
    ]
    # Remove duplicates while preserving order
    return list(dict.fromkeys(variations))


class SEOAnalyzer:
    """Main class for analyzing SEO tags and generating feedback"""
    
    def __init__(self):
        self.soup = None
        self.url = None
        self.seo_data = {}
        
    def fetch_html(self, url: str) -> bool:
        """Fetch HTML content from the given URL"""
        try:
            # Normalize URL
            url = normalize_url(url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.soup = BeautifulSoup(response.content, 'html.parser')
            self.url = url
            return True
            
        except requests.RequestException as e:
            raise Exception(f"Network error while fetching {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to analyze {url}: {str(e)}")
    
    def extract_seo_tags(self) -> Dict:
        """Extract all relevant SEO tags from the HTML"""
        if not self.soup:
            return {}
        
        seo_data = {
            'url': self.url,
            'title': '',
            'meta_description': '',
            'meta_keywords': '',
            'og_tags': {},
            'twitter_tags': {},
            'h1_tags': [],
            'canonical': ''
        }
        
        # Extract title
        title_tag = self.soup.find('title')
        if title_tag:
            seo_data['title'] = title_tag.get_text().strip()
        
        # Extract meta tags
        meta_tags = self.soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                seo_data['meta_description'] = content
            elif name == 'keywords':
                seo_data['meta_keywords'] = content
            elif property_attr.startswith('og:'):
                seo_data['og_tags'][property_attr] = content
            elif name.startswith('twitter:'):
                seo_data['twitter_tags'][name] = content
        
        # Extract H1 tags
        h1_tags = self.soup.find_all('h1')
        seo_data['h1_tags'] = [h1.get_text().strip() for h1 in h1_tags]
        
        # Extract canonical URL
        canonical = self.soup.find('link', rel='canonical')
        if canonical:
            seo_data['canonical'] = canonical.get('href', '')
        
        self.seo_data = seo_data
        return seo_data
    
    def analyze_seo_quality(self) -> Dict:
        """Analyze SEO quality and provide feedback"""
        analysis = {
            'title': {'status': 'error', 'message': '', 'score': 0},
            'description': {'status': 'error', 'message': '', 'score': 0},
            'og_tags': {'status': 'error', 'message': '', 'score': 0},
            'twitter_tags': {'status': 'error', 'message': '', 'score': 0},
            'h1_structure': {'status': 'error', 'message': '', 'score': 0}
        }
        
        # Analyze title
        title = self.seo_data.get('title', '')
        if not title:
            analysis['title'] = {'status': 'error', 'message': 'Missing title tag', 'score': 0}
        elif len(title) < 30:
            analysis['title'] = {'status': 'warning', 'message': f'Title too short ({len(title)} chars). Optimal: 50-60 chars', 'score': 10}
        elif len(title) > 60:
            analysis['title'] = {'status': 'warning', 'message': f'Title too long ({len(title)} chars). Optimal: 50-60 chars', 'score': 15}
        else:
            analysis['title'] = {'status': 'success', 'message': f'Title length optimal ({len(title)} chars)', 'score': 20}
        
        # Analyze meta description
        description = self.seo_data.get('meta_description', '')
        if not description:
            analysis['description'] = {'status': 'error', 'message': 'Missing meta description', 'score': 0}
        elif len(description) < 120:
            analysis['description'] = {'status': 'warning', 'message': f'Description too short ({len(description)} chars). Optimal: 150-160 chars', 'score': 10}
        elif len(description) > 160:
            analysis['description'] = {'status': 'warning', 'message': f'Description too long ({len(description)} chars). Optimal: 150-160 chars', 'score': 15}
        else:
            analysis['description'] = {'status': 'success', 'message': f'Description length optimal ({len(description)} chars)', 'score': 20}
        
        # Analyze Open Graph tags
        og_tags = self.seo_data.get('og_tags', {})
        required_og = ['og:title', 'og:description', 'og:type', 'og:url']
        missing_og = [tag for tag in required_og if tag not in og_tags]
        
        if not og_tags:
            analysis['og_tags'] = {'status': 'error', 'message': 'No Open Graph tags found', 'score': 0}
        elif missing_og:
            analysis['og_tags'] = {'status': 'warning', 'message': f'Missing OG tags: {", ".join(missing_og)}', 'score': 10}
        else:
            analysis['og_tags'] = {'status': 'success', 'message': 'All essential Open Graph tags present', 'score': 20}
        
        # Analyze Twitter tags
        twitter_tags = self.seo_data.get('twitter_tags', {})
        required_twitter = ['twitter:card', 'twitter:title', 'twitter:description']
        missing_twitter = [tag for tag in required_twitter if tag not in twitter_tags]
        
        if not twitter_tags:
            analysis['twitter_tags'] = {'status': 'error', 'message': 'No Twitter Card tags found', 'score': 0}
        elif missing_twitter:
            analysis['twitter_tags'] = {'status': 'warning', 'message': f'Missing Twitter tags: {", ".join(missing_twitter)}', 'score': 10}
        else:
            analysis['twitter_tags'] = {'status': 'success', 'message': 'All essential Twitter Card tags present', 'score': 20}
        
        # Analyze H1 structure
        h1_tags = self.seo_data.get('h1_tags', [])
        if not h1_tags:
            analysis['h1_structure'] = {'status': 'error', 'message': 'No H1 tag found', 'score': 0}
        elif len(h1_tags) > 1:
            analysis['h1_structure'] = {'status': 'warning', 'message': f'Multiple H1 tags found ({len(h1_tags)}). Should have only one', 'score': 10}
        else:
            analysis['h1_structure'] = {'status': 'success', 'message': 'Single H1 tag found (optimal)', 'score': 20}
        
        return analysis
    
    def calculate_seo_score(self, analysis: Dict) -> int:
        """Calculate total SEO score out of 100"""
        total_score = sum(item['score'] for item in analysis.values())
        return total_score
    
    def get_preview_data(self) -> Dict:
        """Get data for generating previews"""
        og_tags = self.seo_data.get('og_tags', {})
        twitter_tags = self.seo_data.get('twitter_tags', {})
        
        # Fallback hierarchy: OG tags -> Twitter tags -> meta tags -> title tag
        title = (og_tags.get('og:title') or 
                twitter_tags.get('twitter:title') or 
                self.seo_data.get('title', ''))
        
        description = (og_tags.get('og:description') or 
                      twitter_tags.get('twitter:description') or 
                      self.seo_data.get('meta_description', ''))
        
        image = og_tags.get('og:image') or twitter_tags.get('twitter:image', '')
        
        return {
            'title': title,
            'description': description,
            'image': image,
            'url': self.url,
            'domain': urlparse(self.url).netloc if self.url else ''
        }