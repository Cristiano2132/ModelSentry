import pandas as pd
from typing import List, Dict, Any, Optional
from .base import KRI, ValidationResult

class ValidationSuite:
    """Orquestrador da suite de validação de modelos."""
    
    def __init__(
        self, 
        df: pd.DataFrame, 
        date_col: str, 
        sample_col: str, 
        target_col: str, 
        score_col: str, 
        features: List[str],
        custom_weights: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa a suite de validação com os dados e a configuração.
        
        Args:
            df: DataFrame com os dados de Dev e OOT.
            date_col: Nome da coluna de data.
            sample_col: Nome da coluna que indica se a amostra é 'dev' ou 'oot'.
            target_col: Nome da variável resposta (ex: 0 e 1).
            score_col: Nome da coluna com o score/probabilidade do modelo.
            features: Lista de features utilizadas pelo modelo.
            custom_weights: Dicionário opcional contendo os pesos para agregação.
        """
        self.df = df
        self.config = {
            'date_col': date_col,
            'sample_col': sample_col,
            'target_col': target_col,
            'score_col': score_col,
            'features': features
        }
        self.tests: List[KRI] = []
        self.custom_weights = custom_weights
        
    def add_test(self, test: KRI) -> None:
        """Adiciona um teste (KRI) à suite."""
        self.tests.append(test)
        
    def run(self) -> List[ValidationResult]:
        """
        Executa todos os testes registrados na suite.
        
        Returns:
            Uma lista de ValidationResult contendo os resultados de cada KRI.
        """
        results = []
        for test in self.tests:
            result = test.evaluate(self.df, self.config)
            results.append(result)
        return results

    def calculate_global_risk(self, results: List[ValidationResult]) -> float:
        """
        Calcula o risco global hierárquico com base nos resultados e pesos.
        """
        if not results:
            return 0.0

        # Organizar resultados por dimension -> sub_dimension -> list(KRI results)
        hierarchy = {}
        for r in results:
            dim = r.dimension
            sub = r.sub_dimension
            if dim not in hierarchy:
                hierarchy[dim] = {}
            if sub not in hierarchy[dim]:
                hierarchy[dim][sub] = []
            hierarchy[dim][sub].append(r)
            
        weights_config = self.custom_weights or {}
        
        dim_scores = {}
        for dim, subs in hierarchy.items():
            dim_config = weights_config.get(dim, {})
            sub_weights_config = dim_config.get('sub_dimensions', {}) if isinstance(dim_config, dict) else {}
            
            sub_scores = {}
            for sub, kris in subs.items():
                sub_config = sub_weights_config.get(sub, {}) if isinstance(sub_weights_config, dict) else {}
                kri_weights_config = sub_config.get('kris', {}) if isinstance(sub_config, dict) else {}
                
                # Calculate KRI scores
                kri_total_score = 0.0
                total_kri_weight = 0.0
                
                # Determine missing weights for KRIs
                configured_kris = [k for k in kris if k.name in kri_weights_config]
                unconfigured_kris = [k for k in kris if k.name not in kri_weights_config]
                
                sum_configured_weights = sum(kri_weights_config[k.name] for k in configured_kris)
                remaining_weight = max(0.0, 1.0 - sum_configured_weights)
                
                default_kri_weight = remaining_weight / len(unconfigured_kris) if unconfigured_kris else 0.0
                
                for k in kris:
                    w = kri_weights_config.get(k.name, default_kri_weight)
                    kri_total_score += k.risk_score * w
                    total_kri_weight += w
                    
                if total_kri_weight > 0:
                    sub_scores[sub] = kri_total_score / total_kri_weight
                else:
                    sub_scores[sub] = 0.0
            
            # Calculate Dimension score
            dim_total_score = 0.0
            total_sub_weight = 0.0
            
            configured_subs = [s for s in sub_scores.keys() if s in sub_weights_config and isinstance(sub_weights_config[s], dict) and 'weight' in sub_weights_config[s]]
            unconfigured_subs = [s for s in sub_scores.keys() if s not in configured_subs]
            
            sum_configured_sub_weights = sum(sub_weights_config[s]['weight'] for s in configured_subs)
            remaining_sub_weight = max(0.0, 1.0 - sum_configured_sub_weights)
            
            default_sub_weight = remaining_sub_weight / len(unconfigured_subs) if unconfigured_subs else 0.0
            
            for sub, score in sub_scores.items():
                w = sub_weights_config.get(sub, {}).get('weight', default_sub_weight) if isinstance(sub_weights_config.get(sub), dict) else default_sub_weight
                dim_total_score += score * w
                total_sub_weight += w
                
            if total_sub_weight > 0:
                dim_scores[dim] = dim_total_score / total_sub_weight
            else:
                dim_scores[dim] = 0.0
                
        # Calculate Global score
        final_score = 0.0
        total_dim_weight = 0.0
        
        configured_dims = [d for d in dim_scores.keys() if d in weights_config and isinstance(weights_config[d], dict) and 'weight' in weights_config[d]]
        unconfigured_dims = [d for d in dim_scores.keys() if d not in configured_dims]
        
        sum_configured_dim_weights = sum(weights_config[d]['weight'] for d in configured_dims)
        remaining_dim_weight = max(0.0, 1.0 - sum_configured_dim_weights)
        
        default_dim_weight = remaining_dim_weight / len(unconfigured_dims) if unconfigured_dims else 0.0
        
        for dim, score in dim_scores.items():
            w = weights_config.get(dim, {}).get('weight', default_dim_weight) if isinstance(weights_config.get(dim), dict) else default_dim_weight
            final_score += score * w
            total_dim_weight += w
            
        if total_dim_weight > 0:
            return round(final_score / total_dim_weight, 2)
        return 0.0
