#!/usr/bin/env python3
"""
Script to create test PDFs with vocabulary words for different grade levels
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

# Create test_pdfs directory if it doesn't exist
os.makedirs("test_pdfs", exist_ok=True)

# Word lists for each difficulty level
word_lists = {
    "grade2_words.pdf": {
        "title": "Grade 2 Level Words",
        "words": ["cat", "dog", "run", "jump", "happy", "ball", "tree", "book", "play", "house", 
                 "water", "food", "friend", "smile", "blue", "red", "big", "small", "fast", "slow"]
    },
    "grade3_easy_words.pdf": {
        "title": "Grade 3 Easy Words", 
        "words": ["animal", "school", "teacher", "student", "family", "garden", "flower", "summer", "winter", "music",
                 "picture", "story", "laugh", "bright", "quiet", "careful", "helpful", "important", "different", "favorite"]
    },
    "grade3_medium_words.pdf": {
        "title": "Grade 3 Medium Words",
        "words": ["adventure", "butterfly", "celebrate", "discovery", "elephant", "fantastic", "generous", "hospital", "invention", "journey",
                 "kindness", "library", "mountain", "neighborhood", "ordinary", "perfect", "question", "remember", "surprise", "treasure"]
    },
    "grade3_hard_words.pdf": {
        "title": "Grade 3 Hard Words",
        "words": ["appreciate", "boundary", "communicate", "demonstrate", "environment", "fascinating", "geography", "historical", "incredible", "journalism",
                 "knowledge", "literature", "magnificent", "necessary", "opportunity", "personality", "qualification", "responsibility", "spectacular", "temperature"]
    },
    "grade3_toughest_words.pdf": {
        "title": "Grade 3 Toughest Words",
        "words": ["accomplished", "bewildering", "catastrophe", "determination", "extraordinary", "fundamental", "generalization", "hypothesis", "illustration", "jeopardize",
                 "kindergarten", "laboratory", "multiplication", "negotiation", "observation", "phenomenon", "questionnaire", "recommendation", "significance", "transformation"]
    }
}

def create_pdf(filename, title, words):
    """Create a PDF with the given title and word list"""
    doc = SimpleDocTemplate(f"test_pdfs/{filename}", pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    word_style = ParagraphStyle(
        'WordStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=12
    )
    
    # Build the document
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add words with numbering
    for i, word in enumerate(words, 1):
        story.append(Paragraph(f"{i}. {word}", word_style))
    
    # Build PDF
    doc.build(story)
    print(f"Created: test_pdfs/{filename}")

# Create all PDFs
for filename, data in word_lists.items():
    create_pdf(filename, data["title"], data["words"])

print("\n✅ All 5 test PDFs created successfully!")
print("Files created in test_pdfs/ directory:")
for filename in word_lists.keys():
    print(f"  - {filename}")
