#!/usr/bin/env python3
"""
Lead Score Calculator

This script calculates lead scores from CRM exports (CSV format) based on
demographic fit and behavioral engagement criteria. It supports HubSpot,
Salesforce, and generic CSV formats.

Usage:
    python score-calculator.py --input contacts.csv --output scored_contacts.csv
    python score-calculator.py --input contacts.csv --config custom_scoring.json
    python score-calculator.py --analyze contacts.csv  # Analysis mode only

Requirements:
    pandas, numpy, argparse, json, datetime
"""

import pandas as pd
import numpy as np
import argparse
import json
import sys
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadScoreCalculator:
    """
    Lead scoring engine that calculates demographic and behavioral scores
    based on configurable criteria.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the calculator with scoring configuration.
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.scoring_results = {}
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load scoring configuration from file or use defaults."""
        
        default_config = {
            "demographic_scoring": {
                "industry": {
                    "technology": 20,
                    "software": 20,
                    "saas": 20,
                    "professional services": 15,
                    "consulting": 15,
                    "financial services": 15,
                    "healthcare": 10,
                    "manufacturing": 10,
                    "education": 8,
                    "retail": 5,
                    "government": 2,
                    "non-profit": 2,
                    "competitor": -50
                },
                "company_size": {
                    "1-24": 5,
                    "25-49": 8,
                    "50-99": 12,
                    "100-1000": 25,
                    "1001-5000": 15,
                    "5001-10000": 8,
                    "10000+": 3
                },
                "job_title": {
                    "ceo|cto|cmo|cfo|president|founder|owner": 30,
                    "vp|vice president|svp|evp": 25,
                    "director|head of": 20,
                    "manager|senior manager": 15,
                    "senior|lead": 10,
                    "coordinator|specialist|analyst": 8,
                    "associate|assistant": 5,
                    "intern|student": -5
                },
                "revenue": {
                    "1000000-10000000": 15,
                    "10000000-100000000": 20,
                    "100000000+": 10,
                    "unknown": 0
                }
            },
            "behavioral_scoring": {
                "website_activity": {
                    "pricing_page": 10,
                    "demo_page": 8,
                    "case_studies": 6,
                    "product_pages": 5,
                    "blog": 2,
                    "careers": -2
                },
                "email_engagement": {
                    "email_open": 1,
                    "email_click": 3,
                    "email_reply": 10,
                    "unsubscribe": -10
                },
                "content_downloads": {
                    "whitepaper": 15,
                    "case_study": 12,
                    "datasheet": 10,
                    "ebook": 8,
                    "webinar": 12,
                    "template": 6
                },
                "form_submissions": {
                    "demo_request": 20,
                    "contact_form": 15,
                    "trial_signup": 25,
                    "newsletter": 5
                }
            },
            "thresholds": {
                "mql": 50,
                "sql": 80,
                "hot_lead": 90
            },
            "decay_rules": {
                "website_activity": {
                    "days": 30,
                    "rate": 0.5
                },
                "email_engagement": {
                    "days": 60,
                    "rate": 0.25
                }
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    # Merge with defaults
                    default_config.update(custom_config)
                    logger.info(f"Loaded custom configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
                logger.info("Using default configuration")
        
        return default_config
    
    def calculate_demographic_score(self, row: pd.Series) -> Dict[str, Any]:
        """
        Calculate demographic fit score based on company and individual attributes.
        
        Args:
            row: DataFrame row containing contact data
            
        Returns:
            Dictionary with demographic score and breakdown
        """
        score = 0
        breakdown = {}
        
        # Industry scoring
        industry_score = self._score_industry(row.get('industry', ''))
        score += industry_score
        breakdown['industry'] = industry_score
        
        # Company size scoring
        size_score = self._score_company_size(row)
        score += size_score
        breakdown['company_size'] = size_score
        
        # Job title scoring
        title_score = self._score_job_title(row.get('job_title', ''))
        score += title_score
        breakdown['job_title'] = title_score
        
        # Revenue scoring (if available)
        revenue_score = self._score_revenue(row.get('annual_revenue', ''))
        score += revenue_score
        breakdown['revenue'] = revenue_score
        
        return {
            'score': max(0, score),  # Don't allow negative demographic scores
            'breakdown': breakdown
        }
    
    def _score_industry(self, industry: str) -> int:
        """Score based on industry fit."""
        if pd.isna(industry) or industry == '':
            return 0
        
        industry = str(industry).lower().strip()
        industry_scores = self.config['demographic_scoring']['industry']
        
        # Exact match first
        if industry in industry_scores:
            return industry_scores[industry]
        
        # Partial match
        for key, score in industry_scores.items():
            if key in industry or industry in key:
                return score
        
        return 0  # Unknown industry
    
    def _score_company_size(self, row: pd.Series) -> int:
        """Score based on company size (employees)."""
        # Try multiple common column names
        size_fields = ['num_employees', 'company_size', 'employees', 'number_of_employees']
        size_value = None
        
        for field in size_fields:
            if field in row and not pd.isna(row[field]):
                size_value = row[field]
                break
        
        if size_value is None:
            return 0
        
        # Convert to integer if it's a string representation
        try:
            if isinstance(size_value, str):
                # Extract numbers from strings like "100-500"
                numbers = re.findall(r'\d+', size_value.replace(',', ''))
                if numbers:
                    size_value = int(numbers[0])  # Take the first number
                else:
                    return 0
            else:
                size_value = int(size_value)
        except (ValueError, TypeError):
            return 0
        
        # Map to size ranges
        size_ranges = self.config['demographic_scoring']['company_size']
        
        if size_value <= 24:
            return size_ranges['1-24']
        elif size_value <= 49:
            return size_ranges['25-49']
        elif size_value <= 99:
            return size_ranges['50-99']
        elif size_value <= 1000:
            return size_ranges['100-1000']
        elif size_value <= 5000:
            return size_ranges['1001-5000']
        elif size_value <= 10000:
            return size_ranges['5001-10000']
        else:
            return size_ranges['10000+']
    
    def _score_job_title(self, job_title: str) -> int:
        """Score based on job title/role."""
        if pd.isna(job_title) or job_title == '':
            return 0
        
        job_title = str(job_title).lower().strip()
        title_patterns = self.config['demographic_scoring']['job_title']
        
        for pattern, score in title_patterns.items():
            # Use regex matching for flexible title matching
            if re.search(pattern, job_title):
                return score
        
        return 0  # Unknown title
    
    def _score_revenue(self, revenue: str) -> int:
        """Score based on annual revenue."""
        if pd.isna(revenue) or revenue == '':
            return 0
        
        try:
            # Convert revenue to number (handle various formats)
            revenue_str = str(revenue).replace('$', '').replace(',', '').lower()
            
            # Handle 'k' and 'm' suffixes
            if 'k' in revenue_str:
                revenue_num = float(revenue_str.replace('k', '')) * 1000
            elif 'm' in revenue_str:
                revenue_num = float(revenue_str.replace('m', '')) * 1000000
            else:
                revenue_num = float(revenue_str)
            
            # Map to revenue ranges
            if 1000000 <= revenue_num < 10000000:
                return self.config['demographic_scoring']['revenue']['1000000-10000000']
            elif 10000000 <= revenue_num < 100000000:
                return self.config['demographic_scoring']['revenue']['10000000-100000000']
            elif revenue_num >= 100000000:
                return self.config['demographic_scoring']['revenue']['100000000+']
            else:
                return 0
                
        except (ValueError, TypeError):
            return self.config['demographic_scoring']['revenue']['unknown']
    
    def calculate_behavioral_score(self, row: pd.Series) -> Dict[str, Any]:
        """
        Calculate behavioral engagement score based on activities.
        
        Args:
            row: DataFrame row containing activity data
            
        Returns:
            Dictionary with behavioral score and breakdown
        """
        score = 0
        breakdown = {}
        
        # Website activity scoring
        website_score = self._score_website_activity(row)
        score += website_score
        breakdown['website_activity'] = website_score
        
        # Email engagement scoring
        email_score = self._score_email_engagement(row)
        score += email_score
        breakdown['email_engagement'] = email_score
        
        # Content download scoring
        content_score = self._score_content_downloads(row)
        score += content_score
        breakdown['content_downloads'] = content_score
        
        # Form submission scoring
        form_score = self._score_form_submissions(row)
        score += form_score
        breakdown['form_submissions'] = form_score
        
        return {
            'score': max(0, score),
            'breakdown': breakdown
        }
    
    def _score_website_activity(self, row: pd.Series) -> int:
        """Score website page visits and session data."""
        score = 0
        website_scores = self.config['behavioral_scoring']['website_activity']
        
        # Look for page visit columns
        page_columns = [col for col in row.index if 'page' in col.lower() or 'visit' in col.lower()]
        
        for col in page_columns:
            if pd.isna(row[col]) or row[col] == 0:
                continue
                
            page_type = col.lower()
            visits = int(row[col]) if isinstance(row[col], (int, float)) else 1
            
            # Match page types to scoring rules
            for page_key, points in website_scores.items():
                if page_key.replace('_', ' ') in page_type or page_key.replace('_', '') in page_type:
                    # Apply diminishing returns for multiple visits
                    page_score = points * min(visits, 3) * (0.8 ** max(0, visits - 1))
                    score += page_score
                    break
        
        # Session quality bonuses
        if 'session_duration' in row and not pd.isna(row['session_duration']):
            duration = float(row['session_duration'])
            if duration > 300:  # 5 minutes
                score += 5
            elif duration > 120:  # 2 minutes
                score += 2
        
        return int(score)
    
    def _score_email_engagement(self, row: pd.Series) -> int:
        """Score email opens, clicks, and replies."""
        score = 0
        email_scores = self.config['behavioral_scoring']['email_engagement']
        
        # Email opens
        if 'email_opens' in row and not pd.isna(row['email_opens']):
            opens = int(row['email_opens'])
            score += email_scores['email_open'] * min(opens, 10)  # Cap at 10 opens
        
        # Email clicks
        if 'email_clicks' in row and not pd.isna(row['email_clicks']):
            clicks = int(row['email_clicks'])
            score += email_scores['email_click'] * min(clicks, 5)  # Cap at 5 clicks
        
        # Email replies
        if 'email_replies' in row and not pd.isna(row['email_replies']):
            replies = int(row['email_replies'])
            score += email_scores['email_reply'] * replies
        
        # Unsubscribes (negative scoring)
        if 'unsubscribed' in row and row['unsubscribed']:
            score += email_scores['unsubscribe']
        
        return score
    
    def _score_content_downloads(self, row: pd.Series) -> int:
        """Score content downloads and resource access."""
        score = 0
        content_scores = self.config['behavioral_scoring']['content_downloads']
        
        # Look for download columns
        download_columns = [col for col in row.index if 'download' in col.lower() or 'content' in col.lower()]
        
        for col in download_columns:
            if pd.isna(row[col]) or row[col] == 0:
                continue
            
            downloads = int(row[col]) if isinstance(row[col], (int, float)) else 1
            content_type = col.lower()
            
            # Match content types to scoring rules
            for content_key, points in content_scores.items():
                if content_key.replace('_', ' ') in content_type or content_key in content_type:
                    score += points * min(downloads, 3)  # Cap at 3 downloads per type
                    break
        
        return score
    
    def _score_form_submissions(self, row: pd.Series) -> int:
        """Score form submissions and lead magnets."""
        score = 0
        form_scores = self.config['behavioral_scoring']['form_submissions']
        
        # Look for form submission columns
        form_columns = [col for col in row.index if 'form' in col.lower() or 'submit' in col.lower()]
        
        for col in form_columns:
            if pd.isna(row[col]) or row[col] == 0:
                continue
            
            submissions = int(row[col]) if isinstance(row[col], (int, float)) else 1
            form_type = col.lower()
            
            # Match form types to scoring rules
            for form_key, points in form_scores.items():
                if form_key.replace('_', ' ') in form_type or form_key in form_type:
                    score += points * submissions
                    break
        
        return score
    
    def apply_decay_rules(self, behavioral_score: int, last_activity_date: str) -> int:
        """Apply time decay to behavioral scores based on last activity."""
        if pd.isna(last_activity_date) or last_activity_date == '':
            return int(behavioral_score * 0.5)  # Heavy penalty for unknown activity
        
        try:
            last_activity = pd.to_datetime(last_activity_date)
            days_since_activity = (datetime.now() - last_activity).days
            
            # Apply website activity decay
            website_decay = self.config['decay_rules']['website_activity']
            if days_since_activity > website_decay['days']:
                periods = days_since_activity // website_decay['days']
                decay_factor = website_decay['rate'] ** periods
                behavioral_score = int(behavioral_score * decay_factor)
            
            return behavioral_score
            
        except (ValueError, TypeError):
            return int(behavioral_score * 0.5)
    
    def classify_lead(self, total_score: int) -> str:
        """Classify lead based on total score."""
        thresholds = self.config['thresholds']
        
        if total_score >= thresholds['hot_lead']:
            return 'Hot Lead'
        elif total_score >= thresholds['sql']:
            return 'SQL'
        elif total_score >= thresholds['mql']:
            return 'MQL'
        else:
            return 'Cold Lead'
    
    def process_contacts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all contacts in the DataFrame and calculate scores.
        
        Args:
            df: DataFrame containing contact data
            
        Returns:
            DataFrame with added scoring columns
        """
        logger.info(f"Processing {len(df)} contacts...")
        
        # Initialize new columns
        df['demographic_score'] = 0
        df['behavioral_score'] = 0
        df['total_lead_score'] = 0
        df['lead_grade'] = 'D'
        df['lead_classification'] = 'Cold Lead'
        df['scoring_notes'] = ''
        
        # Process each contact
        for idx, row in df.iterrows():
            try:
                # Calculate demographic score
                demo_result = self.calculate_demographic_score(row)
                df.at[idx, 'demographic_score'] = demo_result['score']
                
                # Calculate behavioral score
                behavioral_result = self.calculate_behavioral_score(row)
                behavioral_score = behavioral_result['score']
                
                # Apply decay if last activity date is available
                if 'last_activity_date' in df.columns:
                    behavioral_score = self.apply_decay_rules(
                        behavioral_score, 
                        row.get('last_activity_date', '')
                    )
                
                df.at[idx, 'behavioral_score'] = behavioral_score
                
                # Calculate total score
                total_score = demo_result['score'] + behavioral_score
                df.at[idx, 'total_lead_score'] = total_score
                
                # Assign grade based on demographic score
                demo_score = demo_result['score']
                if demo_score >= 80:
                    grade = 'A+'
                elif demo_score >= 70:
                    grade = 'A'
                elif demo_score >= 60:
                    grade = 'A-'
                elif demo_score >= 50:
                    grade = 'B+'
                elif demo_score >= 40:
                    grade = 'B'
                elif demo_score >= 30:
                    grade = 'B-'
                elif demo_score >= 20:
                    grade = 'C+'
                elif demo_score >= 10:
                    grade = 'C'
                else:
                    grade = 'D'
                
                df.at[idx, 'lead_grade'] = grade
                
                # Classify lead
                df.at[idx, 'lead_classification'] = self.classify_lead(total_score)
                
                # Add scoring notes
                notes = f"Demo: {demo_result['score']}, Behavioral: {behavioral_score}"
                df.at[idx, 'scoring_notes'] = notes
                
            except Exception as e:
                logger.warning(f"Error processing contact {idx}: {e}")
                continue
        
        logger.info("Scoring completed successfully")
        return df
    
    def generate_analysis_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate analysis report of scoring results."""
        
        report = {
            'summary': {
                'total_contacts': len(df),
                'avg_total_score': df['total_lead_score'].mean(),
                'avg_demographic_score': df['demographic_score'].mean(),
                'avg_behavioral_score': df['behavioral_score'].mean()
            },
            'score_distribution': {
                'hot_leads': len(df[df['lead_classification'] == 'Hot Lead']),
                'sqls': len(df[df['lead_classification'] == 'SQL']),
                'mqls': len(df[df['lead_classification'] == 'MQL']),
                'cold_leads': len(df[df['lead_classification'] == 'Cold Lead'])
            },
            'grade_distribution': df['lead_grade'].value_counts().to_dict(),
            'top_scoring_factors': {},
            'recommendations': []
        }
        
        # Add recommendations based on analysis
        hot_lead_pct = report['score_distribution']['hot_leads'] / len(df) * 100
        if hot_lead_pct < 5:
            report['recommendations'].append(
                "Consider lowering Hot Lead threshold or adjusting scoring criteria"
            )
        elif hot_lead_pct > 15:
            report['recommendations'].append(
                "Consider raising Hot Lead threshold to focus on best prospects"
            )
        
        mql_pct = report['score_distribution']['mqls'] / len(df) * 100
        if mql_pct < 10:
            report['recommendations'].append(
                "MQL threshold may be too high - consider lowering to capture more leads"
            )
        
        return report

def main():
    """Main function to run the lead scoring calculator."""
    parser = argparse.ArgumentParser(description='Calculate lead scores from CSV export')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file path')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--config', '-c', help='JSON configuration file path')
    parser.add_argument('--analyze', '-a', action='store_true', 
                       help='Analysis mode - generate report only')
    parser.add_argument('--sample', '-s', type=int, 
                       help='Process only a sample of N contacts')
    
    args = parser.parse_args()
    
    try:
        # Load data
        logger.info(f"Loading data from {args.input}")
        df = pd.read_csv(args.input)
        
        if args.sample:
            df = df.sample(n=min(args.sample, len(df)))
            logger.info(f"Using sample of {len(df)} contacts")
        
        # Initialize calculator
        calculator = LeadScoreCalculator(args.config)
        
        # Process contacts
        scored_df = calculator.process_contacts(df)
        
        # Generate analysis report
        report = calculator.generate_analysis_report(scored_df)
        
        # Print analysis
        print("\n" + "="*60)
        print("LEAD SCORING ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nSUMMARY:")
        print(f"  Total Contacts: {report['summary']['total_contacts']:,}")
        print(f"  Average Total Score: {report['summary']['avg_total_score']:.1f}")
        print(f"  Average Demographic Score: {report['summary']['avg_demographic_score']:.1f}")
        print(f"  Average Behavioral Score: {report['summary']['avg_behavioral_score']:.1f}")
        
        print(f"\nLEAD CLASSIFICATION:")
        total = report['summary']['total_contacts']
        for classification, count in report['score_distribution'].items():
            pct = count / total * 100
            print(f"  {classification}: {count:,} ({pct:.1f}%)")
        
        print(f"\nGRADE DISTRIBUTION:")
        for grade, count in sorted(report['grade_distribution'].items()):
            pct = count / total * 100
            print(f"  Grade {grade}: {count:,} ({pct:.1f}%)")
        
        if report['recommendations']:
            print(f"\nRECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Save output if not in analysis mode
        if not args.analyze:
            output_path = args.output or args.input.replace('.csv', '_scored.csv')
            scored_df.to_csv(output_path, index=False)
            logger.info(f"Scored data saved to {output_path}")
            
            # Save top scoring contacts
            top_contacts = scored_df.nlargest(20, 'total_lead_score')
            top_path = output_path.replace('.csv', '_top_20.csv')
            top_contacts.to_csv(top_path, index=False)
            logger.info(f"Top 20 contacts saved to {top_path}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()