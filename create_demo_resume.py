#!/usr/bin/env python3
"""
Create a professional demo resume PDF for testing the OptiHire application
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

def create_demo_resume():
    """Create a professional resume PDF"""
    
    # Ensure uploads directory exists
    os.makedirs('uploads', exist_ok=True)
    
    # Create PDF
    pdf_path = 'uploads/demo_resume_john_smith.pdf'
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Header
    story.append(Paragraph('JOHN SMITH', title_style))
    story.append(Paragraph(
        'Senior Full Stack Developer',
        ParagraphStyle(
            'Subtitle',
            parent=normal_style,
            fontSize=12,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_CENTER
        )
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Contact Info
    contact_data = [[
        'Email: john.smith.dev@email.com',
        'Phone: +1 (555) 234-5678',
        'Location: San Francisco, CA'
    ]]
    contact_table = Table(contact_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#4a5568'))
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Professional Summary
    story.append(Paragraph('PROFESSIONAL SUMMARY', heading_style))
    story.append(Paragraph(
        'Experienced Full Stack Software Engineer with 6+ years of expertise in designing and '
        'developing scalable web applications. Proficient in modern JavaScript frameworks, Python, '
        'and cloud technologies. Proven track record of delivering high-quality solutions in '
        'fast-paced environments. Strong problem-solver with excellent collaboration skills.',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Technical Skills
    story.append(Paragraph('TECHNICAL SKILLS', heading_style))
    skills_text = '''
    <b>Languages:</b> Python, JavaScript, TypeScript, HTML5, CSS3, SQL<br/>
    <b>Frontend:</b> React, Redux, Next.js, Vue.js, Tailwind CSS, Material-UI<br/>
    <b>Backend:</b> Node.js, Express, Django, Flask, FastAPI, REST API, GraphQL<br/>
    <b>Databases:</b> PostgreSQL, MongoDB, MySQL, Redis<br/>
    <b>Cloud &amp; DevOps:</b> AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes, CI/CD, Jenkins<br/>
    <b>Tools:</b> Git, GitHub, GitLab, Jira, Agile/Scrum
    '''
    story.append(Paragraph(skills_text, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Professional Experience
    story.append(Paragraph('PROFESSIONAL EXPERIENCE', heading_style))
    
    # Job 1
    story.append(Paragraph(
        '<b>Senior Software Engineer</b> | TechVision Inc. | San Francisco, CA<br/>'
        '<i>January 2021 - Present</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Led development of microservices architecture serving 2M+ users, improving system performance by 40%<br/>'
        '• Architected and implemented React-based dashboard with real-time data visualization<br/>'
        '• Mentored team of 5 junior developers, conducting code reviews and technical training<br/>'
        '• Implemented CI/CD pipelines using Jenkins and Docker, reducing deployment time by 60%<br/>'
        '• Collaborated with product team to define technical requirements and roadmap',
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Job 2
    story.append(Paragraph(
        '<b>Full Stack Developer</b> | Digital Solutions Co. | Remote<br/>'
        '<i>March 2019 - December 2020</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Developed and maintained e-commerce platform using React, Node.js, and PostgreSQL<br/>'
        '• Built RESTful APIs handling 100K+ daily requests with 99.9% uptime<br/>'
        '• Optimized database queries, reducing page load times by 50%<br/>'
        '• Integrated third-party payment gateways and shipping APIs<br/>'
        '• Participated in agile sprints and daily standups',
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Job 3
    story.append(Paragraph(
        '<b>Junior Software Developer</b> | StartupHub | Austin, TX<br/>'
        '<i>June 2017 - February 2019</i>',
        normal_style
    ))
    story.append(Paragraph(
        '• Developed responsive web applications using JavaScript, HTML5, and CSS3<br/>'
        '• Implemented user authentication and authorization systems<br/>'
        '• Wrote unit and integration tests achieving 85% code coverage<br/>'
        '• Fixed bugs and implemented new features based on user feedback',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Education
    story.append(Paragraph('EDUCATION', heading_style))
    story.append(Paragraph(
        '<b>Bachelor of Science in Computer Science</b><br/>'
        'Stanford University | Graduated: May 2017<br/>'
        'GPA: 3.7/4.0',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Certifications
    story.append(Paragraph('CERTIFICATIONS', heading_style))
    story.append(Paragraph(
        '• AWS Certified Solutions Architect - Associate (2022)<br/>'
        '• Google Cloud Professional Developer (2021)<br/>'
        '• MongoDB Certified Developer (2020)',
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Projects
    story.append(Paragraph('PROJECTS &amp; ACHIEVEMENTS', heading_style))
    story.append(Paragraph(
        '• <b>Open Source Contributor:</b> Active contributor to React and Node.js communities (500+ GitHub stars)<br/>'
        '• <b>Hackathon Winner:</b> 1st place at TechCrunch Disrupt 2022 for AI-powered productivity app<br/>'
        '• <b>Tech Speaker:</b> Presented at React Conference 2023 on performance optimization',
        normal_style
    ))
    
    # Build PDF
    doc.build(story)
    print(f'✅ Resume PDF created successfully at: {pdf_path}')
    print(f'📄 File size: {os.path.getsize(pdf_path)} bytes')
    return pdf_path

if __name__ == '__main__':
    create_demo_resume()
