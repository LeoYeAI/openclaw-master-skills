#!/usr/bin/env python3
"""
ADME Property Predictor - Predict drug candidate ADME properties.

Predicts Absorption, Distribution, Metabolism, and Excretion properties
using molecular descriptors and cheminformatics models.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


@dataclass
class ADMEResult:
    """Container for ADME prediction results."""
    # Molecule info
    smiles: str
    molecular_weight: float
    formula: str
    
    # Absorption
    lipinski_violations: int
    lipinski_pass: bool
    caco2_permeability: str
    hia: float  # Human Intestinal Absorption %
    solubility_class: str
    psa: float  # Polar Surface Area
    logp: float
    hbd: int  # H-bond donors
    hba: int  # H-bond acceptors
    rotatable_bonds: int
    
    # Distribution
    bbb_permeable: bool
    ppb_percent: float  # Plasma protein binding
    vd_estimate: float  # Volume of distribution
    
    # Metabolism
    cyp3a4_substrate: bool
    cyp2c9_substrate: bool
    cyp2d6_substrate: bool
    metabolic_stability: str
    
    # Excretion
    t12_hours: float  # Half-life
    clearance_ml_min_kg: float
    excretion_route: str
    
    # Overall
    druglikeness_score: float
    recommendation: str


class ADMEPredictor:
    """Predict ADME properties from molecular structure."""
    
    def __init__(self):
        if not RDKIT_AVAILABLE:
            raise ImportError(
                "RDKit is required for ADME prediction. "
                "Install with: pip install rdkit"
            )
    
    def predict(self, smiles: str, properties: Optional[List[str]] = None) -> ADMEResult:
        """Predict ADME properties for a molecule."""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        
        # Calculate basic descriptors
        mw = Descriptors.MolWt(mol)
        formula = rdMolDescriptors.CalcMolFormula(mol)
        logp = Crippen.MolLogP(mol)
        psa = Descriptors.TPSA(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        rot_bonds = Lipinski.NumRotatableBonds(mol)
        
        # Absorption properties
        lipinski_violations = self._lipinski_violations(mol)
        lipinski_pass = lipinski_violations <= 1
        caco2_perm = self._predict_caco2(logp, psa, mw)
        hia = self._predict_hia(logp, psa, mw)
        sol_class = self._classify_solubility(logp, mw)
        
        # Distribution properties
        bbb = self._predict_bbb(logp, psa, mw, hbd)
        ppb = self._predict_ppb(logp, psa)
        vd = self._estimate_vd(logp, ppb)
        
        # Metabolism properties
        cyp3a4 = self._predict_cyp3a4_substrate(logp, rot_bonds)
        cyp2c9 = self._predict_cyp2c9_substrate(mol)
        cyp2d6 = self._predict_cyp2d6_substrate(mol, psa)
        metab_stab = self._assess_metabolic_stability(mol, rot_bonds)
        
        # Excretion properties
        t12 = self._estimate_half_life(logp, vd, mw)
        clearance = self._estimate_clearance(logp, psa, mw)
        excretion = self._predict_excretion_route(mw, logp)
        
        # Overall drug-likeness
        score = self._calculate_druglikeness(
            lipinski_pass, logp, psa, hia, bbb, t12
        )
        recommendation = self._get_recommendation(score, lipinski_violations)
        
        return ADMEResult(
            smiles=smiles,
            molecular_weight=round(mw, 2),
            formula=formula,
            lipinski_violations=lipinski_violations,
            lipinski_pass=lipinski_pass,
            caco2_permeability=caco2_perm,
            hia=round(hia, 1),
            solubility_class=sol_class,
            psa=round(psa, 1),
            logp=round(logp, 2),
            hbd=hbd,
            hba=hba,
            rotatable_bonds=rot_bonds,
            bbb_permeable=bbb,
            ppb_percent=round(ppb, 1),
            vd_estimate=round(vd, 2),
            cyp3a4_substrate=cyp3a4,
            cyp2c9_substrate=cyp2c9,
            cyp2d6_substrate=cyp2d6,
            metabolic_stability=metab_stab,
            t12_hours=round(t12, 1),
            clearance_ml_min_kg=round(clearance, 1),
            excretion_route=excretion,
            druglikeness_score=round(score, 2),
            recommendation=recommendation
        )
    
    def _lipinski_violations(self, mol) -> int:
        """Count Lipinski Rule of 5 violations."""
        violations = 0
        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        
        if mw > 500:
            violations += 1
        if logp > 5:
            violations += 1
        if hbd > 5:
            violations += 1
        if hba > 10:
            violations += 1
        
        return violations
    
    def _predict_caco2(self, logp: float, psa: float, mw: float) -> str:
        """Predict Caco-2 permeability."""
        # Simplified model: high lipophilicity, moderate PSA favors permeability
        score = logp - (psa / 100) - (max(0, mw - 400) / 200)
        if score > 2:
            return "high"
        elif score > 0.5:
            return "moderate"
        else:
            return "low"
    
    def _predict_hia(self, logp: float, psa: float, mw: float) -> float:
        """Predict Human Intestinal Absorption percentage."""
        # Based on Zhao et al. model
        if psa > 140:
            return 30.0
        elif psa > 90:
            base = 70.0
        else:
            base = 95.0
        
        # Adjust for lipophilicity
        if logp < -1:
            base -= 20
        elif logp > 5:
            base -= 15
        
        # Adjust for size
        if mw > 500:
            base -= 10
        
        return max(10, min(100, base))
    
    def _classify_solubility(self, logp: float, mw: float) -> str:
        """Classify aqueous solubility."""
        # Simplified classification
        if logp < 0:
            return "highly soluble"
        elif logp < 2:
            return "soluble"
        elif logp < 4:
            return "slightly soluble"
        else:
            return "poorly soluble"
    
    def _predict_bbb(self, logp: float, psa: float, mw: float, hbd: int) -> bool:
        """Predict Blood-Brain Barrier permeability."""
        # Based on Clark's rules
        if psa > 90 or mw > 450 or hbd > 3:
            return False
        if logp < -0.5 or logp > 6:
            return False
        return True
    
    def _predict_ppb(self, logp: float, psa: float) -> float:
        """Predict plasma protein binding percentage."""
        # Simplified: lipophilic compounds bind more
        base = 30 + (logp * 15)
        if psa > 120:
            base -= 20
        return max(5, min(99, base))
    
    def _estimate_vd(self, logp: float, ppb: float) -> float:
        """Estimate volume of distribution (L/kg)."""
        # Simplified model
        fu = (100 - ppb) / 100  # Fraction unbound
        vd = 0.1 + (fu * 0.5) + (max(0, logp - 2) * 0.3)
        return min(vd, 10)
    
    def _predict_cyp3a4_substrate(self, logp: float, rot_bonds: int) -> bool:
        """Predict CYP3A4 substrate likelihood."""
        # CYP3A4 prefers lipophilic, flexible molecules
        return logp > 1 and rot_bonds >= 3
    
    def _predict_cyp2c9_substrate(self, mol) -> bool:
        """Predict CYP2C9 substrate likelihood."""
        # Simplified: check for acidic groups (common CYP2C9 substrates)
        pattern = Chem.MolFromSmarts('[C](=O)[O;H1]')  # Carboxylic acid
        return mol.HasSubstructMatch(pattern)
    
    def _predict_cyp2d6_substrate(self, mol, psa: float) -> bool:
        """Predict CYP2D6 substrate likelihood."""
        # CYP2D6 substrates often contain basic nitrogen
        basic_n = Chem.MolFromSmarts('[N;H1,H2,H3;+0,+1]')
        has_basic_n = mol.HasSubstructMatch(basic_n)
        return has_basic_n and psa > 20
    
    def _assess_metabolic_stability(self, mol, rot_bonds: int) -> str:
        """Assess metabolic stability."""
        # Count metabolic hotspots
        hotspots = 0
        
        # Unsubstituted aromatic positions
        aromatic_c = Chem.MolFromSmarts('[cH]')
        hotspots += len(mol.GetSubstructMatches(aromatic_c))
        
        # Benzylic positions
        benzylic = Chem.MolFromSmarts('[c]C[#1]')
        hotspots += len(mol.GetSubstructMatches(benzylic))
        
        # High rotatable bonds indicate flexibility
        if rot_bonds > 10:
            hotspots += 2
        
        if hotspots <= 2:
            return "high"
        elif hotspots <= 5:
            return "moderate"
        else:
            return "low"
    
    def _estimate_half_life(self, logp: float, vd: float, mw: float) -> float:
        """Estimate elimination half-life (hours)."""
        # Simplified: based on Vd and molecular properties
        base = 2 + (vd * 2)
        if logp > 4:
            base += 2
        if mw > 400:
            base += 1
        return min(base, 24)
    
    def _estimate_clearance(self, logp: float, psa: float, mw: float) -> float:
        """Estimate clearance (mL/min/kg)."""
        # Simplified model
        base = 10
        if psa > 100:
            base += 5  # More polar = more renal clearance
        if logp > 4:
            base -= 3  # Lipophilic = slower clearance
        if mw > 500:
            base -= 2
        return max(1, base)
    
    def _predict_excretion_route(self, mw: float, logp: float) -> str:
        """Predict primary excretion route."""
        if mw < 300 and logp < 2:
            return "renal (primarily)"
        elif logp > 4:
            return "biliary/hepatic"
        else:
            return "mixed renal/hepatic"
    
    def _calculate_druglikeness(
        self, lipinski_pass: bool, logp: float, psa: float,
        hia: float, bbb: bool, t12: float
    ) -> float:
        """Calculate overall drug-likeness score (0-1)."""
        score = 0.0
        
        # Lipinski compliance
        score += 0.2 if lipinski_pass else 0.0
        
        # LogP in sweet spot (1-3)
        if 1 <= logp <= 3:
            score += 0.2
        elif 0 <= logp <= 5:
            score += 0.1
        
        # PSA acceptable
        if psa <= 90:
            score += 0.2
        elif psa <= 140:
            score += 0.1
        
        # Good absorption
        if hia >= 80:
            score += 0.2
        elif hia >= 50:
            score += 0.1
        
        # Reasonable half-life
        if 2 <= t12 <= 8:
            score += 0.2
        elif 1 <= t12 <= 12:
            score += 0.1
        
        return score
    
    def _get_recommendation(self, score: float, lipinski_violations: int) -> str:
        """Generate recommendation based on score."""
        if score >= 0.8 and lipinski_violations <= 1:
            return "Excellent drug candidate"
        elif score >= 0.6 and lipinski_violations <= 2:
            return "Good drug candidate with minor concerns"
        elif score >= 0.4:
            return "Moderate candidate - optimization needed"
        else:
            return "Poor drug candidate - significant issues"


def format_output(result: ADMEResult, format_type: str = "json") -> str:
    """Format output as JSON or table."""
    if format_type == "json":
        data = asdict(result)
        return json.dumps(data, indent=2)
    
    # Table format
    lines = [
        "=" * 60,
        "ADME PROPERTY PREDICTION REPORT",
        "=" * 60,
        f"\nMolecule: {result.formula}",
        f"SMILES: {result.smiles}",
        f"Molecular Weight: {result.molecular_weight} Da",
        "",
        "-" * 40,
        "ABSORPTION (A)",
        "-" * 40,
        f"  Lipinski Violations: {result.lipinski_violations}/4",
        f"  Lipinski Pass: {result.lipinski_pass}",
        f"  Caco-2 Permeability: {result.caco2_permeability}",
        f"  HIA: {result.hia}%",
        f"  Solubility: {result.solubility_class}",
        f"  PSA: {result.psa} Å²",
        f"  LogP: {result.logp}",
        f"  HBD/HBA: {result.hbd}/{result.hba}",
        "",
        "-" * 40,
        "DISTRIBUTION (D)",
        "-" * 40,
        f"  BBB Permeable: {result.bbb_permeable}",
        f"  Plasma Protein Binding: {result.ppb_percent}%",
        f"  Vd Estimate: {result.vd_estimate} L/kg",
        "",
        "-" * 40,
        "METABOLISM (M)",
        "-" * 40,
        f"  CYP3A4 Substrate: {result.cyp3a4_substrate}",
        f"  CYP2C9 Substrate: {result.cyp2c9_substrate}",
        f"  CYP2D6 Substrate: {result.cyp2d6_substrate}",
        f"  Metabolic Stability: {result.metabolic_stability}",
        "",
        "-" * 40,
        "EXCRETION (E)",
        "-" * 40,
        f"  Half-life: {result.t12_hours} h",
        f"  Clearance: {result.clearance_ml_min_kg} mL/min/kg",
        f"  Excretion Route: {result.excretion_route}",
        "",
        "=" * 60,
        f"Drug-likeness Score: {result.druglikeness_score}/1.0",
        f"Recommendation: {result.recommendation}",
        "=" * 60,
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Predict ADME properties for drug candidates"
    )
    parser.add_argument(
        "--smiles", "-s",
        help="SMILES string of the molecule"
    )
    parser.add_argument(
        "--properties", "-p",
        nargs="+",
        choices=["absorption", "distribution", "metabolism", "excretion", "all"],
        default=["all"],
        help="Specific properties to calculate"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "table"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input CSV file with SMILES column"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    # Initialize predictor
    try:
        predictor = ADMEPredictor()
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get SMILES to process
    smiles_list = []
    if args.smiles:
        smiles_list.append(args.smiles)
    elif args.input:
        import csv
        with open(args.input, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                smiles_list.append(row.get('smiles', row.get('SMILES', '')))
    else:
        # Demo mode with aspirin
        print("No input provided. Running demo with Aspirin...")
        smiles_list = ["CC(=O)Oc1ccccc1C(=O)O"]
    
    # Process molecules
    results = []
    for smiles in smiles_list:
        if not smiles:
            continue
        try:
            result = predictor.predict(smiles, args.properties)
            results.append(result)
            print(format_output(result, args.format))
            print()
        except Exception as e:
            print(f"Error processing {smiles}: {e}", file=sys.stderr)
    
    # Save to file if requested
    if args.output and results:
        output_data = [asdict(r) for r in results]
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
