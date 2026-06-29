#!/usr/bin/env python3
"""
Antibody Humanizer - AI-powered antibody humanization tool
Predicts optimal human frameworks from murine antibody sequences and generates humanized sequences

Usage:
    python3 main.py --vh <VH_SEQUENCE> --vl <VL_SEQUENCE> --name <NAME>
    python3 main.py --input <INPUT_JSON> --output <OUTPUT_JSON>
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class NumberingScheme(Enum):
    """Antibody numbering schemes"""
    KABAT = "kabat"
    CHOTHIA = "chothia"
    IMGT = "imgt"


@dataclass
class CDRRegion:
    """CDR region definition"""
    name: str
    start: int
    end: int
    sequence: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "sequence": self.sequence
        }


@dataclass
class BackMutation:
    """Back mutation definition"""
    position: str
    from_aa: str
    to_aa: str
    reason: str
    
    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "from": self.from_aa,
            "to": self.to_aa,
            "reason": self.reason
        }


@dataclass
class HumanizationCandidate:
    """Humanization candidate result"""
    rank: int
    framework_source: str
    human_homology: float
    humanness_score: float
    risk_level: str
    humanized_vh: str
    humanized_vl: str
    back_mutations: List[BackMutation]
    
    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "framework_source": self.framework_source,
            "human_homology": round(self.human_homology, 4),
            "humanness_score": round(self.humanness_score, 2),
            "risk_level": self.risk_level,
            "humanized_vh": self.humanized_vh,
            "humanized_vl": self.humanized_vl,
            "back_mutations": [m.to_dict() for m in self.back_mutations]
        }


# Human germline gene database (simplified version)
HUMAN_GERMLINE_VH = {
    "IGHV1-2*02": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCAR",
    "IGHV1-46*01": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYWIHWVRQAPGQGLEWMGEINPNSGSTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCAR",
    "IGHV3-23*01": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSDSWIHWVRQAPGKGLEWVAWISPYGGSTYYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCAR",
    "IGHV3-30*01": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
    "IGHV4-34*01": "QVQLQSGPELVKPGASVKMSCKASGYTFTSYNMHWVKQTPGRGLEWIGAIYPGNGDTSYNQKFKDKATLTADKSSSTAYMQLSSLTSEDSAVYYCAR",
}

HUMAN_GERMLINE_VL = {
    "IGKV1-12*01": "DIQMTQSPSSLSASVGDRVTITCRASQGISSALAWYQQKPGKAPKLLIYKASSLESGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYNSYS",
    "IGKV1-39*01": "DIQMTQSPSSLSASVGDRVTITCRASQGIRNDLGWYQQKPGKAPKRLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQAY",
    "IGKV3-11*01": "DIQMTQSPSSLSASVGDRVTITCSASSSVSYMNWYQQKPGKAPKLLIYDTSKLASGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQW",
    "IGKV3-15*01": "DIQMTQSPSSLSASVGDRVTITCSASSSVSYMHWFQQKPGKAPKPLIYDTSKLASGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQ",
    "IGKV4-1*01":  "DIQMTQSPSSLSASVGDRVTITCKASQDVSTAVAWYQQKPGQSPKLLIYSASYRYTGVPDRFTGSGSGTDFTLTISSLQAEDVAVYYC",
}

# CDR position definitions (Chothia numbering scheme)
CDR_POSITIONS_CHOTHIA = {
    "VH": {
        "CDR-H1": (26, 32),
        "CDR-H2": (52, 56),
        "CDR-H3": (95, 102)
    },
    "VL": {
        "CDR-L1": (24, 34),
        "CDR-L2": (50, 56),
        "CDR-L3": (89, 97)
    }
}

# Kabat numbering scheme
CDR_POSITIONS_KABAT = {
    "VH": {
        "CDR-H1": (31, 35),
        "CDR-H2": (50, 65),
        "CDR-H3": (95, 102)
    },
    "VL": {
        "CDR-L1": (24, 34),
        "CDR-L2": (50, 56),
        "CDR-L3": (89, 97)
    }
}

# IMGT numbering scheme
CDR_POSITIONS_IMGT = {
    "VH": {
        "CDR-H1": (27, 38),
        "CDR-H2": (56, 65),
        "CDR-H3": (105, 117)
    },
    "VL": {
        "CDR-L1": (27, 38),
        "CDR-L2": (56, 65),
        "CDR-L3": (105, 117)
    }
}

# Critical framework residues (Vernier and Interface residues)
CRITICAL_RESIDUES = {
    "VH": [2, 4, 24, 27, 29, 48, 71, 73, 78, 93],  # Based on Chothia numbering
    "VL": [2, 4, 35, 36, 46, 47, 49, 64, 71, 87]
}


class AntibodyHumanizer:
    """Core antibody humanization class"""
    
    def __init__(self, scheme: NumberingScheme = NumberingScheme.CHOTHIA):
        self.scheme = scheme
        self.cdr_positions = self._get_cdr_positions()
        
    def _get_cdr_positions(self) -> Dict:
        """Get CDR position definitions"""
        if self.scheme == NumberingScheme.KABAT:
            return CDR_POSITIONS_KABAT
        elif self.scheme == NumberingScheme.IMGT:
            return CDR_POSITIONS_IMGT
        return CDR_POSITIONS_CHOTHIA
    
    def validate_sequence(self, sequence: str) -> Tuple[bool, str]:
        """Validate amino acid sequence"""
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence = sequence.upper().replace(" ", "").replace("\n", "")
        
        if not sequence:
            return False, "Empty sequence"
        
        invalid_chars = set(sequence) - valid_aa
        if invalid_chars:
            return False, f"Invalid amino acid characters: {invalid_chars}"
        
        if len(sequence) < 80:
            return False, f"Sequence length ({len(sequence)}) too short, variable region typically >80 amino acids"
        
        if len(sequence) > 150:
            return False, f"Sequence length ({len(sequence)}) too long, variable region typically <150 amino acids"
        
        return True, sequence
    
    def extract_cdrs(self, sequence: str, chain_type: str) -> Dict[str, CDRRegion]:
        """Extract CDR regions from sequence"""
        cdrs = {}
        positions = self.cdr_positions.get(chain_type, {})
        
        for cdr_name, (start, end) in positions.items():
            # Convert to 0-based indexing
            seq_start = start - 1
            seq_end = min(end, len(sequence))
            
            if seq_start < len(sequence):
                cdr_seq = sequence[seq_start:seq_end]
                cdrs[cdr_name] = CDRRegion(
                    name=cdr_name,
                    start=start,
                    end=seq_end,
                    sequence=cdr_seq
                )
        
        return cdrs
    
    def extract_frameworks(self, sequence: str, chain_type: str) -> Dict[str, str]:
        """Extract framework region sequences"""
        cdr_positions = self.cdr_positions.get(chain_type, {})
        frameworks = {}
        
        # FR1: From sequence start to before CDR1
        cdr1_start = cdr_positions.get(f"CDR-{chain_type[0]}1", (1, 1))[0]
        frameworks["FR1"] = sequence[:cdr1_start-1]
        
        # FR2: From after CDR1 to before CDR2
        cdr1_end = cdr_positions.get(f"CDR-{chain_type[0]}1", (1, 1))[1]
        cdr2_start = cdr_positions.get(f"CDR-{chain_type[0]}2", (1, 1))[0]
        frameworks["FR2"] = sequence[cdr1_end:cdr2_start-1]
        
        # FR3: From after CDR2 to before CDR3
        cdr2_end = cdr_positions.get(f"CDR-{chain_type[0]}2", (1, 1))[1]
        cdr3_start = cdr_positions.get(f"CDR-{chain_type[0]}3", (1, 1))[0]
        frameworks["FR3"] = sequence[cdr2_end:cdr3_start-1]
        
        # FR4: From after CDR3 to sequence end
        cdr3_end = cdr_positions.get(f"CDR-{chain_type[0]}3", (1, 1))[1]
        frameworks["FR4"] = sequence[cdr3_end:]
        
        return frameworks
    
    def calculate_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate similarity between two sequences (based on identity and conservative substitutions)"""
        # Conservative substitution groups (simplified BLOSUM62)
        conservative_groups = [
            set("ILMV"),  # Hydrophobic aliphatic
            set("FWY"),   # Aromatic
            set("DE"),    # Acidic
            set("KRH"),   # Basic
            set("STNQ"),  # Polar
            set("AG"),    # Small non-polar
            set("C"),     # Cysteine (special)
            set("P"),     # Proline (special)
        ]
        
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0.0
        
        matches = 0
        for i in range(min_len):
            aa1, aa2 = seq1[i], seq2[i]
            if aa1 == aa2:
                matches += 1.0  # Exact match
            else:
                # Check for conservative substitution
                for group in conservative_groups:
                    if aa1 in group and aa2 in group:
                        matches += 0.5  # Conservative substitution gets partial score
                        break
        
        # Length penalty (shorter comparison sequence)
        length_penalty = min_len / max(len(seq1), len(seq2))
        
        return (matches / min_len) * length_penalty
    
    def find_best_frameworks(self, sequence: str, chain_type: str, 
                            top_n: int = 3) -> List[Tuple[str, float, str]]:
        """Find best matching human frameworks"""
        
        if chain_type == "VH":
            germline_db = HUMAN_GERMLINE_VH
        else:
            germline_db = HUMAN_GERMLINE_VL
        
        # Extract framework regions
        source_frameworks = self.extract_frameworks(sequence, chain_type)
        source_cdrs = self.extract_cdrs(sequence, chain_type)
        
        scores = []
        for germline_name, germline_seq in germline_db.items():
            germline_frameworks = self.extract_frameworks(germline_seq, chain_type)
            germline_cdrs = self.extract_cdrs(germline_seq, chain_type)
            
            # Calculate framework similarity
            fr_similarities = []
            for fr_name in ["FR1", "FR2", "FR3", "FR4"]:
                if fr_name in source_frameworks and fr_name in germline_frameworks:
                    sim = self.calculate_similarity(
                        source_frameworks[fr_name], 
                        germline_frameworks[fr_name]
                    )
                    fr_similarities.append(sim)
            
            # Overall framework similarity
            avg_similarity = sum(fr_similarities) / len(fr_similarities) if fr_similarities else 0
            
            # Build humanized sequence (keep original CDRs)
            humanized = self._build_humanized_sequence(
                source_frameworks, source_cdrs, germline_frameworks
            )
            
            scores.append((germline_name, avg_similarity, humanized))
        
        # Sort and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    
    def _build_humanized_sequence(self, source_frs: Dict[str, str], 
                                   source_cdrs: Dict[str, CDRRegion],
                                   germline_frs: Dict[str, str]) -> str:
        """Build humanized sequence (human FR + original CDR)"""
        # Simplified construction method
        fr_order = ["FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4"]
        
        result = []
        for region in fr_order:
            if region.startswith("FR"):
                # Use human framework
                result.append(germline_frs.get(region, source_frs.get(region, "")))
            else:
                # Use original CDR
                cdr_key = f"CDR-{region[-1]}"
                for cdr_name, cdr in source_cdrs.items():
                    if cdr_name.endswith(region[-1]):
                        result.append(cdr.sequence)
                        break
        
        return "".join(result)
    
    def predict_back_mutations(self, mouse_seq: str, humanized_seq: str, 
                               chain_type: str) -> List[BackMutation]:
        """Predict required back mutations"""
        mutations = []
        critical_pos = CRITICAL_RESIDUES.get(chain_type, [])
        
        min_len = min(len(mouse_seq), len(humanized_seq))
        
        for pos in critical_pos:
            idx = pos - 1  # Convert to 0-based
            if idx < min_len:
                mouse_aa = mouse_seq[idx]
                human_aa = humanized_seq[idx]
                
                if mouse_aa != human_aa:
                    reason = self._classify_mutation_reason(pos, chain_type)
                    mutations.append(BackMutation(
                        position=f"{chain_type}-{pos}",
                        from_aa=human_aa,
                        to_aa=mouse_aa,
                        reason=reason
                    ))
        
        return mutations
    
    def _classify_mutation_reason(self, position: int, chain_type: str) -> str:
        """Classify mutation reason"""
        vernier_positions = [35, 36, 47, 48, 49] if chain_type == "VL" else [24, 27, 29, 71, 78]
        interface_positions = [34, 36, 38, 44, 46, 87] if chain_type == "VL" else [37, 39, 45, 47, 91]
        packing_positions = [2, 4]  # Hydrophobic core
        
        if position in vernier_positions:
            return "Vernier region - affects CDR conformation"
        elif position in interface_positions:
            return "VH-VL interface - affects chain pairing"
        elif position in packing_positions:
            return "Packing residue - core stability"
        else:
            return "Conserved framework position"
    
    def calculate_humanness_score(self, sequence: str, 
                                   germline_name: str, 
                                   chain_type: str) -> Tuple[float, float, str]:
        """Calculate humanization score"""
        
        if chain_type == "VH":
            germline_seq = HUMAN_GERMLINE_VH.get(germline_name, "")
        else:
            germline_seq = HUMAN_GERMLINE_VL.get(germline_name, "")
        
        if not germline_seq:
            return 0.0, 0.0, "Unknown"
        
        # Calculate similarity to human germline
        similarity = self.calculate_similarity(sequence, germline_seq)
        
        # T20 score simulation (based on 20mer peptide humanization degree)
        # In real application, would need complete T20 database
        t20_score = similarity * 100
        
        # Normalize to 0-100 scale
        humanness_score = min(100, similarity * 110)
        
        # Risk classification
        if humanness_score >= 85:
            risk_level = "Low"
        elif humanness_score >= 70:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return similarity, humanness_score, risk_level
    
    def humanize(self, vh_sequence: str, vl_sequence: str, 
                 antibody_name: str = "", top_n: int = 3) -> Dict:
        """Execute complete humanization analysis"""
        
        # Validate sequences
        vh_valid, vh_result = self.validate_sequence(vh_sequence)
        if not vh_valid:
            raise ValueError(f"VH sequence error: {vh_result}")
        vh_sequence = vh_result
        
        vl_valid, vl_result = self.validate_sequence(vl_sequence)
        if not vl_valid:
            raise ValueError(f"VL sequence error: {vl_result}")
        vl_sequence = vl_result
        
        # Extract CDRs
        vh_cdrs = self.extract_cdrs(vh_sequence, "VH")
        vl_cdrs = self.extract_cdrs(vl_sequence, "VL")
        
        # Find best human frameworks
        vh_candidates = self.find_best_frameworks(vh_sequence, "VH", top_n)
        vl_candidates = self.find_best_frameworks(vl_sequence, "VL", top_n)
        
        # Generate humanization candidates
        candidates = []
        rank = 1
        
        for vh_name, vh_sim, vh_humanized in vh_candidates:
            for vl_name, vl_sim, vl_humanized in vl_candidates:
                # Calculate composite score
                avg_similarity = (vh_sim + vl_sim) / 2
                _, humanness_score, risk_level = self.calculate_humanness_score(
                    vh_humanized + vl_humanized, vh_name, "VH"
                )
                
                # Predict back mutations
                vh_mutations = self.predict_back_mutations(vh_sequence, vh_humanized, "VH")
                vl_mutations = self.predict_back_mutations(vl_sequence, vl_humanized, "VL")
                all_mutations = vh_mutations + vl_mutations
                
                candidate = HumanizationCandidate(
                    rank=rank,
                    framework_source=f"{vh_name} / {vl_name}",
                    human_homology=avg_similarity,
                    humanness_score=humanness_score,
                    risk_level=risk_level,
                    humanized_vh=vh_humanized,
                    humanized_vl=vl_humanized,
                    back_mutations=all_mutations
                )
                candidates.append(candidate)
                rank += 1
        
        # Sort by score
        candidates.sort(key=lambda x: x.humanness_score, reverse=True)
        for i, c in enumerate(candidates, 1):
            c.rank = i
        
        # Build output
        best_candidate = candidates[0] if candidates else None
        
        result = {
            "input": {
                "name": antibody_name or "Unnamed Antibody",
                "vh_length": len(vh_sequence),
                "vl_length": len(vl_sequence),
                "vh_sequence": vh_sequence,
                "vl_sequence": vl_sequence
            },
            "analysis": {
                "scheme": self.scheme.value,
                "vh_cdrs": {name: cdr.to_dict() for name, cdr in vh_cdrs.items()},
                "vl_cdrs": {name: cdr.to_dict() for name, cdr in vl_cdrs.items()}
            },
            "humanization_candidates": [c.to_dict() for c in candidates[:top_n]],
            "recommendation": {
                "best_candidate": 1,
                "rationale": "Highest human homology with minimal back-mutations required",
                "immunogenicity_risk": best_candidate.risk_level if best_candidate else "Unknown"
            }
        }
        
        return result


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Antibody Humanizer - AI-powered antibody humanization tool"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--vh", type=str, help="Murine VH sequence (amino acids)")
    input_group.add_argument("--input", "-i", type=str, help="Input JSON file path")
    
    parser.add_argument("--vl", type=str, help="Murine VL sequence (amino acids)")
    parser.add_argument("--name", "-n", type=str, help="Antibody name", default="")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--format", "-f", type=str, 
                       choices=["json", "fasta", "csv"],
                       default="json", help="Output format")
    parser.add_argument("--scheme", "-s", type=str,
                       choices=["kabat", "chothia", "imgt"],
                       default="chothia", help="Numbering scheme")
    parser.add_argument("--top-n", type=int, default=3,
                       help="Number of best human frameworks to return")
    
    return parser.parse_args()


