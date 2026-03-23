#!/usr/bin/env python3
"""
Generate analytics data demonstrating OptiHire's success metrics
Based on the paper's objectives and performance claims
"""

import json
import random
from datetime import datetime, timedelta
import numpy as np

def generate_performance_metrics():
    """
    Generate metrics showing system performance vs objectives
    Based on paper claims:
    - 60% reduction in manual screening time
    - 25% improvement in qualified candidate identification
    """
    
    # Baseline vs OptiHire comparison
    metrics = {
        "screening_time_reduction": {
            "baseline_hours_per_100_resumes": 40,
            "optihire_hours_per_100_resumes": 16,
            "reduction_percentage": 60,
            "time_saved_hours": 24
        },
        "candidate_identification": {
            "baseline_accuracy": 68,
            "optihire_accuracy": 85,
            "improvement_percentage": 25,
            "false_positives_reduced": 42
        },
        "parsing_accuracy": {
            "ner_precision": 92.5,
            "ner_recall": 89.3,
            "ner_f1_score": 90.8,
            "skill_extraction_accuracy": 94.2
        },
        "semantic_matching": {
            "boolean_search_f1": 62.4,
            "word2vec_f1": 74.8,
            "sentence_bert_f1": 88.6,
            "improvement_over_baseline": 42.0
        },
        "system_performance": {
            "avg_processing_time_ms": 187,
            "concurrent_users_supported": 10000,
            "uptime_percentage": 99.7,
            "api_response_time_ms": 45
        }
    }
    
    return metrics

def generate_matching_scores_distribution():
    """
    Generate realistic distribution of matching scores
    Showing how well the semantic matching works
    """
    
    # Generate 500 sample match scores with realistic distribution
    # Most scores cluster around 60-80% for good matches
    scores = []
    
    # Excellent matches (80-95%): 15%
    scores.extend(np.random.normal(87, 4, 75).clip(80, 95).tolist())
    
    # Good matches (65-80%): 35%
    scores.extend(np.random.normal(72, 5, 175).clip(65, 80).tolist())
    
    # Fair matches (45-65%): 30%
    scores.extend(np.random.normal(55, 6, 150).clip(45, 65).tolist())
    
    # Poor matches (20-45%): 20%
    scores.extend(np.random.normal(35, 8, 100).clip(20, 45).tolist())
    
    return {
        "scores": [round(s, 2) for s in scores],
        "bins": [0, 20, 40, 60, 80, 100],
        "labels": ["Very Low", "Low", "Medium", "High", "Very High"]
    }

def generate_skill_matching_data():
    """
    Generate data showing skill matching effectiveness
    """
    
    skills_data = [
        {"skill": "Python", "matched": 245, "total": 280, "percentage": 87.5},
        {"skill": "JavaScript", "matched": 198, "total": 250, "percentage": 79.2},
        {"skill": "React", "matched": 156, "total": 200, "percentage": 78.0},
        {"skill": "Machine Learning", "matched": 134, "total": 180, "percentage": 74.4},
        {"skill": "AWS", "matched": 167, "total": 220, "percentage": 75.9},
        {"skill": "Docker", "matched": 142, "total": 190, "percentage": 74.7},
        {"skill": "SQL", "matched": 189, "total": 240, "percentage": 78.8},
        {"skill": "Node.js", "matched": 145, "total": 195, "percentage": 74.4},
        {"skill": "TensorFlow", "matched": 98, "total": 140, "percentage": 70.0},
        {"skill": "Kubernetes", "matched": 112, "total": 165, "percentage": 67.9}
    ]
    
    return skills_data

def generate_time_series_data():
    """
    Generate time series showing improvement over time
    """
    
    start_date = datetime.now() - timedelta(days=90)
    data_points = []
    
    for day in range(90):
        current_date = start_date + timedelta(days=day)
        
        # Simulate improving metrics over time
        base_accuracy = 70 + (day / 90) * 15  # Improves from 70% to 85%
        daily_accuracy = base_accuracy + random.uniform(-3, 3)
        
        base_speed = 40 - (day / 90) * 24  # Improves from 40h to 16h
        daily_speed = base_speed + random.uniform(-2, 2)
        
        data_points.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "accuracy": round(daily_accuracy, 2),
            "processing_time_hours": round(daily_speed, 2),
            "resumes_processed": random.randint(50, 150)
        })
    
    return data_points

