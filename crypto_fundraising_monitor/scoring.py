"""
Investor quality scoring module for Crypto Fundraising Monitor
"""
from typing import List
from .models import FundraisingProject, Investor
from .config import VC_SCORES, HIGHLIGHT_THRESHOLD


class InvestorQualityScorer:
    """Calculate investor quality scores for fundraising projects"""
    
    @staticmethod
    def calculate_project_score(project: FundraisingProject) -> int:
        """
        Calculate total investor quality score for a project
        
        Args:
            project: FundraisingProject instance
            
        Returns:
            Total score (sum of all investor scores)
        """
        total_score = 0
        
        for investor in project.investors:
            # Convert investor name to lowercase for matching
            investor_lower = investor.name.lower()
            
            # Check if investor matches any VC in our scoring system
            for vc_name, score in VC_SCORES.items():
                if vc_name in investor_lower or investor_lower in vc_name:
                    total_score += score
                    break
        
        return total_score
    
    @staticmethod
    def should_highlight(project: FundraisingProject) -> bool:
        """
        Determine if project should be highlighted (bold) based on score
        
        Args:
            project: FundraisingProject instance
            
        Returns:
            True if project meets highlight threshold
        """
        score = InvestorQualityScorer.calculate_project_score(project)
        return score >= HIGHLIGHT_THRESHOLD
    
    @staticmethod
    def get_project_summary(project: FundraisingProject) -> str:
        """
        Generate formatted project summary with highlighting
        
        Args:
            project: FundraisingProject instance
            
        Returns:
            Formatted string for Telegram message
        """
        score = InvestorQualityScorer.calculate_project_score(project)
        should_highlight = InvestorQualityScorer.should_highlight(project)
        
        # Format project name with highlighting if needed
        if should_highlight:
            project_name = f"**{project.name}**"
        else:
            project_name = project.name
        
        # Format investors list
        investor_names = [investor.name for investor in project.investors]
        investors_str = ", ".join(investor_names)
        
        # Create 3-line format as specified
        summary = (
            f"프로젝트: {project_name}\n"
            f"Raise amount: {project.formatted_amount}\n"
            f"Investors: {investors_str}\n"
        )
        
        return summary
    
    @staticmethod
    def get_projects_by_score(projects: List[FundraisingProject]) -> List[FundraisingProject]:
        """
        Sort projects by investor quality score (highest first)
        
        Args:
            projects: List of FundraisingProject instances
            
        Returns:
            Sorted list of projects
        """
        return sorted(
            projects,
            key=lambda p: InvestorQualityScorer.calculate_project_score(p),
            reverse=True
        )
    
    @staticmethod
    def get_score_distribution(projects: List[FundraisingProject]) -> dict:
        """
        Get distribution of projects by score ranges
        
        Args:
            projects: List of FundraisingProject instances
            
        Returns:
            Dictionary with score ranges and project counts
        """
        distribution = {
            'high': 0,      # >= HIGHLIGHT_THRESHOLD
            'medium': 0,    # 3-6
            'low': 0        # 0-2
        }
        
        for project in projects:
            score = InvestorQualityScorer.calculate_project_score(project)
            
            if score >= HIGHLIGHT_THRESHOLD:
                distribution['high'] += 1
            elif score >= 3:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution 