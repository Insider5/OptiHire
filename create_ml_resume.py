#!/usr/bin/env python3
"""
Create a Machine Learning Engineer demo resume PDF
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import os

def create_ml_resume():
    """Create a Machine Learning Engineer resume PDF"""
    
    os.makedirs('uploads', exist_ok=True)
    
    pdf_path = 'uploads/demo_resume_sarah_chen.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, 
                                 textColor=colors.HexColor('#1a365d'), spaceAfter=6, 
                                 alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
                                   textColor=colors.HexColor('#2c5282'), spaceAfter=6, 
                                   spaceBefore=12, fontName='Helvetica-Bold')
    
    normal_style = styles['Normal']
    
    # Header
    story.append(Paragraph('SARAH CHEN', title_style))
    story.append(Paragraph('Machine Learning Engineer', 
                          ParagraphStyle('Subtitle', parent=normal_style, fontSize=12,
                                       textColor=colors.HexColor('#4a5568'), alignment=TA_CENTER)))
    story.append(Spacer(1, 0.1*inch))
    
    # Contact
    contact_data = [['Email: sarah.chen.ml@email.com', 'Phone: +1 (555) 987-6543', 'Location: Remote']]
    contact_table = Table(contact_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#4a5568'))
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph('PROFESSIONAL SUMMARY', heading_style))
    story.append(Paragraph(
        'Machine Learning Engineer with 4+ years of experience developing and deploying ML models at scale. '
        'Expertise in deep learning, NLP, and computer vision. Proven ability to translate business problems '
        'into ML solutions. Strong background in Python, TensorFlow, PyTorch, and cloud ML platforms. '
        'Published researcher with contributions to top-tier ML conferences.',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Skills
    story.append(Paragraph('TECHNICAL SKILLS', heading_style))
    skills_text = '''
    <b>Languages:</b> Python, R, SQL, C++, Java<br/>
    <b>ML/DL Frameworks:</b> TensorFlow, PyTorch, Keras, Scikit-learn, XGBoost, LightGBM<br/>
    <b>NLP &amp; CV:</b> Transformers, BERT, GPT, YOLO, ResNet, spaCy, Hugging Face<br/>
    <b>Data Science:</b> Pandas, NumPy, Matplotlib, Seaborn, Jupyter, MLflow<br/>
    <b>Cloud &amp; MLOps:</b> AWS SageMaker, GCP AI Platform, Docker, Kubernetes, Airflow<br/>
    <b>Databases:</b> PostgreSQL, MongoDB, Redis, Elasticsearch
    '''
    story.append(Paragraph(skills_text, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Experience
    story.append(Paragraph('PROFESSIONAL EXPERIENCE', heading_style))
    
    story.append(Paragraph(
        '<b>Machine Learning Engineer</b> | AI Innovations Lab | Remote<br/>'
        '<i>February 2022 - Present</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Developed NLP models for sentiment analysis achieving 94% accuracy on production data<br/>'
        '• Built and deployed recommendation system serving 1M+ users with 35% increase in engagement<br/>'
        '• Implemented MLOps pipeline for automated model training, testing, and deployment<br/>'
        '• Optimized deep learning models reducing inference time by 60% using TensorRT<br/>'
        '• Collaborated with data engineers to build scalable feature engineering pipelines',
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(
        '<b>Data Scientist</b> | TechData Corp | Seattle, WA<br/>'
        '<i>June 2020 - January 2022</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Designed computer vision models for object detection with 89% mAP score<br/>'
        '• Developed time-series forecasting models improving prediction accuracy by 25%<br/>'
        '• Created data visualization dashboards for model performance monitoring<br/>'
        '• Conducted A/B tests to evaluate model performance in production<br/>'
        '• Presented ML insights to stakeholders and executive leadership',
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(
        '<b>ML Research Intern</b> | Google AI | Mountain View, CA<br/>'
        '<i>Summer 2019</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Researched novel attention mechanisms for transformer models<br/>'
        '• Implemented and benchmarked state-of-the-art NLP models<br/>'
        '• Co-authored research paper accepted at NeurIPS 2020<br/>'
        '• Contributed to open-source TensorFlow projects',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Education
    story.append(Paragraph('EDUCATION', heading_style))
    story.append(Paragraph(
        '<b>Master of Science in Artificial Intelligence</b><br/>'
        'MIT | Graduated: May 2020<br/>'
        'Thesis: "Efficient Attention Mechanisms for Large-Scale NLP"<br/>'
        'GPA: 3.9/4.0',
        normal_style
    ))
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph(
        '<b>Bachelor of Science in Mathematics</b><br/>'
        'UC Berkeley | Graduated: May 2018<br/>'
        'Minor: Computer Science | GPA: 3.8/4.0',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Certifications
    story.append(Paragraph('CERTIFICATIONS', heading_style))
    story.append(Paragraph(
        '• TensorFlow Developer Certificate (2023)<br/>'
        '• Deep Learning Specialization - Coursera (2021)<br/>'
        '• AWS Machine Learning Specialty (2022)',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Publications & Projects
    story.append(Paragraph('PUBLICATIONS &amp; PROJECTS', heading_style))
    story.append(Paragraph(
        '• <b>Research Paper:</b> "Efficient Transformers for Low-Resource Languages" - NeurIPS 2020<br/>'
        '• <b>Open Source:</b> Contributor to Hugging Face Transformers library (1000+ stars)<br/>'
        '• <b>Kaggle:</b> Competitions Expert with 3 gold medals and top 1% ranking<br/>'
        '• <b>Blog:</b> Technical ML blog with 50K+ monthly readers on Medium',
        normal_style
    ))
    
    doc.build(story)
    print(f'✅ ML Resume PDF created successfully at: {pdf_path}')
    print(f'📄 File size: {os.path.getsize(pdf_path)} bytes')
    return pdf_path

if __name__ == '__main__':
    create_ml_resume()