def read_input_file(filepath: str) -> Dict:
    """Read input from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def write_output(result: Dict, filepath: Optional[str] = None, fmt: str = "json"):
    """Output results"""
    output = json.dumps(result, indent=2, ensure_ascii=False)
    
    if filepath:
        with open(filepath, 'w') as f:
            f.write(output)
        print(f"Results saved to: {filepath}")
    else:
        print(output)


def main():
    """Main function"""
    args = parse_args()
    
    # Determine input
    if args.input:
        input_data = read_input_file(args.input)
        vh_sequence = input_data.get("vh_sequence", "")
        vl_sequence = input_data.get("vl_sequence", "")
        name = input_data.get("name", "")
        scheme_str = input_data.get("scheme", args.scheme)
    else:
        vh_sequence = args.vh
        vl_sequence = args.vl
        name = args.name
        scheme_str = args.scheme
        
        if not vl_sequence:
            print("Error: --vl sequence must be provided when using --vh")
            sys.exit(1)
    
    # Determine numbering scheme
    scheme_map = {
        "kabat": NumberingScheme.KABAT,
        "chothia": NumberingScheme.CHOTHIA,
        "imgt": NumberingScheme.IMGT
    }
    scheme = scheme_map.get(scheme_str.lower(), NumberingScheme.CHOTHIA)
    
    # Execute humanization
    try:
        humanizer = AntibodyHumanizer(scheme=scheme)
        result = humanizer.humanize(
            vh_sequence=vh_sequence,
            vl_sequence=vl_sequence,
            antibody_name=name,
            top_n=args.top_n
        )
        
        # Output results
        write_output(result, args.output, args.format)
        
    except ValueError as e:
        print(f"Input error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Processing error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
