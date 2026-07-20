#!/usr/bin/env python3
"""Anatomy Quiz Master - Interactive anatomy quiz generator for medical education.

This skill generates interactive anatomy quizzes covering gross anatomy, 
neuroanatomy, and clinical correlations for medical education and exam preparation.
"""

import argparse
import random
import json
import sys
from typing import Dict, List, Optional
from pathlib import Path


class AnatomyQuizMaster:
    """Generates anatomy questions for medical education."""
    
    QUESTION_BANK = {
        "upper_limb": [
            {
                "question": "Which nerve is compressed in carpal tunnel syndrome?",
                "options": ["Median nerve", "Ulnar nerve", "Radial nerve", "Musculocutaneous nerve"],
                "correct": "Median nerve",
                "explanation": "The median nerve passes through the carpal tunnel and is compressed by transverse ligament.",
                "clinical": "Patients present with numbness in thumb, index, middle fingers (median nerve distribution)."
            },
            {
                "question": "The rotator cuff consists of all EXCEPT:",
                "options": ["Supraspinatus", "Infraspinatus", "Teres major", "Subscapularis"],
                "correct": "Teres major",
                "explanation": "Rotator cuff = SITS: Supraspinatus, Infraspinatus, Teres minor, Subscapularis.",
                "clinical": "Rotator cuff tears are common in overhead athletes and elderly."
            }
        ],
        "lower_limb": [
            {
                "question": "Which muscle is the primary hip flexor?",
                "options": ["Iliopsoas", "Rectus femoris", "Sartorius", "Tensor fasciae latae"],
                "correct": "Iliopsoas",
                "explanation": "Iliopsoas (iliacus + psoas major) is the strongest hip flexor.",
                "clinical": "Iliopsoas abscess can present with flexed hip posture to reduce pain."
            }
        ],
        "neuroanatomy": [
            {
                "question": "A lesion of the left optic tract results in:",
                "options": ["Right homonymous hemianopia", "Left homonymous hemianopia", "Bitemporal hemianopia", "Total blindness left eye"],
                "correct": "Right homonymous hemianopia",
                "explanation": "Optic tract carries fibers from both eyes for contralateral visual field.",
                "clinical": "Homonymous hemianopia suggests lesion posterior to optic chiasm."
            }
        ],
        "thorax": [
            {
                "question": "The thoracic duct drains lymph into the:",
                "options": ["Left subclavian vein", "Right subclavian vein", "Superior vena cava", "Azygos vein"],
                "correct": "Left subclavian vein",
                "explanation": "Thoracic duct drains most of body, empties at junction of left subclavian and internal jugular.",
                "clinical": "Thoracic duct injury during surgery causes chylothorax."
            }
        ],
        "abdomen": [
            {
                "question": "Which structure passes through the esophageal hiatus?",
                "options": ["Esophagus and vagus nerves", "Aorta", "Inferior vena cava", "Thoracic duct"],
                "correct": "Esophagus and vagus nerves",
                "explanation": "Esophageal hiatus at T10 transmits esophagus and anterior/posterior vagal trunks.",
                "clinical": "Hiatal hernia can cause GERD symptoms."
            }
        ],
        "head_neck": [
            {
                "question": "Which cranial nerve exits through the foramen rotundum?",
                "options": ["Maxillary division of trigeminal (V2)", "Mandibular division (V3)", "Ophthalmic division (V1)", "Facial nerve"],
                "correct": "Maxillary division of trigeminal (V2)",
                "explanation": "Foramen rotundum transmits maxillary nerve (V2) to pterygopalatine fossa.",
                "clinical": "V2 block used for maxillary sinus and dental procedures."
            }
        ],
        "pelvis": [
            {
                "question": "The ureter crosses the iliac vessels at the level of:",
                "options": ["Bifurcation of common iliac artery", "Sacral promontory", "Ischial spine", "Pubic symphysis"],
                "correct": "Bifurcation of common iliac artery",
                "explanation": "Ureter crosses anterior to bifurcation of common iliac into external and internal iliac.",
                "clinical": "Ureter vulnerable during pelvic surgeries, especially hysterectomy."
            }
        ]
    }
    
    DIFFICULTY_LEVELS = ["basic", "intermediate", "advanced"]
    
    def __init__(self):
        """Initialize quiz master."""
        pass
    
    def get_question(self, region: str = "upper_limb", difficulty: str = "intermediate") -> Dict:
        """Generate random anatomy question."""
        questions = self.QUESTION_BANK.get(region, self.QUESTION_BANK["upper_limb"])
        q = random.choice(questions)
        
        return {
            "question": q["question"],
            "options": q["options"],
            "correct_answer": q["correct"],
            "explanation": q["explanation"],
            "clinical_note": q.get("clinical", ""),
            "difficulty": difficulty,
            "region": region
        }
    
    def get_multiple_questions(self, region: str = "upper_limb", difficulty: str = "intermediate", count: int = 5) -> List[Dict]:
        """Generate multiple questions without repetition."""
        questions = self.QUESTION_BANK.get(region, self.QUESTION_BANK["upper_limb"])
        selected = random.sample(questions, min(count, len(questions)))
        
        results = []
        for q in selected:
            results.append({
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct"],
                "explanation": q["explanation"],
                "clinical_note": q.get("clinical", ""),
                "difficulty": difficulty,
                "region": region
            })
        return results
    
    def list_regions(self) -> List[str]:
        """List available anatomical regions."""
        return list(self.QUESTION_BANK.keys())
    
    def list_difficulties(self) -> List[str]:
        """List available difficulty levels."""
        return self.DIFFICULTY_LEVELS.copy()


