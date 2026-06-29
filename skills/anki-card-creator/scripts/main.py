#!/usr/bin/env python3
"""
Anki Card Creator
Convert medical content into Anki flashcards.
"""

import argparse
import re


class AnkiCardCreator:
    """Create Anki flashcards from medical content."""
    
    def parse_text(self, text):
        """Parse input text into question-answer pairs."""
        cards = []
        
        # Simple parsing - look for Q: and A: patterns
        lines = text.strip().split('\n')
        current_q = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:') or line.startswith('Question:'):
                current_q = line.split(':', 1)[1].strip()
            elif line.startswith('A:') or line.startswith('Answer:'):
                if current_q:
                    answer = line.split(':', 1)[1].strip()
                    cards.append((current_q, answer))
                    current_q = None
        
        return cards
    
    def create_drug_card(self, drug_name, mechanism, indications, side_effects):
        """Create drug information card."""
        front = f"<b>{drug_name}</b><br><br>Mechanism of action?"
        back = f"<b>{drug_name}</b><br>{mechanism}<br><br>Indications: {indications}<br>Side effects: {side_effects}"
        return front, back
    
    def create_anatomy_card(self, structure, location, function):
        """Create anatomy card."""
        front = f"<b>{structure}</b><br><br>Location and function?"
        back = f"<b>{structure}</b><br>Location: {location}<br>Function: {function}"
        return front, back
    
    def export_anki_format(self, cards, output_file):
        """Export cards in Anki import format (TSV)."""
        with open(output_file, 'w') as f:
            for front, back in cards:
                # Escape tabs and newlines
                front = front.replace('\t', ' ').replace('\n', '<br>')
                back = back.replace('\t', ' ').replace('\n', '<br>')
                f.write(f"{front}\t{back}\n")
    
    def print_cards(self, cards):
        """Print cards for review."""
        print(f"\n{'='*60}")
        print(f"GENERATED {len(cards)} ANKI CARDS")
        print(f"{'='*60}")
        
        for i, (front, back) in enumerate(cards, 1):
            print(f"\nCard {i}:")
            print(f"  Front: {front[:60]}...")
            print(f"  Back:  {back[:60]}...")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Anki Card Creator")
    parser.add_argument("--input", "-i", help="Input text file")
    parser.add_argument("--output", "-o", default="anki_cards.txt",
                       help="Output file (Anki format)")
    parser.add_argument("--drug", action="store_true", help="Create drug card")
    parser.add_argument("--anatomy", action="store_true", help="Create anatomy card")
    parser.add_argument("--name", help="Drug/structure name")
    parser.add_argument("--mechanism", help="Mechanism of action")
    parser.add_argument("--indications", help="Indications")
    parser.add_argument("--side-effects", help="Side effects")
    parser.add_argument("--location", help="Anatomical location")
    parser.add_argument("--function", help="Function")
    
    args = parser.parse_args()
    
    creator = AnkiCardCreator()
    cards = []
    
    if args.drug and args.name:
        card = creator.create_drug_card(
            args.name,
            args.mechanism or "See notes",
            args.indications or "Various",
            args.side_effects or "See notes"
        )
        cards.append(card)
    elif args.anatomy and args.name:
        card = creator.create_anatomy_card(
            args.name,
            args.location or "See notes",
            args.function or "See notes"
        )
        cards.append(card)
    elif args.input:
        with open(args.input) as f:
            text = f.read()
        cards = creator.parse_text(text)
    else:
        # Demo
        cards = [
            ("What is the mechanism of Metformin?", 
             "Inhibits hepatic gluconeogenesis and increases insulin sensitivity"),
            ("What are the cranial nerves?",
             "I Olfactory, II Optic, III Oculomotor, IV Trochlear, V Trigeminal...")
        ]
    
    creator.print_cards(cards)
    creator.export_anki_format(cards, args.output)
    print(f"Cards exported to: {args.output}")
    print("Import this file into Anki: File → Import")


if __name__ == "__main__":
    main()
