"""
UI Components for SEO Analyzer
Streamlit interface components for displaying analysis results
"""

import streamlit as st
from typing import Dict, Tuple
from urllib.parse import urlparse


def get_score_color_and_grade(score: int) -> Tuple[str, str]:
    """Get color and grade for SEO score"""
    if score >= 80:
        return "#4CAF50", "Excellent"
    elif score >= 60:
        return "#FF9800", "Good"
    elif score >= 40:
        return "#FF5722", "Needs Improvement"
    else:
        return "#F44336", "Poor"


def create_score_circle(score: int, size: int = 120, font_size: int = 36) -> str:
    """Create HTML for score circle display"""
    color, grade = get_score_color_and_grade(score)
    return f"""
    <div style="text-align: center; padding: 20px;">
        <div style="display: inline-block; width: {size}px; height: {size}px; border-radius: 50%; 
                    background-color: {color}; color: white; line-height: {size}px; 
                    font-size: {font_size}px; font-weight: bold; margin-bottom: 10px;">
            {score}
        </div>
        <div style="font-size: 18px; color: #333; margin-bottom: 5px;">
            <strong>{grade}</strong>
        </div>
        <div style="color: #666; font-size: 14px;">
            out of 100
        </div>
    </div>
    """


def display_status_icon(status: str) -> str:
    """Return appropriate emoji for status"""
    if status == 'success':
        return '✅'
    elif status == 'warning':
        return '⚠️'
    else:
        return '❌'


def display_seo_tags(seo_data: Dict, analysis: Dict):
    """Display SEO tags with status indicators"""
    st.subheader("SEO Tags Analysis")
    
    # Title
    st.write("**Title Tag**")
    status_icon = display_status_icon(analysis['title']['status'])
    if seo_data.get('title'):
        st.write(f"{status_icon} `<title>{seo_data['title']}</title>`")
    else:
        st.write(f"{status_icon} Missing title tag")
    st.caption(analysis['title']['message'])
    
    # Meta Description
    st.write("**Meta Description**")
    status_icon = display_status_icon(analysis['description']['status'])
    if seo_data.get('meta_description'):
        st.write(f"{status_icon} `<meta name=\"description\" content=\"{seo_data['meta_description']}\">`")
    else:
        st.write(f"{status_icon} Missing meta description")
    st.caption(analysis['description']['message'])
    
    # Meta Keywords
    st.write("**Meta Keywords**")
    if seo_data.get('meta_keywords'):
        st.write(f"✅ `<meta name=\"keywords\" content=\"{seo_data['meta_keywords']}\">`")
    else:
        st.write("⚠️ No meta keywords found")
    
    # Open Graph Tags
    st.write("**Open Graph Tags**")
    status_icon = display_status_icon(analysis['og_tags']['status'])
    og_tags = seo_data.get('og_tags', {})
    if og_tags:
        for prop, content in og_tags.items():
            st.write(f"{status_icon} `<meta property=\"{prop}\" content=\"{content}\">`")
    else:
        st.write(f"{status_icon} No Open Graph tags found")
    st.caption(analysis['og_tags']['message'])
    
    # Twitter Tags
    st.write("**Twitter Card Tags**")
    status_icon = display_status_icon(analysis['twitter_tags']['status'])
    twitter_tags = seo_data.get('twitter_tags', {})
    if twitter_tags:
        for name, content in twitter_tags.items():
            st.write(f"{status_icon} `<meta name=\"{name}\" content=\"{content}\">`")
    else:
        st.write(f"{status_icon} No Twitter Card tags found")
    st.caption(analysis['twitter_tags']['message'])
    
    # H1 Tags
    st.write("**H1 Structure**")
    status_icon = display_status_icon(analysis['h1_structure']['status'])
    h1_tags = seo_data.get('h1_tags', [])
    if h1_tags:
        for i, h1 in enumerate(h1_tags, 1):
            st.write(f"{status_icon} H1 #{i}: `<h1>{h1}</h1>`")
    else:
        st.write(f"{status_icon} No H1 tags found")
    st.caption(analysis['h1_structure']['message'])


