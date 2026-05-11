#!/usr/bin/env python3
"""
Chemical Structure Converter
Convert between IUPAC names, SMILES, and 2D/3D structures.
"""

import argparse


class ChemicalStructureConverter:
    """Convert chemical identifiers."""
    
    # Mock database for common compounds
    COMPOUND_DB = {
        "aspirin": {
            "iupac": "2-acetoxybenzoic acid",
            "smiles": "CC(=O)Oc1ccccc1C(=O)O",
            "formula": "C9H8O4",
            "mw": 180.16
        },
        "caffeine": {
            "iupac": "1,3,7-trimethylxanthine",
            "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "formula": "C8H10N4O2",
            "mw": 194.19
        },
        "glucose": {
            "iupac": "D-glucose",
            "smiles": "C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O",
            "formula": "C6H12O6",
            "mw": 180.16
        },
        "ethanol": {
            "iupac": "ethanol",
            "smiles": "CCO",
            "formula": "C2H6O",
            "mw": 46.07
        }
    }
    
    def smiles_to_iupac(self, smiles):
        """Convert SMILES to IUPAC name (mock)."""
        for name, data in self.COMPOUND_DB.items():
            if data["smiles"] == smiles:
                return data["iupac"]
        return "Unknown structure"
    
    def iupac_to_smiles(self, iupac):
        """Convert IUPAC name to SMILES (mock)."""
        for name, data in self.COMPOUND_DB.items():
            if data["iupac"].lower() == iupac.lower():
                return data["smiles"]
        return "Unknown IUPAC name"
    
    def name_to_identifiers(self, name):
        """Get all identifiers for a compound name."""
        name_lower = name.lower()
        if name_lower in self.COMPOUND_DB:
            return self.COMPOUND_DB[name_lower]
        
        # Try IUPAC match
        for key, data in self.COMPOUND_DB.items():
            if data["iupac"].lower() == name_lower:
                return data
        
        return None
    
    def validate_smiles(self, smiles):
        """Basic SMILES validation."""
        # Simple checks
        open_parens = smiles.count("(")
        close_parens = smiles.count(")")
        if open_parens != close_parens:
            return False, "Mismatched parentheses"
        
        open_brackets = smiles.count("[")
        close_brackets = smiles.count("]")
        if open_brackets != close_brackets:
            return False, "Mismatched brackets"
        
        return True, "Valid SMILES syntax"
    
    def print_conversion(self, name, data):
        """Print conversion results."""
        print(f"\n{'='*60}")
        print(f"COMPOUND: {name.upper()}")
        print(f"{'='*60}")
        print(f"IUPAC Name: {data['iupac']}")
        print(f"SMILES:     {data['smiles']}")
        print(f"Formula:    {data['formula']}")
        print(f"Molecular Weight: {data['mw']} g/mol")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Chemical Structure Converter")
    parser.add_argument("--name", "-n", help="Compound name")
    parser.add_argument("--smiles", "-s", help="SMILES string")
    parser.add_argument("--iupac", "-i", help="IUPAC name")
    parser.add_argument("--validate", action="store_true",
                       help="Validate SMILES syntax")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List available compounds")
    
    args = parser.parse_args()
    
    converter = ChemicalStructureConverter()
    
    if args.list:
        print("\nAvailable compounds:")
        for name in converter.COMPOUND_DB.keys():
            print(f"  - {name}")
        return
    
    if args.name:
        data = converter.name_to_identifiers(args.name)
        if data:
            converter.print_conversion(args.name, data)
        else:
            print(f"Compound '{args.name}' not found in database")
    
    elif args.smiles:
        valid, msg = converter.validate_smiles(args.smiles)
        print(f"SMILES validation: {msg}")
        
        if valid:
            iupac = converter.smiles_to_iupac(args.smiles)
            print(f"IUPAC name: {iupac}")
    
    elif args.iupac:
        smiles = converter.iupac_to_smiles(args.iupac)
        print(f"SMILES: {smiles}")
    
    else:
        # Demo
        data = converter.name_to_identifiers("aspirin")
        converter.print_conversion("aspirin", data)


if __name__ == "__main__":
    main()
