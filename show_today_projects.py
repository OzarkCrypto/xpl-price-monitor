#!/usr/bin/env python3
"""
Show today's projects with proper formatting and scoring
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.scraper import CryptoFundraisingScraper
from crypto_fundraising_monitor.scoring import InvestorQualityScorer

def show_today_projects():
    """Show all today's projects with proper formatting"""
    print("📋 Today's Crypto Fundraising Projects\n")
    
    scraper = CryptoFundraisingScraper()
    
    try:
        # Scrape data
        scraped_data = scraper.scrape_fundraising_data()
        
        if not scraped_data:
            print("❌ Failed to scrape data")
            return
        
        print(f"✅ Total projects found: {len(scraped_data.projects)}\n")
        
        # Sort projects by investor quality score
        sorted_projects = InvestorQualityScorer.get_projects_by_score(scraped_data.projects)
        
        # Show all projects with scores
        for i, project in enumerate(sorted_projects, 1):
            score = InvestorQualityScorer.calculate_project_score(project)
            should_highlight = InvestorQualityScorer.should_highlight(project)
            
            # Format project name with highlighting
            if should_highlight:
                project_name = f"**{project.name}**"
            else:
                project_name = project.name
            
            print(f"{i:02d}. {project_name}")
            print(f"    Round: {project.round_type}")
            print(f"    Amount: {project.formatted_amount}")
            print(f"    Category: {project.project_category}")
            print(f"    Investors: {', '.join(project.investor_names)}")
            print(f"    Score: {score} {'(HIGHLIGHT)' if should_highlight else ''}")
            print()
        
        # Show score distribution
        score_dist = InvestorQualityScorer.get_score_distribution(sorted_projects)
        print("📊 Score Distribution:")
        print(f"   High (≥7): {score_dist['high']} projects")
        print(f"   Medium (3-6): {score_dist['medium']} projects")
        print(f"   Low (0-2): {score_dist['low']} projects")
        
        # Show highlighted projects summary
        highlighted_projects = [p for p in sorted_projects if InvestorQualityScorer.should_highlight(p)]
        if highlighted_projects:
            print(f"\n✨ Highlighted Projects ({len(highlighted_projects)}):")
            for project in highlighted_projects:
                score = InvestorQualityScorer.calculate_project_score(project)
                print(f"   • {project.name} (Score: {score})")
        
        # Generate message preview
        print(f"\n💬 Message Preview:")
        print("=" * 50)
        
        # Header
        print("📋 Daily Crypto Fundraising (New)")
        print(f"오늘 신규 {len(sorted_projects)}건\n")
        
        # Projects
        for i, project in enumerate(sorted_projects):
            summary = InvestorQualityScorer.get_project_summary(project)
            print(summary)
            
            # Add separator between projects
            if i < len(sorted_projects) - 1:
                print("---------")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    show_today_projects() 