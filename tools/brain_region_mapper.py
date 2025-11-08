"""
Brain Region Mapper
Maps MRI volumetric data to 6 key brain regions using rule-based estimates
"""
from typing import Dict, Optional
import pandas as pd


class BrainRegionMapper:
    """
    Maps MRI CSV data to 6 brain regions required by frontend.
    Uses direct measurements where available, estimates for missing regions.
    """

    # Estimation coefficients based on neuroanatomy literature
    PREFRONTAL_CORTEX_RATIO = 0.25  # ~25% of gray matter
    PARIETAL_LOBE_RATIO = 0.20      # ~20% of gray matter
    AMYGDALA_HIPPOCAMPUS_RATIO = 0.03  # Amygdala ~3% of hippocampal volume
    CEREBELLUM_BRAIN_RATIO = 0.10   # ~10% of total brain volume

    # Normal ranges for flagging atrophy (normalized volumes)
    NORMAL_RANGES = {
        'hippocampus': (0.0020, 0.0025),
        'prefrontalCortex': (0.024, 0.030),
        'temporalLobe': (0.028, 0.035),
        'parietalLobe': (0.019, 0.024),
        'amygdala': (0.00006, 0.00008),
        'cerebellum': (0.095, 0.115)
    }

    def parse_mri_csv(self, csv_path: str) -> Dict[str, float]:
        """Parse MRI CSV file and extract volumetric data"""
        df = pd.read_csv(csv_path)

        # Convert to dictionary for easy lookup
        mri_data = {}
        for _, row in df.iterrows():
            structure = row['Structure']
            mri_data[structure] = {
                'volume': float(row['Volume_mm3']),
                'normalized': float(row['Normalized_Volume'])
            }

        return mri_data

    def map_to_brain_regions(self, mri_data: Dict[str, Dict]) -> Dict[str, float]:
        """
        Map MRI data to 6 brain regions with normalized scores (0-1)

        Returns scores representing relative health (1.0 = healthy, 0.0 = severe atrophy)
        """

        # 1. HIPPOCAMPUS - Direct measurement (average left/right)
        left_hipp = mri_data.get('Left-Hippocampus', {}).get('normalized', 0)
        right_hipp = mri_data.get('Right-Hippocampus', {}).get('normalized', 0)
        hippocampus_norm = (left_hipp + right_hipp) / 2
        hippocampus_score = self._normalize_to_health_score(
            hippocampus_norm,
            self.NORMAL_RANGES['hippocampus']
        )

        # 2. TEMPORAL LOBE - Direct measurement (average left/right)
        left_temporal = mri_data.get('Left-Temporal-Lobe', {}).get('normalized', 0)
        right_temporal = mri_data.get('Right-Temporal-Lobe', {}).get('normalized', 0)
        temporal_norm = (left_temporal + right_temporal) / 2
        temporal_score = self._normalize_to_health_score(
            temporal_norm,
            self.NORMAL_RANGES['temporalLobe']
        )

        # 3. PREFRONTAL CORTEX - Estimated from gray matter
        gray_matter = mri_data.get('Total-gray-matter', {}).get('normalized', 0)
        prefrontal_norm = gray_matter * self.PREFRONTAL_CORTEX_RATIO
        prefrontal_score = self._normalize_to_health_score(
            prefrontal_norm,
            self.NORMAL_RANGES['prefrontalCortex']
        )

        # 4. PARIETAL LOBE - Estimated from gray matter
        parietal_norm = gray_matter * self.PARIETAL_LOBE_RATIO
        parietal_score = self._normalize_to_health_score(
            parietal_norm,
            self.NORMAL_RANGES['parietalLobe']
        )

        # 5. AMYGDALA - Estimated from hippocampal volume
        amygdala_norm = hippocampus_norm * self.AMYGDALA_HIPPOCAMPUS_RATIO
        amygdala_score = self._normalize_to_health_score(
            amygdala_norm,
            self.NORMAL_RANGES['amygdala']
        )

        # 6. CEREBELLUM - Estimated from total brain volume
        brain_volume = mri_data.get('Brain-Segmentation-Volume', {}).get('normalized', 0)
        cerebellum_norm = brain_volume * self.CEREBELLUM_BRAIN_RATIO
        cerebellum_score = self._normalize_to_health_score(
            cerebellum_norm,
            self.NORMAL_RANGES['cerebellum']
        )

        return {
            'hippocampus': round(hippocampus_score, 3),
            'prefrontalCortex': round(prefrontal_score, 3),
            'temporalLobe': round(temporal_score, 3),
            'parietalLobe': round(parietal_score, 3),
            'amygdala': round(amygdala_score, 3),
            'cerebellum': round(cerebellum_score, 3)
        }

    def _normalize_to_health_score(
        self,
        normalized_volume: float,
        normal_range: tuple
    ) -> float:
        """
        Convert normalized volume to health score (0-1)

        - 1.0 = within or above normal range (healthy)
        - 0.5-1.0 = below normal but not severe
        - 0.0-0.5 = significant atrophy
        """
        min_normal, max_normal = normal_range

        if normalized_volume >= min_normal:
            # Within or above normal range
            # Cap at 1.0, proportional above min_normal
            return min(1.0, normalized_volume / max_normal)
        else:
            # Below normal - scale from 0 to 0.8
            # Severe atrophy (50% of min) = 0.0
            # Just below normal = 0.8
            ratio = normalized_volume / min_normal
            return max(0.0, ratio * 0.8)

    def detect_atrophy_alerts(
        self,
        brain_regions: Dict[str, float],
        threshold: float = 0.7
    ) -> list:
        """
        Detect regions with concerning atrophy

        Args:
            brain_regions: Dict of region scores
            threshold: Score below which to flag (default 0.7)

        Returns:
            List of alert dictionaries
        """
        alerts = []

        severity_map = {
            (0.0, 0.4): 'critical',
            (0.4, 0.6): 'high',
            (0.6, threshold): 'moderate'
        }

        for region, score in brain_regions.items():
            if score < threshold:
                severity = 'moderate'
                for (low, high), sev in severity_map.items():
                    if low <= score < high:
                        severity = sev
                        break

                alerts.append({
                    'region': region,
                    'score': score,
                    'severity': severity,
                    'message': f'{region.replace("_", " ").title()}: Score {score:.2f} - {"Significant" if severity == "critical" else "Moderate"} atrophy detected'
                })

        return alerts

    def compare_mri_scans(
        self,
        baseline_regions: Dict[str, float],
        current_regions: Dict[str, float]
    ) -> Dict:
        """
        Compare two MRI scans to detect progression

        Returns change analysis and recommendations
        """
        changes = {}
        declining_regions = []

        for region in baseline_regions.keys():
            baseline = baseline_regions[region]
            current = current_regions[region]
            change = current - baseline
            percent_change = (change / baseline * 100) if baseline > 0 else 0

            changes[region] = {
                'baseline': baseline,
                'current': current,
                'absolute_change': round(change, 3),
                'percent_change': round(percent_change, 1)
            }

            # Flag significant decline (>10% loss)
            if percent_change < -10:
                declining_regions.append({
                    'region': region,
                    'percent_decline': abs(percent_change)
                })

        # Generate recommendation
        recommendation = "Continue routine monitoring"
        if len(declining_regions) >= 3:
            recommendation = "URGENT: Multiple regions showing decline. Recommend neurologist consultation and follow-up MRI in 3 months."
        elif len(declining_regions) >= 1:
            recommendation = "Schedule follow-up MRI in 6 months to monitor progression."

        return {
            'changes': changes,
            'declining_regions': declining_regions,
            'recommendation': recommendation,
            'requires_doctor_review': len(declining_regions) >= 1
        }


# Convenience function
def analyze_mri_file(csv_path: str) -> Dict:
    """
    Quick analysis of MRI CSV file

    Returns:
        - brain_regions: Scores for 6 regions
        - alerts: Any atrophy alerts
        - raw_data: Original MRI measurements
    """
    mapper = BrainRegionMapper()
    mri_data = mapper.parse_mri_csv(csv_path)
    brain_regions = mapper.map_to_brain_regions(mri_data)
    alerts = mapper.detect_atrophy_alerts(brain_regions)

    return {
        'brain_regions': brain_regions,
        'alerts': alerts,
        'raw_data': mri_data
    }