def display_google_preview(preview_data: Dict):
    """Display Google search result preview"""
    st.subheader("Google Search Preview")
    
    with st.container():
        # Simulate Google search result appearance
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; padding: 16px; border-radius: 8px; background-color: white;">
            <div style="color: #1a0dab; font-size: 18px; line-height: 1.2; margin-bottom: 4px;">
                <strong>{preview_data['title'][:60]}{'...' if len(preview_data['title']) > 60 else ''}</strong>
            </div>
            <div style="color: #006621; font-size: 14px; margin-bottom: 4px;">
                {preview_data['url']}
            </div>
            <div style="color: #545454; font-size: 14px; line-height: 1.4;">
                {preview_data['description'][:160]}{'...' if len(preview_data['description']) > 160 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_social_preview(preview_data: Dict):
    """Display social media preview"""
    st.subheader("Social Media Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Facebook/LinkedIn Preview**")
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; max-width: 400px;">
            <div style="height: 200px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #666;">
                {'🖼️ Image Preview' if preview_data['image'] else '📷 No Image'}
            </div>
            <div style="padding: 12px; background-color: #f7f7f7;">
                <div style="color: #606770; font-size: 12px; text-transform: uppercase; margin-bottom: 4px;">
                    {preview_data['domain']}
                </div>
                <div style="color: #1d2129; font-size: 16px; font-weight: bold; margin-bottom: 4px; line-height: 1.2;">
                    {preview_data['title'][:60]}{'...' if len(preview_data['title']) > 60 else ''}
                </div>
                <div style="color: #606770; font-size: 14px; line-height: 1.3;">
                    {preview_data['description'][:120]}{'...' if len(preview_data['description']) > 120 else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.write("**Twitter Preview**")
        st.markdown(f"""
        <div style="border: 1px solid #e1e8ed; border-radius: 14px; overflow: hidden; max-width: 400px;">
            <div style="height: 200px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #666;">
                {'🖼️ Image Preview' if preview_data['image'] else '📷 No Image'}
            </div>
            <div style="padding: 12px; border-top: 1px solid #e1e8ed;">
                <div style="color: #536471; font-size: 15px; margin-bottom: 2px;">
                    {preview_data['domain']}
                </div>
                <div style="color: #0f1419; font-size: 15px; font-weight: bold; margin-bottom: 2px; line-height: 1.2;">
                    {preview_data['title'][:60]}{'...' if len(preview_data['title']) > 60 else ''}
                </div>
                <div style="color: #536471; font-size: 15px; line-height: 1.3;">
                    {preview_data['description'][:120]}{'...' if len(preview_data['description']) > 120 else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_seo_score(score: int):
    """Display SEO score with visual indicator"""
    st.subheader("SEO Score")
    st.markdown(create_score_circle(score), unsafe_allow_html=True)


def display_analysis_history(db_manager):
    """Display analysis history and comparison"""
    st.subheader("Analysis History")
    
    # URL Lookup Section
    st.write("**🔍 Look up previous analysis:**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        lookup_url = st.text_input(
            "Enter URL to find previous analysis:",
            placeholder="https://example.com",
            help="Enter a URL to retrieve its most recent SEO analysis"
        )
    
    with col2:
        lookup_button = st.button("🔍 Find Analysis", use_container_width=True)
    
    if lookup_button and lookup_url:
        analysis = db_manager.get_analysis_by_url(lookup_url)
        if analysis:
            st.success(f"✅ Found analysis from {analysis['analyzed_at'].strftime('%Y-%m-%d %H:%M')}")
            
            with st.expander("📊 View Analysis Results", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**URL:** {analysis['url']}")
                    st.write(f"**Title:** {analysis['title']}")
                    st.write(f"**Meta Description:** {analysis['meta_description'][:100]}{'...' if len(analysis['meta_description']) > 100 else ''}")
                    
                    # Show some key tags
                    if analysis['og_tags']:
                        st.write("**Open Graph Tags:**")
                        for key, value in list(analysis['og_tags'].items())[:3]:
                            st.write(f"  - {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
                    
                    if analysis['h1_tags']:
                        st.write(f"**H1 Tags:** {len(analysis['h1_tags'])} found")
                        for i, h1 in enumerate(analysis['h1_tags'][:2], 1):
                            st.write(f"  - H1 #{i}: {h1[:50]}{'...' if len(h1) > 50 else ''}")
                
                with col2:
                    # Display score
                    score = analysis['seo_score']
                    st.markdown(create_score_circle(score, size=80, font_size=24), unsafe_allow_html=True)
                
                # Button to re-analyze this URL
                if st.button(f"🔄 Re-analyze this URL", key="reanalyze_lookup"):
                    st.session_state.rerun_url = analysis['url']
                    st.rerun()
        else:
            st.warning(f"❌ No analysis found for: {lookup_url}")
            st.info("💡 Tip: Make sure the URL exactly matches a previously analyzed URL")
    
    st.divider()
    
    # Get recent analyses
    recent_analyses = db_manager.get_recent_analyses(20)
    
    if recent_analyses:
        st.write("**Recent Website Analyses:**")
        
        for i, analysis in enumerate(recent_analyses):
            with st.expander(f"🔗 {analysis['domain']} - Score: {analysis['seo_score']}/100 - {analysis['analyzed_at'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**URL:** {analysis['url']}")
                    st.write(f"**Title:** {analysis['title'][:100]}{'...' if len(analysis['title']) > 100 else ''}")
                
                with col2:
                    # Score color coding
                    score = analysis['seo_score']
                    color, _ = get_score_color_and_grade(score)
                    
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="color: {color}; font-size: 24px; font-weight: bold;">
                            {score}/100
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button(f"Re-analyze", key=f"reanalyze_{i}"):
                        # Pre-fill the URL input and trigger analysis
                        st.session_state.rerun_url = analysis['url']
                        st.rerun()
        
        # URL comparison section
        st.subheader("URL Performance Comparison")
        unique_domains = list(set([analysis['domain'] for analysis in recent_analyses]))
        
        if len(unique_domains) > 1:
            domain_scores = {}
            for domain in unique_domains:
                domain_analyses = [a for a in recent_analyses if a['domain'] == domain]
                avg_score = sum([a['seo_score'] for a in domain_analyses]) / len(domain_analyses)
                domain_scores[domain] = {
                    'avg_score': round(avg_score, 1),
                    'count': len(domain_analyses)
                }
            
            st.write("**Average SEO Scores by Domain:**")
            for domain, data in sorted(domain_scores.items(), key=lambda x: x[1]['avg_score'], reverse=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🌐 **{domain}** ({data['count']} analyses)")
                with col2:
                    st.write(f"**{data['avg_score']}/100**")
    else:
        st.info("No analysis history found. Analyze some websites to see them here!")


def display_interactive_preview_editing(preview_data: Dict, tab_type: str = "google"):
    """Display interactive preview editing interface"""
    if tab_type == "google":
        st.subheader("Edit Preview (Experimental)")
        with st.expander("✏️ Edit Title and Description"):
            edited_title = st.text_input("Title:", value=preview_data['title'], max_chars=60)
            edited_description = st.text_area("Description:", value=preview_data['description'], max_chars=160)
            
            if edited_title != preview_data['title'] or edited_description != preview_data['description']:
                edited_preview = preview_data.copy()
                edited_preview['title'] = edited_title
                edited_preview['description'] = edited_description
                
                st.write("**Updated Preview:**")
                display_google_preview(edited_preview)
    
    elif tab_type == "social":
        st.subheader("Edit Social Preview (Experimental)")
        with st.expander("✏️ Edit Social Media Preview"):
            edited_title_social = st.text_input("Social Title:", value=preview_data['title'], max_chars=60, key="social_title")
            edited_description_social = st.text_area("Social Description:", value=preview_data['description'], max_chars=120, key="social_desc")
            
            if edited_title_social != preview_data['title'] or edited_description_social != preview_data['description']:
                edited_preview_social = preview_data.copy()
                edited_preview_social['title'] = edited_title_social
                edited_preview_social['description'] = edited_description_social
                
                st.write("**Updated Social Preview:**")
                display_social_preview(edited_preview_social)