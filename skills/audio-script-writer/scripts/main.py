#!/usr/bin/env python3
"""Audio Script Writer - Converts written content to audio-optimized scripts.

This skill transforms written medical/scientific content into scripts optimized 
for audio delivery (podcasts, videos, presentations).
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


class AudioScriptWriter:
    """Converts written content to audio scripts optimized for spoken delivery."""
    
    # Standard speaking rates
    WORDS_PER_MINUTE = {
        "slow": 130,
        "normal": 150,
        "fast": 170
    }
    
    # Text replacements for spoken word
    ABBREVIATIONS = {
        "e.g.": "for example",
        "i.e.": "that is",
        "etc.": "and so on",
        "vs.": "versus",
        "Dr.": "Doctor",
        "Prof.": "Professor",
        "Mr.": "Mister",
        "Ms.": "Miss",
        "Mrs.": "Missus",
        "No.": "Number",
        "Fig.": "Figure",
        "et al.": "and colleagues",
        "ibid.": "as previously mentioned"
    }
    
    def __init__(self, style: str = "conversational"):
        """Initialize with style preference."""
        self.style = style
        
    def convert(self, content: str, duration: int = 5, pace: str = "normal") -> Dict:
        """Convert text to audio script.
        
        Args:
            content: Input text content
            duration: Target duration in minutes
            pace: Speaking pace (slow, normal, fast)
            
        Returns:
            Dictionary with script and metadata
        """
        # Calculate target word count
        wpm = self.WORDS_PER_MINUTE.get(pace, 150)
        target_words = duration * wpm
        
        # Preprocess for spoken word
        script = self._preprocess_for_audio(content)
        
        # Truncate to target length if needed
        words = script.split()
        if len(words) > target_words:
            # Find natural break point
            truncated = words[:target_words]
            # Try to end at sentence
            for i in range(len(truncated) - 1, max(0, len(truncated) - 50), -1):
                if truncated[i].endswith(('.', '!', '?')):
                    truncated = truncated[:i+1]
                    break
            script = ' '.join(truncated)
        
        # Add style-specific formatting
        script = self._apply_style(script)
        
        # Generate pronunciation notes
        pronunciation_notes = self._extract_pronunciation_notes(content)
        
        actual_word_count = len(script.split())
        estimated_duration = actual_word_count / wpm
        
        return {
            "script": script,
            "metadata": {
                "target_duration_minutes": duration,
                "estimated_duration_minutes": round(estimated_duration, 1),
                "word_count": actual_word_count,
                "speaking_pace": pace,
                "style": self.style
            },
            "pronunciation_notes": pronunciation_notes,
            "formatting_notes": self._generate_formatting_notes()
        }
    
    def _preprocess_for_audio(self, text: str) -> str:
        """Preprocess text for audio delivery."""
        # Replace abbreviations
        for abbrev, spoken in self.ABBREVIATIONS.items():
            text = text.replace(abbrev, spoken)
        
        # Remove citations [1], [2,3]
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        
        # Convert numbers to words for small numbers
        text = self._numbers_to_words(text)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _numbers_to_words(self, text: str) -> str:
        """Convert small numbers to words for better flow."""
        number_words = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
            "10": "ten", "11": "eleven", "12": "twelve"
        }
        
        # Replace standalone small numbers
        for num, word in number_words.items():
            # Use word boundaries to avoid replacing parts of other words
            text = re.sub(r'\b' + num + r'\b', word, text)
        
        return text
    
    def _apply_style(self, script: str) -> str:
        """Apply style-specific formatting."""
        if self.style == "conversational":
            # Add conversational transitions
            script = script.replace("Furthermore,", "Also,")
            script = script.replace("However,", "But,")
            script = script.replace("Therefore,", "So,")
            script = script.replace("In conclusion,", "To wrap up,")
            
        elif self.style == "formal":
            # Keep formal but simplify
            script = script.replace("utilize", "use")
            script = script.replace("demonstrate", "show")
            script = script.replace("investigate", "study")
            
        elif self.style == "educational":
            # Add explanatory phrases
            sentences = script.split('. ')
            enhanced = []
            for sent in sentences:
                if any(term in sent.lower() for term in ['study', 'research', 'found']):
                    sent = "Research shows that " + sent[0].lower() + sent[1:]
                enhanced.append(sent)
            script = '. '.join(enhanced)
        
        return script
    
    def _extract_pronunciation_notes(self, text: str) -> List[str]:
        """Extract medical/scientific terms that may need pronunciation guidance."""
        notes = []
        
        # Common medical terms that are often mispronounced
        medical_terms = {
            r'\bmyocardial\b': "my-oh-KAR-dee-al",
            r'\bantihypertensive\b': "an-tee-hy-per-TEN-siv",
            r'\bhypercholesterolemia\b': "HY-per-koh-LES-ter-ol-EE-mee-ah",
            r'\bpharmacokinetics\b': "far-mah-koh-kih-NET-iks",
            r'\bmetastasis\b': "meh-TAS-tah-sis",
            r'\bautoimmune\b': "aw-toh-ih-MYOON",
            r'\bpathophysiology\b': "path-oh-fiz-ee-OL-oh-jee"
        }
        
        for pattern, pronunciation in medical_terms.items():
            if re.search(pattern, text, re.IGNORECASE):
                term = pattern.replace(r'\b', '').replace(r'\b', '')
                notes.append(f"{term}: {pronunciation}")
        
        return notes if notes else ["No complex medical terms requiring pronunciation guidance"]
    
    def _generate_formatting_notes(self) -> List[str]:
        """Generate formatting notes for the script."""
        notes = [
            "[PAUSE] - Insert 1-second pause",
            "[EMPHASIS] - Emphasize this word/phrase",
            "[SLOW] - Slow down for clarity",
            "--- - Section break"
        ]
        return notes


def main():
    parser = argparse.ArgumentParser(
        description="Audio Script Writer - Convert written content to audio-optimized scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert from file
  python main.py --input article.txt --duration 5 --output script.json
  
  # Convert with specific style
  python main.py --input paper.txt --style educational --pace slow
  
  # Quick conversion from stdin
  cat article.txt | python main.py --duration 3
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input text file path"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output JSON file path (default: print to stdout)"
    )
    
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=5,
        help="Target duration in minutes (default: 5)"
    )
    
    parser.add_argument(
        "--pace", "-p",
        type=str,
        choices=["slow", "normal", "fast"],
        default="normal",
        help="Speaking pace (default: normal)"
    )
    
    parser.add_argument(
        "--style", "-s",
        type=str,
        choices=["conversational", "formal", "educational"],
        default="conversational",
        help="Script style (default: conversational)"
    )
    
    parser.add_argument(
        "--text",
        type=str,
        help="Direct text input (alternative to --input)"
    )
    
    args = parser.parse_args()
    
    # Get input content
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        content = args.text
    else:
        # Read from stdin
        content = sys.stdin.read()
        if not content:
            print("Error: No input provided. Use --input, --text, or pipe content via stdin.", file=sys.stderr)
            sys.exit(1)
    
    # Convert to audio script
    writer = AudioScriptWriter(style=args.style)
    result = writer.convert(content, duration=args.duration, pace=args.pace)
    
    # Output results
    output = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Script saved to: {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
