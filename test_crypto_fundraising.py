#!/usr/bin/env python3
"""
Test script for Crypto Fundraising Monitor
"""
import sys
import os
import logging
from unittest.mock import Mock, patch

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.models import FundraisingProject, Investor
from crypto_fundraising_monitor.scoring import InvestorQualityScorer
from crypto_fundraising_monitor.config import VC_SCORES, HIGHLIGHT_THRESHOLD

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


def test_vc_scoring():
    """Test VC scoring system"""
    print("🧪 Testing VC Scoring System...")
    
    # Test T1 VC (should get 5 points)
    test_project_t1 = FundraisingProject(
        name="Test Project T1",
        round_type="Series A",
        date="Aug 2025",
        amount_usd=10000000,
        project_category="Infrastructure",
        investors=[
            Investor(name="Sequoia", is_lead=True),
            Investor(name="a16z", is_lead=False)
        ]
    )
    
    score_t1 = InvestorQualityScorer.calculate_project_score(test_project_t1)
    print(f"T1 Project Score: {score_t1} (expected: 10)")
    assert score_t1 == 10, f"Expected 10, got {score_t1}"
    
    # Test T2 VC (should get 3 points)
    test_project_t2 = FundraisingProject(
        name="Test Project T2",
        round_type="Seed",
        date="Aug 2025",
        amount_usd=5000000,
        project_category="DeFi",
        investors=[
            Investor(name="Electric", is_lead=True),
            Investor(name="HashKey", is_lead=False)
        ]
    )
    
    score_t2 = InvestorQualityScorer.calculate_project_score(test_project_t2)
    print(f"T2 Project Score: {score_t2} (expected: 6)")
    assert score_t2 == 6, f"Expected 6, got {score_t2}"
    
    # Test mixed tier project
    test_project_mixed = FundraisingProject(
        name="Test Project Mixed",
        round_type="Series B",
        date="Aug 2025",
        amount_usd=20000000,
        project_category="AI",
        investors=[
            Investor(name="Sequoia", is_lead=True),
            Investor(name="Electric", is_lead=False),
            Investor(name="Unknown VC", is_lead=False)
        ]
    )
    
    score_mixed = InvestorQualityScorer.calculate_project_score(test_project_mixed)
    print(f"Mixed Project Score: {score_mixed} (expected: 8)")
    assert score_mixed == 8, f"Expected 8, got {score_mixed}"
    
    print("✅ VC Scoring tests passed!")


def test_highlight_threshold():
    """Test highlight threshold logic"""
    print("\n🧪 Testing Highlight Threshold...")
    
    # Project below threshold
    low_score_project = FundraisingProject(
        name="Low Score Project",
        round_type="Pre-seed",
        date="Aug 2025",
        amount_usd=1000000,
        project_category="Gaming",
        investors=[
            Investor(name="Unknown VC", is_lead=True)
        ]
    )
    
    should_highlight_low = InvestorQualityScorer.should_highlight(low_score_project)
    print(f"Low Score Project Highlight: {should_highlight_low} (expected: False)")
    assert not should_highlight_low, "Low score project should not be highlighted"
    
    # Project above threshold
    high_score_project = FundraisingProject(
        name="High Score Project",
        round_type="Series A",
        date="Aug 2025",
        amount_usd=15000000,
        project_category="Infrastructure",
        investors=[
            Investor(name="Sequoia", is_lead=True),
            Investor(name="a16z", is_lead=False)
        ]
    )
    
    should_highlight_high = InvestorQualityScorer.should_highlight(high_score_project)
    print(f"High Score Project Highlight: {should_highlight_high} (expected: True)")
    assert should_highlight_high, "High score project should be highlighted"
    
    print("✅ Highlight threshold tests passed!")


def test_project_formatting():
    """Test project message formatting"""
    print("\n🧪 Testing Project Formatting...")
    
    test_project = FundraisingProject(
        name="Test Project",
        round_type="Series A",
        date="Aug 2025",
        amount_usd=10000000,
        project_category="Infrastructure",
        investors=[
            Investor(name="Sequoia", is_lead=True),
            Investor(name="Electric", is_lead=False)
        ]
    )
    
    summary = InvestorQualityScorer.get_project_summary(test_project)
    print("Project Summary:")
    print(summary)
    
    # Check if summary contains required elements
    assert "프로젝트:" in summary, "Summary should contain project name"
    assert "Raise amount:" in summary, "Summary should contain amount"
    assert "Investors:" in summary, "Summary should contain investors"
    assert "Sequoia" in summary, "Summary should contain investor names"
    assert "Electric" in summary, "Summary should contain investor names"
    
    print("✅ Project formatting tests passed!")


def test_config_validation():
    """Test configuration validation"""
    print("\n🧪 Testing Configuration...")
    
    print(f"Highlight Threshold: {HIGHLIGHT_THRESHOLD}")
    print(f"VC Tiers: {len(VC_SCORES)} VCs configured")
    
    # Check if key VCs are in the scoring system
    key_vcs = ['sequoia', 'a16z', 'paradigm', 'pantera']
    for vc in key_vcs:
        if vc in VC_SCORES:
            print(f"✅ {vc}: {VC_SCORES[vc]} points")
        else:
            print(f"❌ {vc}: Not found in scoring system")
    
    print("✅ Configuration tests completed!")


def main():
    """Run all tests"""
    print("🚀 Starting Crypto Fundraising Monitor Tests\n")
    
    try:
        test_vc_scoring()
        test_highlight_threshold()
        test_project_formatting()
        test_config_validation()
        
        print("\n🎉 All tests passed successfully!")
        print("\n시스템이 정상적으로 작동합니다.")
        print("실제 사용을 위해서는 다음 단계를 완료하세요:")
        print("1. .env 파일에 TELEGRAM_BOT_TOKEN 설정")
        print("2. python crypto_fundraising_monitor/run.py 실행")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 