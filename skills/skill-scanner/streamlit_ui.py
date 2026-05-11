#!/usr/bin/env python3
"""
Skill Scanner - Streamlit Web UI
A user-friendly interface for scanning Clawdbot/MCP skills for security issues.
"""

import streamlit as st
import tempfile
import os
import zipfile
import shutil
from pathlib import Path

# Import the scanner
try:
    from skill_scanner import SkillScanner
except ImportError:
    st.error("skill_scanner.py must be in the same directory as this file")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Skill Scanner",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .safe-badge {
        background-color: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
    }
    .warning-badge {
        background-color: #f59e0b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
    }
    .danger-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
    }
    .finding-card {
        border-left: 4px solid;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9fafb;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .critical { border-color: #ef4444; }
    .high { border-color: #f97316; }
    .medium { border-color: #f59e0b; }
    .low { border-color: #3b82f6; }
    .info { border-color: #6b7280; }
</style>
""", unsafe_allow_html=True)

def get_severity_color(severity: str) -> str:
    """Get color for severity level."""
    colors = {
        'critical': '#ef4444',
        'high': '#f97316',
        'medium': '#f59e0b',
        'low': '#3b82f6',
        'info': '#6b7280'
    }
    return colors.get(severity.lower(), '#6b7280')

def get_verdict_display(verdict: str):
    """Get styled verdict display."""
    if verdict == 'APPROVED':
        return '**APPROVED** - No security issues detected', 'success'
    elif verdict == 'CAUTION':
        return '**CAUTION** - Minor issues found, review recommended', 'warning'
    else:
        return '**REJECT** - Security issues detected', 'error'

def main():
    # Header
    st.markdown('<p class="main-header">Skill Scanner</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Security audit tool for Clawdbot/MCP skills - scans for malware, spyware, crypto-mining, and malicious patterns</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        output_format = st.selectbox("Output Format", ["Markdown", "JSON"], index=0)
        show_info = st.checkbox("Show Info-level findings", value=False)
        st.markdown("---")
        st.markdown("### About")
        st.markdown("This tool scans skill files for potential security issues including:")
        st.markdown("- Data exfiltration patterns")
        st.markdown("- System modification attempts")
        st.markdown("- Crypto-mining indicators")
        st.markdown("- Arbitrary code execution risks")
        st.markdown("- Backdoors and obfuscation")
    
    # Main content
    tab1, tab2 = st.tabs(["Scan Files", "Scan Text"])
    
    with tab1:
        st.subheader("Upload Skill Files")
        uploaded_files = st.file_uploader(
            "Upload skill files or a ZIP archive",
            accept_multiple_files=True,
            type=['py', 'js', 'ts', 'sh', 'bash', 'md', 'txt', 'json', 'yaml', 'yml', 'zip'],
            help="Supports Python, JavaScript, TypeScript, Shell scripts, and ZIP archives"
        )
        
        if uploaded_files:
            if st.button("Scan Files", type="primary", use_container_width=True):
                with st.spinner("Scanning files for security issues..."):
                    # Create temp directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        
                        for uploaded_file in uploaded_files:
                            file_path = temp_path / uploaded_file.name
                            
                            if uploaded_file.name.endswith('.zip'):
                                # Extract ZIP file
                                with open(file_path, 'wb') as f:
                                    f.write(uploaded_file.getvalue())
                                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                    zip_ref.extractall(temp_path)
                                os.remove(file_path)
                            else:
                                with open(file_path, 'wb') as f:
                                    f.write(uploaded_file.getvalue())
                        
                        # Run scanner
                        scanner = SkillScanner(str(temp_path))
                        results = scanner.scan()
                        
                        display_results(results, output_format.lower(), show_info)
    
    with tab2:
        st.subheader("Paste Code for Analysis")
        code_input = st.text_area(
            "Paste code to scan",
            height=300,
            placeholder="Paste your skill code here...",
            help="Paste any code snippet to scan for security issues"
        )
        
        if code_input:
            if st.button("Scan Code", type="primary", use_container_width=True, key="scan_text"):
                with st.spinner("Analyzing code..."):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        code_file = temp_path / "code_snippet.py"
                        code_file.write_text(code_input)
                        
                        scanner = SkillScanner(str(temp_path))
                        results = scanner.scan()
                        
                        display_results(results, output_format.lower(), show_info)

def display_results(results: dict, output_format: str, show_info: bool):
    """Display scan results in a user-friendly format."""
    
    st.markdown("---")
    st.header("Scan Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    findings = results.get('findings', [])
    if not show_info:
        findings = [f for f in findings if f.get('severity', '').lower() != 'info']
    
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for finding in results.get('findings', []):
        sev = finding.get('severity', 'info').lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
    
    with col1:
        st.metric("Critical", severity_counts['critical'])
    with col2:
        st.metric("High", severity_counts['high'])
    with col3:
        st.metric("Medium", severity_counts['medium'])
    with col4:
        st.metric("Low", severity_counts['low'])
    
    # Verdict
    verdict = results.get('verdict', 'UNKNOWN')
    verdict_text, verdict_type = get_verdict_display(verdict)
    
    if verdict_type == 'success':
        st.success(verdict_text)
    elif verdict_type == 'warning':
        st.warning(verdict_text)
    else:
        st.error(verdict_text)
    
    # Files scanned
    files_scanned = results.get('files_scanned', [])
    if files_scanned:
        with st.expander(f"Files Scanned ({len(files_scanned)})", expanded=False):
            for f in files_scanned:
                st.text(f"- {f}")
    
    # Detailed findings
    if findings:
        st.subheader(f"Findings ({len(findings)})")
        
        for i, finding in enumerate(findings):
            severity = finding.get('severity', 'info').lower()
            color = get_severity_color(severity)
            
            with st.container():
                st.markdown(f"""
                <div class="finding-card {severity}">
                    <strong style="color: {color};">[{severity.upper()}]</strong> 
                    <strong>{finding.get('category', 'Unknown')}</strong><br/>
                    <em>{finding.get('file', 'Unknown file')}</em> 
                    {f"(Line {finding.get('line', '?')})" if finding.get('line') else ''}<br/>
                    {finding.get('description', '')}
                </div>
                """, unsafe_allow_html=True)
                
                if finding.get('match'):
                    with st.expander("View matched code"):
                        st.code(finding.get('match', ''), language='python')
    else:
        st.info("No security issues found!")
    
    # Export options
    st.markdown("---")
    st.subheader("Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Markdown export
        if output_format == 'markdown':
            from skill_scanner import SkillScanner
            scanner = SkillScanner('.')
            md_report = scanner.format_markdown(results)
            st.download_button(
                label="Download Markdown Report",
                data=md_report,
                file_name="skill_scan_report.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with col2:
        # JSON export
        import json
        json_report = json.dumps(results, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name="skill_scan_report.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