def main():
    parser = argparse.ArgumentParser(
        description="Anatomy Quiz Master - Generate interactive anatomy quizzes for medical education",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get single question
  python main.py --region upper_limb
  
  # Generate 10-question quiz
  python main.py --region neuroanatomy --difficulty advanced --count 10 --output quiz.json
  
  # List all available regions
  python main.py --list-regions
        """
    )
    
    parser.add_argument(
        "--region", "-r",
        type=str,
        default="upper_limb",
        choices=["upper_limb", "lower_limb", "thorax", "abdomen", "pelvis", "head_neck", "neuroanatomy"],
        help="Anatomical region for quiz questions (default: upper_limb)"
    )
    
    parser.add_argument(
        "--difficulty", "-d",
        type=str,
        default="intermediate",
        choices=["basic", "intermediate", "advanced"],
        help="Difficulty level (default: intermediate)"
    )
    
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1,
        help="Number of questions to generate (default: 1)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (JSON format). If not specified, prints to stdout"
    )
    
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all available anatomical regions and exit"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)"
    )
    
    args = parser.parse_args()
    
    quiz = AnatomyQuizMaster()
    
    # Handle list regions
    if args.list_regions:
        regions = quiz.list_regions()
        print("Available anatomical regions:")
        for region in regions:
            print(f"  - {region}")
        return
    
    # Generate questions
    try:
        if args.count == 1:
            result: Dict = quiz.get_question(args.region, args.difficulty)
        else:
            result: List[Dict] = quiz.get_multiple_questions(args.region, args.difficulty, args.count)
        
        # Output results
        if args.format == "json":
            output = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Text format for human reading
            if args.count == 1:
                question_data = result
                output = f"""
Question: {question_data['question']}
Options:
"""
                for i, opt in enumerate(question_data['options'], 1):
                    output += f"  {i}. {opt}\n"
                output += f"\nCorrect Answer: {question_data['correct_answer']}\n"
                output += f"Explanation: {question_data['explanation']}\n"
                if question_data['clinical_note']:
                    output += f"Clinical Note: {question_data['clinical_note']}\n"
            else:
                questions_list = result
                output = f"Generated {len(questions_list)} questions for {args.region}:\n\n"
                for i, q in enumerate(questions_list, 1):
                    output += f"Q{i}: {q['question']}\n"
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Quiz saved to: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
