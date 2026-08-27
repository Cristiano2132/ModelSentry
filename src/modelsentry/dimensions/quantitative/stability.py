from typing import Any, Dict
import pandas as pd
import numpy as np
from modelsentry.core.base import KRI, ValidationResult

class PSI_KRI(KRI):
    """
    KRI Quantitativo (Stability): Calcula o Population Stability Index (PSI) do score.
    """
    def __init__(self, ref_sample: str = 'dev', eval_samples: list = None):
        if eval_samples is None:
            eval_samples = ['oot']
        super().__init__(
            name="Population Stability Index (PSI) KRI",
            description=f"Avalia a estabilidade populacional (PSI). Referência: {ref_sample}. Avaliados: {', '.join(eval_samples)}.",
            dimension="Quantitativa",
            sub_dimension="Stability"
        )
        self.ref_sample = ref_sample
        self.eval_samples = eval_samples

    def _calculate_psi(self, expected: pd.Series, actual: pd.Series, q: int = 10) -> float:
        """Calcula o PSI entre duas séries numéricas (ex: score) usando decis reais."""
        # Se os dados estiverem vazios
        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        try:
            # Define os decis com base na distribuição de referência
            _, bin_edges = pd.qcut(expected.dropna(), q=q, retbins=True, duplicates='drop')
            
            # Ajusta os limites para englobar os dados de atual que possam fugir dos extremos
            bin_edges[0] = -np.inf
            bin_edges[-1] = np.inf
            
            # Calcula as distribuições
            expected_counts = pd.cut(expected.dropna(), bins=bin_edges).value_counts(sort=False).values
            actual_counts = pd.cut(actual.dropna(), bins=bin_edges).value_counts(sort=False).values
        except Exception:
            return 0.0

        # Converte para proporções
        expected_pct = expected_counts / len(expected)
        actual_pct = actual_counts / len(actual)

        # Trata zeros para evitar log(0) e divisão por zero
        expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
        actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)

        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        # Converter para percentual (0-100)
        return float(psi) * 100.0

    def _get_risk_score(self, psi_value: float) -> float:
        """
        Lógica (Percentual):
        PSI < 5% => Risco 0 (Nota 100)
        PSI < 10% => Risco 15 (Nota 85)
        PSI < 15% => Risco 30 (Nota 70)
        PSI < 20% => Risco 40 (Nota 60)
        PSI >= 20% => Risco 100 (Nota 0)
        """
        if psi_value < 5.0: return 0.0
        elif psi_value < 10.0: return 15.0
        elif psi_value < 15.0: return 30.0
        elif psi_value < 20.0: return 40.0
        else: return 100.0

    def evaluate(self, df: pd.DataFrame, config: Dict[str, Any]) -> ValidationResult:
        date_col = config.get('date_col')
        sample_col = config.get('sample_col')
        score_col = config.get('score_col')

        df_ref = df[df[sample_col] == self.ref_sample]
        overall_ref_score = df_ref[score_col]

        results_list = []
        
        # Garante que a amostra de referência também seja avaliada safra a safra
        samples_to_eval = set(self.eval_samples + [self.ref_sample])
        
        for sample_name in samples_to_eval:
            df_sample = df[df[sample_col] == sample_name]
            for date_val, group in df_sample.groupby(date_col):
                psi_val = self._calculate_psi(overall_ref_score, group[score_col])
                risk = self._get_risk_score(psi_val)
                results_list.append({
                    'amostra': sample_name,
                    'safra': date_val,
                    'psi_score': psi_val,
                    'risco_kri': risk
                })

        df_psi_results = pd.DataFrame(results_list)

        # Calcula a nota para dev e para oot (baseada no max PSI observado)
        df_dev = df_psi_results[df_psi_results['amostra'] == self.ref_sample]
        max_psi_dev = df_dev['psi_score'].max() if not df_dev.empty else 0.0
        risk_dev = self._get_risk_score(max_psi_dev)

        df_oot = df_psi_results[df_psi_results['amostra'] != self.ref_sample]
        max_psi_oot = df_oot['psi_score'].max() if not df_oot.empty else 0.0
        risk_oot = self._get_risk_score(max_psi_oot)

        # KRI final é a média entre o risco do max_dev e o risco do max_oot
        # Se não houver amostra oot (só dev), o risco é apenas de dev
        if df_oot.empty:
            final_risk_score = risk_dev
        else:
            final_risk_score = (risk_dev + risk_oot) / 2.0

        avg_psi = df_psi_results['psi_score'].mean() if not df_psi_results.empty else 0.0

        details = {
            "ref_sample": self.ref_sample, 
            "eval_samples": self.eval_samples,
            "max_psi_dev": float(max_psi_dev),
            "max_psi_oot": float(max_psi_oot),
            "risk_dev": risk_dev,
            "risk_oot": risk_oot
        }

        return ValidationResult(
            name=self.name,
            value=avg_psi,
            risk_score=round(final_risk_score, 2),
            dimension=self.dimension,
            sub_dimension=self.sub_dimension,
            details=details,
            tables={"psi_mensal": df_psi_results}
        )