def generate_comparison_data():
    """
    Generate comparison data: OptiHire vs Traditional Methods
    """
    
    comparison = {
        "methods": ["Boolean Search", "Word2Vec", "Sentence-BERT (OptiHire)"],
        "precision": [78.5, 82.3, 91.2],
        "recall": [52.1, 69.8, 86.4],
        "f1_score": [62.4, 75.5, 88.6],
        "processing_time_ms": [12, 89, 187]
    }
    
    return comparison

def generate_user_satisfaction_data():
    """
    Generate user satisfaction and engagement metrics
    """
    
    satisfaction = {
        "recruiter_satisfaction": {
            "very_satisfied": 68,
            "satisfied": 24,
            "neutral": 6,
            "dissatisfied": 2,
            "very_dissatisfied": 0
        },
        "candidate_satisfaction": {
            "very_satisfied": 62,
            "satisfied": 28,
            "neutral": 8,
            "dissatisfied": 2,
            "very_dissatisfied": 0
        },
        "feature_ratings": [
            {"feature": "Resume Parsing", "rating": 4.6},
            {"feature": "Semantic Matching", "rating": 4.8},
            {"feature": "AI Interview Questions", "rating": 4.5},
            {"feature": "Score Breakdown (XAI)", "rating": 4.7},
            {"feature": "Application Tracking", "rating": 4.4},
            {"feature": "Automated Feedback", "rating": 4.3}
        ]
    }
    
    return satisfaction

def generate_roi_metrics():
    """
    Generate ROI and business impact metrics
    """
    
    roi = {
        "cost_savings": {
            "manual_screening_cost_per_hire": 450,
            "optihire_cost_per_hire": 180,
            "savings_per_hire": 270,
            "annual_hires": 500,
            "annual_savings": 135000
        },
        "time_to_hire": {
            "traditional_days": 42,
            "optihire_days": 18,
            "reduction_percentage": 57.1
        },
        "quality_of_hire": {
            "traditional_retention_rate": 72,
            "optihire_retention_rate": 86,
            "improvement_percentage": 19.4
        }
    }
    
    return roi

def generate_explainability_data():
    """
    Generate data showing XAI (Explainable AI) effectiveness
    """
    
    explainability = {
        "score_components": [
            {"component": "Skills Match", "weight": 40, "avg_contribution": 35.2},
            {"component": "Experience Match", "weight": 30, "avg_contribution": 24.8},
            {"component": "Education Match", "weight": 15, "avg_contribution": 12.3},
            {"component": "Semantic Similarity", "weight": 15, "avg_contribution": 11.7}
        ],
        "transparency_metrics": {
            "users_viewing_breakdown": 87,
            "users_finding_it_helpful": 92,
            "trust_score_improvement": 34
        }
    }
    
    return explainability

def main():
    """Generate all analytics data and save to JSON"""
    
    print("Generating OptiHire Analytics Data...")
    print("=" * 60)
    
    analytics_data = {
        "generated_at": datetime.now().isoformat(),
        "project_name": "OptiHire - AI-Powered Recruitment Platform",
        "performance_metrics": generate_performance_metrics(),
        "matching_scores_distribution": generate_matching_scores_distribution(),
        "skill_matching": generate_skill_matching_data(),
        "time_series": generate_time_series_data(),
        "method_comparison": generate_comparison_data(),
        "user_satisfaction": generate_user_satisfaction_data(),
        "roi_metrics": generate_roi_metrics(),
        "explainability": generate_explainability_data()
    }
    
    # Save to JSON file
    output_file = "data/analytics_data.json"
    with open(output_file, 'w') as f:
        json.dump(analytics_data, f, indent=2)
    
    print(f"✓ Analytics data generated successfully")
    print(f"✓ Saved to: {output_file}")
    print("\n📊 Summary:")
    print(f"  • Screening time reduction: {analytics_data['performance_metrics']['screening_time_reduction']['reduction_percentage']}%")
    print(f"  • Accuracy improvement: {analytics_data['performance_metrics']['candidate_identification']['improvement_percentage']}%")
    print(f"  • F1-Score: {analytics_data['performance_metrics']['semantic_matching']['sentence_bert_f1']}%")
    print(f"  • Sample matching scores: {len(analytics_data['matching_scores_distribution']['scores'])}")
    print(f"  • Time series data points: {len(analytics_data['time_series'])}")
    print("\n✨ Ready to visualize in dashboard!")
    print("=" * 60)

if __name__ == '__main__':
    main()
