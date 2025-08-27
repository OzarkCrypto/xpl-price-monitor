#!/usr/bin/env python3
"""
Debug VC name matching and scoring
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.config import VC_SCORES, VC_TIERS
from crypto_fundraising_monitor.scoring import InvestorQualityScorer
from crypto_fundraising_monitor.models import FundraisingProject, Investor

def debug_vc_matching():
    """Debug VC name matching"""
    print("🔍 Debugging VC Name Matching...")
    
    print(f"\n📊 VC Tiers Configuration:")
    for tier, vcs in VC_TIERS.items():
        score = 5 if tier == 'T1' else (3 if tier == 'T2' else 2)
        print(f"{tier} ({score} points): {', '.join(vcs)}")
    
    print(f"\n📋 VC Scores Mapping ({len(VC_SCORES)} VCs):")
    for vc, score in sorted(VC_SCORES.items()):
        print(f"  {vc}: {score} points")
    
    # Test specific VCs from the scraped data
    test_vcs = [
        "Colosseum", "Balaji Srinivasan", "Ignight Capital",
        "SBI Holdings", "Mirana Ventures", "Offchain Labs", "Polygon", "Yunqi Partners",
        "CoinFund", "Hypersphere", "Tykhe Ventures", "Varrock", "Echo", "Breed VC", "WAGMI Ventures",
        "13bookscapital", "Lightspeed Faction", "Veris Ventures", "CRIT Ventures", "Mark Ransford"
    ]
    
    print(f"\n🧪 Testing VC Matching:")
    for vc in test_vcs:
        vc_lower = vc.lower()
        matched = False
        for known_vc, score in VC_SCORES.items():
            if known_vc in vc_lower or vc_lower in known_vc:
                print(f"✅ {vc} -> {known_vc} ({score} points)")
                matched = True
                break
        if not matched:
            print(f"❌ {vc} -> No match")
    
    # Test scoring with actual project
    print(f"\n🧪 Testing Project Scoring:")
    test_project = FundraisingProject(
        name="Test Project",
        round_type="Series A",
        date="Aug 2025",
        amount_usd=10000000,
        project_category="Infrastructure",
        investors=[
            Investor(name="Lightspeed Faction", is_lead=True),
            Investor(name="CoinFund", is_lead=False),
            Investor(name="Unknown VC", is_lead=False)
        ]
    )
    
    score = InvestorQualityScorer.calculate_project_score(test_project)
    print(f"Project Score: {score}")
    
    # Check individual investor scores
    for investor in test_project.investors:
        investor_lower = investor.name.lower()
        for known_vc, vc_score in VC_SCORES.items():
            if known_vc in investor_lower or investor_lower in known_vc:
                print(f"  {investor.name} -> {known_vc} ({vc_score} points)")
                break

if __name__ == "__main__":
    debug_vc_matching() 