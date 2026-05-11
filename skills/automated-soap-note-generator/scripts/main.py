#!/usr/bin/env python3
"""
Automated SOAP Note Generator

Transforms unstructured clinical notes/dictation into standardized SOAP format.
Uses medical NLP techniques for entity extraction and section classification.

Usage:
    python main.py --input "clinical text" --output output.md
    python main.py --audio consultation.wav --output output.md
"""

import argparse
import re
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class SOAPSection(Enum):
    """SOAP note sections."""
    SUBJECTIVE = "Subjective"
    OBJECTIVE = "Objective"
    ASSESSMENT = "Assessment"
    PLAN = "Plan"


@dataclass
class MedicalEntity:
    """Represents a medical entity extracted from text."""
    text: str
    label: str  # e.g., 'SYMPTOM', 'DIAGNOSIS', 'MEDICATION', 'PROCEDURE'
    start: int
    end: int
    attributes: Dict = None


@dataclass
class SOAPNote:
    """Structured SOAP note data class."""
    patient_id: Optional[str]
    encounter_date: Optional[str]
    provider: Optional[str]
    subjective: str
    objective: str
    assessment: str
    plan: str
    raw_input: str = ""
    entities: List[MedicalEntity] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "patient_id": self.patient_id,
            "encounter_date": self.encounter_date,
            "provider": self.provider,
            "subjective": self.subjective,
            "objective": self.objective,
            "assessment": self.assessment,
            "plan": self.plan,
            "raw_input": self.raw_input,
            "entities": [asdict(e) for e in (self.entities or [])]
        }

    def to_markdown(self) -> str:
        """Generate formatted SOAP note in markdown."""
        md = ["# SOAP Note"]
        
        if self.patient_id:
            md.append(f"**Patient ID:** {self.patient_id}")
        if self.encounter_date:
            md.append(f"**Date:** {self.encounter_date}")
        if self.provider:
            md.append(f"**Provider:** {self.provider}")
        
        md.append("")
        md.append("## Subjective")
        md.append(self.subjective or "No subjective information provided.")
        
        md.append("")
        md.append("## Objective")
        md.append(self.objective or "No objective findings documented.")
        
        md.append("")
        md.append("## Assessment")
        md.append(self.assessment or "Assessment pending.")
        
        md.append("")
        md.append("## Plan")
        md.append(self.plan or "Plan to be determined.")
        
        return "\n".join(md)


class MedicalNLPProcessor:
    """Medical NLP processing utilities."""
    
    # Medical terminology patterns for rule-based extraction
    SYMPTOM_KEYWORDS = [
        "pain", "ache", "discomfort", "nausea", "vomiting", "fever", "chills",
        "headache", "dizziness", "fatigue", "weakness", "numbness", "tingling",
        "shortness of breath", "cough", "sore throat", "congestion", "rash",
        "swelling", "bruising", "bleeding", "diarrhea", "constipation"
    ]
    
    DIAGNOSIS_KEYWORDS = [
        "diagnosed with", "diagnosis", "condition", "disease", "disorder",
        "infection", "syndrome", "hypertension", "diabetes", "asthma",
        "pneumonia", "bronchitis", "migraine", "arthritis"
    ]
    
    MEDICATION_KEYWORDS = [
        "prescribed", "medication", "drug", "mg", "tablet", "capsule",
        "aspirin", "ibuprofen", "acetaminophen", "antibiotic", "insulin",
        "lisinopril", "metformin", "omeprazole", "amlodipine"
    ]
    
    PROCEDURE_KEYWORDS = [
        "procedure", "surgery", "operation", "biopsy", "x-ray", "mri",
        "ct scan", "ultrasound", "blood test", "urinalysis", "ecg", "ekg"
    ]
    
    VITAL_SIGN_PATTERNS = {
        "bp": r"\b(?:BP|blood pressure)[\s:]*?(\d{2,3})/(\d{2,3})\b",
        "hr": r"\b(?:HR|heart rate|pulse)[\s:]*?(\d{2,3})\b",
        "rr": r"\b(?:RR|respiratory rate)[\s:]*?(\d{1,2})\b",
        "temp": r"\b(?:temp|temperature)[\s:]*?(\d{2}\.?\d?)[°\s]*(?:F|C)?\b",
        "spo2": r"\b(?:SpO2|oxygen saturation)[\s:]*?(\d{2,3})%?\b",
        "weight": r"\b(?:weight|wt)[\s:]*?(\d{2,3}(?:\.\d)?)\s*(?:kg|lbs?)\b"
    }
    
    NEGATION_PATTERNS = [
        r"\bno\s+(\w+)",
        r"\bdenies\s+(\w+)",
        r"\bdenied\s+(\w+)",
        r"\bwithout\s+(\w+)",
        r"\bnot\s+\w+\s+(\w+)"
    ]

    def extract_entities(self, text: str) -> List[MedicalEntity]:
        """Extract medical entities from text."""
        entities = []
        text_lower = text.lower()
        
        # Extract symptoms
        for symptom in self.SYMPTOM_KEYWORDS:
            for match in re.finditer(r'\b' + re.escape(symptom) + r'\b', text_lower):
                start = match.start()
                end = match.end()
                entities.append(MedicalEntity(
                    text=text[start:end],
                    label="SYMPTOM",
                    start=start,
                    end=end
                ))
        
        # Extract medications
        for med in self.MEDICATION_KEYWORDS:
            for match in re.finditer(r'\b' + re.escape(med) + r'\b', text_lower):
                start = match.start()
                end = match.end()
                entities.append(MedicalEntity(
                    text=text[start:end],
                    label="MEDICATION",
                    start=start,
                    end=end
                ))
        
        # Extract diagnoses
        for diag in self.DIAGNOSIS_KEYWORDS:
            for match in re.finditer(r'\b' + re.escape(diag) + r'\b', text_lower):
                start = match.start()
                end = match.end()
                entities.append(MedicalEntity(
                    text=text[start:end],
                    label="DIAGNOSIS",
                    start=start,
                    end=end
                ))
        
        # Extract procedures
        for proc in self.PROCEDURE_KEYWORDS:
            for match in re.finditer(r'\b' + re.escape(proc) + r'\b', text_lower):
                start = match.start()
                end = match.end()
                entities.append(MedicalEntity(
                    text=text[start:end],
                    label="PROCEDURE",
                    start=start,
                    end=end
                ))
        
        return entities
    
    def extract_vital_signs(self, text: str) -> Dict[str, str]:
        """Extract vital signs from text."""
        vitals = {}
        for vital_name, pattern in self.VITAL_SIGN_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                vitals[vital_name] = matches[0] if isinstance(matches[0], str) else f"{matches[0][0]}/{matches[0][1]}"
        return vitals
    
    def detect_negation(self, text: str) -> List[str]:
        """Detect negated findings."""
        negated = []
        for pattern in self.NEGATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            negated.extend(matches)
        return negated


