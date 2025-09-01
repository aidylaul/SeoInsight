"""
SEO Tag Visualizer - Main Application
Streamlit web application for analyzing website SEO tags
"""

import streamlit as st
from seo_analyzer import SEOAnalyzer
from database import DatabaseManager
from ui_components import (
    display_seo_tags, display_google_preview, display_social_preview,
    display_seo_score, display_analysis_history, display_interactive_preview_editing
)

# Page configuration
st.set_page_config(
    page_title="SEO Tag Visualizer",
    page_icon="🔍",
    layout="wide"
)

# Health check endpoint for Render
@st.fragment
def healthcheck():
    if st.query_params.get("health") == "check":
        st.write("OK")
        st.stop()

healthcheck()


def main():
    """Main Streamlit application"""
    st.title("🔍 SEO Tag Visualizer")
    st.write("Analyze any website's SEO tags and get actionable feedback to improve search engine visibility.")
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SEOAnalyzer()
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    # Clean up old cached data if needed
    def cleanup_cache():
        """Remove old cached analysis data"""
        cache_keys = ['cached_analysis', 'cached_score', 'cached_preview', 'cached_url']
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    # URL input section
    st.subheader("Website Analysis")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Check if we need to pre-fill URL from history
        default_url = ""
        if 'rerun_url' in st.session_state:
            default_url = st.session_state.rerun_url
            del st.session_state.rerun_url
        
        url = st.text_input(
            "Enter Website URL:",
            value=default_url,
            placeholder="https://example.com",
            help="Enter the full URL of the website you want to analyze"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Analysis section
    if analyze_button and url:
        with st.spinner("Fetching and analyzing website..."):
            try:
                # Clear old cache before new analysis
                cleanup_cache()
                
                if st.session_state.analyzer.fetch_html(url):
                    seo_data = st.session_state.analyzer.extract_seo_tags()
                    analysis = st.session_state.analyzer.analyze_seo_quality()
                    score = st.session_state.analyzer.calculate_seo_score(analysis)
                    
                    # Save to database
                    if st.session_state.db_manager.save_analysis(seo_data, analysis, score):
                        st.success("✅ Analysis saved to database!")
                    
                    st.session_state.analyzed = True
                    st.rerun()
            except Exception as e:
                st.error(str(e))
    
    # Display results if analysis is complete
    if st.session_state.analyzed and st.session_state.analyzer.seo_data:
        seo_data = st.session_state.analyzer.seo_data
        
        # Cache analysis results to avoid redundant calculations
        if 'cached_analysis' not in st.session_state or st.session_state.cached_url != st.session_state.analyzer.url:
            st.session_state.cached_analysis = st.session_state.analyzer.analyze_seo_quality()
            st.session_state.cached_score = st.session_state.analyzer.calculate_seo_score(st.session_state.cached_analysis)
            st.session_state.cached_preview = st.session_state.analyzer.get_preview_data()
            st.session_state.cached_url = st.session_state.analyzer.url
        
        analysis = st.session_state.cached_analysis
        score = st.session_state.cached_score
        preview_data = st.session_state.cached_preview
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 SEO Tags", "📊 SEO Score", "🔍 Google Preview", "📱 Social Preview", "📊 History"])
        
        with tab1:
            display_seo_tags(seo_data, analysis)
        
        with tab2:
            col1, col2 = st.columns([1, 2])
            with col1:
                display_seo_score(score)
            with col2:
                st.subheader("Score Breakdown")
                for category, details in analysis.items():
                    icon = "✅" if details['status'] == 'success' else "⚠️" if details['status'] == 'warning' else "❌"
                    st.write(f"{icon} **{category.replace('_', ' ').title()}**: {details['score']}/20")
                    st.caption(details['message'])
        
        with tab3:
            display_google_preview(preview_data)
            display_interactive_preview_editing(preview_data, "google")
        
        with tab4:
            display_social_preview(preview_data)
            display_interactive_preview_editing(preview_data, "social")
        
        with tab5:
            display_analysis_history(st.session_state.db_manager)
    
    # Instructions and tips
    if not st.session_state.analyzed:
        st.subheader("How it works")
        st.write("""
        1. **Enter a URL** - Input any website URL you want to analyze
        2. **Get Analysis** - The tool fetches the HTML and extracts SEO tags
        3. **Review Results** - See what's working and what needs improvement
        4. **View Previews** - See how your site appears in search results and social media
        5. **Get Score** - Receive an overall SEO score out of 100
        """)
        
        st.subheader("What we analyze")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("""
            **SEO Elements:**
            - Title tag length (50-60 chars optimal)
            - Meta description (150-160 chars optimal)
            - Meta keywords presence
            - H1 tag structure (single H1 recommended)
            - Canonical URL
            """)
        
        with col2:
            st.write("""
            **Social Media Tags:**
            - Open Graph tags (Facebook, LinkedIn)
            - Twitter Card tags
            - Social media image tags
            - Preview generation for all platforms
            """)


if __name__ == "__main__":
    main()