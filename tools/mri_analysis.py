"""MRI volumetric analysis"""
import pandas as pd
import os
from typing import Dict

class MRIAnalyzer:
    
    KEY_STRUCTURES = {
        'hippocampus': ['Hippocampus'],
        'ventricles': ['Lateral-Ventricle'],
        'temporal_lobe': ['Temporal-Lobe'],
        'brain_volume': ['Brain-Segmentation'],
        'gray_matter': ['gray-matter'],
    }
    
    @staticmethod
    def parse_csv(csv_path: str) -> Dict:
        """Extract volumetric data"""
        if not os.path.exists(csv_path):
            return {'error': 'CSV not found', 'structures': {}}
        
        try:
            df = pd.read_csv(csv_path)
            metrics = {}
            icv = 1500000  # Default
            
            for metric_name, structures in MRIAnalyzer.KEY_STRUCTURES.items():
                total_vol = 0
                for struct in structures:
                    matching = df[df['Structure'].str.contains(struct, case=False, na=False)]
                    if not matching.empty:
                        total_vol += matching['Volume_mm3'].sum()
                
                metrics[metric_name] = {
                    'volume_mm3': float(total_vol),
                    'normalized': float(total_vol / icv)
                }
            
            return {'structures': metrics}
        except Exception as e:
            return {'error': str(e), 'structures': {}}
    
    @staticmethod
    def clinical_summary(metrics: Dict) -> str:
        """Generate summary"""
        structures = metrics.get('structures', {})
        findings = []
        
        hippocampus = structures.get('hippocampus', {}).get('normalized', 0)
        if hippocampus < 0.003:
            findings.append("significant hippocampal atrophy")
        elif hippocampus < 0.004:
            findings.append("mild hippocampal volume reduction")
        
        if not findings:
            return "Volumetric measures within expected range."
        
        return f"MRI findings: {', '.join(findings)}."