class SOAPNoteGenerator:
    """Main SOAP note generator class."""
    
    # Section classification keywords
    SUBJECTIVE_INDICATORS = [
        "patient reports", "patient states", "patient complains", "c/o",
        "history of", "h/o", "symptoms", "feels", "experiencing",
        "onset", "duration", "frequency", "severity", "character",
        "aggravated by", "relieved by", "associated with", "denies"
    ]
    
    OBJECTIVE_INDICATORS = [
        "exam reveals", "physical exam", "vital signs", "vitals",
        "bp", "blood pressure", "heart rate", "pulse", "respiratory rate",
        "temperature", "afebrile", "alert", "oriented", "mucous membranes",
        "lungs clear", "heart regular", "abdomen soft", "no tenderness"
    ]
    
    ASSESSMENT_INDICATORS = [
        "assessment", "impression", "diagnosis", "differential",
        "likely", "probable", "suspected", "appears to be", "consistent with",
        "rule out", "r/o", "possible", "consider", "most likely"
    ]
    
    PLAN_INDICATORS = [
        "plan", "will", "continue", "start", "initiate", "discontinue",
        "prescribe", "refer", "follow up", "follow-up", "return",
        "monitor", "recheck", "labs", "imaging", "schedule"
    ]
    
    def __init__(self):
        self.nlp = MedicalNLPProcessor()
    
    def classify_section(self, sentence: str) -> SOAPSection:
        """Classify which SOAP section a sentence belongs to."""
        sentence_lower = sentence.lower()
        
        scores = {
            SOAPSection.SUBJECTIVE: 0,
            SOAPSection.OBJECTIVE: 0,
            SOAPSection.ASSESSMENT: 0,
            SOAPSection.PLAN: 0
        }
        
        # Score each section
        for indicator in self.SUBJECTIVE_INDICATORS:
            if indicator in sentence_lower:
                scores[SOAPSection.SUBJECTIVE] += 1
        
        for indicator in self.OBJECTIVE_INDICATORS:
            if indicator in sentence_lower:
                scores[SOAPSection.OBJECTIVE] += 1
        
        for indicator in self.ASSESSMENT_INDICATORS:
            if indicator in sentence_lower:
                scores[SOAPSection.ASSESSMENT] += 1
        
        for indicator in self.PLAN_INDICATORS:
            if indicator in sentence_lower:
                scores[SOAPSection.PLAN] += 1
        
        return max(scores, key=scores.get)
    
    def parse_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_subjective(self, text: str, sentences: List[str]) -> str:
        """Extract subjective section content."""
        subjective_sentences = []
        
        for sentence in sentences:
            if self.classify_section(sentence) == SOAPSection.SUBJECTIVE:
                subjective_sentences.append(sentence)
        
        # If no subjective section detected, look for patient-reported content
        if not subjective_sentences:
            for sentence in sentences:
                lower = sentence.lower()
                if any(x in lower for x in ["patient", "pt", "reports", "states", "complains"]):
                    subjective_sentences.append(sentence)
        
        return " ".join(subjective_sentences) if subjective_sentences else ""
    
    def extract_objective(self, text: str, sentences: List[str]) -> str:
        """Extract objective section content."""
        objective_sentences = []
        
        for sentence in sentences:
            if self.classify_section(sentence) == SOAPSection.OBJECTIVE:
                objective_sentences.append(sentence)
        
        # Add vital signs if found
        vitals = self.nlp.extract_vital_signs(text)
        if vitals:
            vital_text = "Vital signs: " + ", ".join([f"{k}: {v}" for k, v in vitals.items()])
            objective_sentences.insert(0, vital_text)
        
        return " ".join(objective_sentences) if objective_sentences else ""
    
    def extract_assessment(self, text: str, sentences: List[str]) -> str:
        """Extract assessment section content."""
        assessment_sentences = []
        
        for sentence in sentences:
            if self.classify_section(sentence) == SOAPSection.ASSESSMENT:
                assessment_sentences.append(sentence)
        
        # Look for diagnosis patterns
        if not assessment_sentences:
            for sentence in sentences:
                lower = sentence.lower()
                if any(x in lower for x in ["diagnosis", "impression", "assessment", "likely"]):
                    assessment_sentences.append(sentence)
        
        return " ".join(assessment_sentences) if assessment_sentences else ""
    
    def extract_plan(self, text: str, sentences: List[str]) -> str:
        """Extract plan section content."""
        plan_sentences = []
        
        for sentence in sentences:
            if self.classify_section(sentence) == SOAPSection.PLAN:
                plan_sentences.append(sentence)
        
        # Look for medication/treatment patterns
        if not plan_sentences:
            for sentence in sentences:
                lower = sentence.lower()
                if any(x in lower for x in ["prescribed", "started", "continue", "follow up"]):
                    plan_sentences.append(sentence)
        
        return " ".join(plan_sentences) if plan_sentences else ""
    
    def generate(self, input_text: str, patient_id: Optional[str] = None,
                 encounter_date: Optional[str] = None,
                 provider: Optional[str] = None) -> SOAPNote:
        """
        Generate a SOAP note from unstructured clinical text.
        
        Args:
            input_text: Raw clinical text/dictation
            patient_id: Patient identifier
            encounter_date: Date of encounter
            provider: Healthcare provider name
            
        Returns:
            SOAPNote object with structured sections
        """
        # Parse sentences
        sentences = self.parse_sentences(input_text)
        
        # Extract entities
        entities = self.nlp.extract_entities(input_text)
        
        # Extract each section
        subjective = self.extract_subjective(input_text, sentences)
        objective = self.extract_objective(input_text, sentences)
        assessment = self.extract_assessment(input_text, sentences)
        plan = self.extract_plan(input_text, sentences)
        
        return SOAPNote(
            patient_id=patient_id,
            encounter_date=encounter_date or datetime.now().strftime("%Y-%m-%d"),
            provider=provider,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
            raw_input=input_text,
            entities=entities
        )
    
    def generate_from_audio(self, audio_path: str, **kwargs) -> SOAPNote:
        """
        Generate SOAP note from audio file (placeholder - requires ASR integration).
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional arguments for generate()
            
        Returns:
            SOAPNote object
        """
        # This is a placeholder - would integrate with ASR service
        raise NotImplementedError(
            "Audio transcription requires integration with ASR service. "
            "Use generate() with pre-transcribed text instead."
        )


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate SOAP notes from clinical text"
    )
    parser.add_argument("--input", "-i", help="Input clinical text")
    parser.add_argument("--input-file", "-f", help="Path to input text file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--patient-id", "-p", help="Patient identifier")
    parser.add_argument("--provider", help="Healthcare provider name")
    parser.add_argument("--format", choices=["markdown", "json"], 
                        default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    # Get input text
    if args.input:
        input_text = args.input
    elif args.input_file:
        with open(args.input_file, 'r') as f:
            input_text = f.read()
    else:
        # Demo mode with sample input
        input_text = (
            "Patient is a 45-year-old male presenting with chest pain for 2 hours. "
            "Pain is 8/10, crushing quality, radiates to left arm. "
            "Patient reports shortness of breath and diaphoresis. "
            "Vital signs: BP 160/95, HR 105, RR 22, Temp 98.6F. "
            "Physical exam reveals diaphoretic patient, chest clear bilaterally. "
            "Assessment: Acute coronary syndrome, possible STEMI. "
            "Plan: Activate cath lab, give aspirin 325mg, nitroglycerin 0.4mg SL."
        )
        print("Demo mode - using sample input...\n")
    
    # Generate SOAP note
    generator = SOAPNoteGenerator()
    soap_note = generator.generate(
        input_text=input_text,
        patient_id=args.patient_id,
        provider=args.provider
    )
    
    # Format output
    if args.format == "json":
        output = json.dumps(soap_note.to_dict(), indent=2)
    else:
        output = soap_note.to_markdown()
    
    # Write or print output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"SOAP note written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
