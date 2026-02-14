"""
A/B Testing Framework - Compare NVIDIA vs DeepSeek quality.

Allows running both models in parallel and comparing results.
"""

import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class ABTestingFramework:
    """Framework for A/B testing different AI models."""
    
    def __init__(self):
        """Initialize A/B testing framework."""
        self.test_results = []
    
    def run_ab_test(
        self,
        nvidia_client,
        deepseek_llm,
        semantic_blocks: List[Dict[str, Any]],
        rules: str
    ) -> Dict[str, Any]:
        """
        Run both NVIDIA and DeepSeek in parallel and compare results.
        
        Args:
            nvidia_client: NVIDIA client instance
            deepseek_llm: DeepSeek LLM instance
            semantic_blocks: Blocks to analyze
            rules: Publisher rules
        
        Returns:
            Dict with comparison results
        """
        results = {
            "nvidia": None,
            "deepseek": None,
            "comparison": {}
        }
        
        # Run both models in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Submit NVIDIA task
            if nvidia_client:
                futures["nvidia"] = executor.submit(
                    self._run_nvidia_test,
                    nvidia_client,
                    semantic_blocks,
                    rules
                )
            
            # Submit DeepSeek task
            if deepseek_llm:
                futures["deepseek"] = executor.submit(
                    self._run_deepseek_test,
                    deepseek_llm,
                    semantic_blocks,
                    rules
                )
            
            # Collect results
            for model_name, future in futures.items():
                try:
                    results[model_name] = future.result(timeout=60)
                except Exception as e:
                    results[model_name] = {"error": str(e)}
        
        # Compare results
        results["comparison"] = self._compare_results(
            results.get("nvidia"),
            results.get("deepseek")
        )
        
        # Store test result
        self.test_results.append(results)
        
        return results
    
    def _run_nvidia_test(
        self,
        nvidia_client,
        semantic_blocks: List[Dict[str, Any]],
        rules: str
    ) -> Dict[str, Any]:
        """Run NVIDIA analysis."""
        start_time = time.time()
        
        try:
            # Simplified analysis for A/B testing
            blocks_summary = "\n".join([
                f"Block {i}: {b.get('text', '')[:100]}..."
                for i, b in enumerate(semantic_blocks[:10])
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": "Analyze academic manuscript structure. Return JSON."
                },
                {
                    "role": "user",
                    "content": f"Classify these blocks:\n\n{blocks_summary}"
                }
            ]
            
            response = nvidia_client.chat(messages, model="llama-70b", temperature=0.3)
            latency = time.time() - start_time
            
            return {
                "response": response,
                "latency": latency,
                "success": True,
                "model": "NVIDIA Llama 3.3 70B"
            }
        except Exception as e:
            return {
                "error": str(e),
                "latency": time.time() - start_time,
                "success": False,
                "model": "NVIDIA Llama 3.3 70B"
            }
    
    def _run_deepseek_test(
        self,
        deepseek_llm,
        semantic_blocks: List[Dict[str, Any]],
        rules: str
    ) -> Dict[str, Any]:
        """Run DeepSeek analysis."""
        start_time = time.time()
        
        try:
            import json
            blocks_json = json.dumps(semantic_blocks[:10], indent=2)
            
            prompt = f"Analyze these manuscript blocks:\n{blocks_json}\n\nReturn JSON classification."
            
            response = deepseek_llm.invoke(prompt)
            latency = time.time() - start_time
            
            return {
                "response": response.content,
                "latency": latency,
                "success": True,
                "model": "DeepSeek"
            }
        except Exception as e:
            return {
                "error": str(e),
                "latency": time.time() - start_time,
                "success": False,
                "model": "DeepSeek"
            }
    
    def _compare_results(
        self,
        nvidia_result: Optional[Dict],
        deepseek_result: Optional[Dict]
    ) -> Dict[str, Any]:
        """Compare NVIDIA and DeepSeek results."""
        comparison = {
            "both_succeeded": False,
            "latency_winner": None,
            "latency_difference": 0.0
        }
        
        if not nvidia_result or not deepseek_result:
            return comparison
        
        nvidia_success = nvidia_result.get("success", False)
        deepseek_success = deepseek_result.get("success", False)
        
        comparison["both_succeeded"] = nvidia_success and deepseek_success
        
        if nvidia_success and deepseek_success:
            nvidia_latency = nvidia_result.get("latency", 0)
            deepseek_latency = deepseek_result.get("latency", 0)
            
            comparison["latency_winner"] = "NVIDIA" if nvidia_latency < deepseek_latency else "DeepSeek"
            comparison["latency_difference"] = abs(nvidia_latency - deepseek_latency)
            comparison["nvidia_latency"] = nvidia_latency
            comparison["deepseek_latency"] = deepseek_latency
        
        return comparison
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all A/B tests."""
        if not self.test_results:
            return {"message": "No tests run yet"}
        
        nvidia_wins = sum(1 for r in self.test_results if r.get("comparison", {}).get("latency_winner") == "NVIDIA")
        deepseek_wins = sum(1 for r in self.test_results if r.get("comparison", {}).get("latency_winner") == "DeepSeek")
        
        return {
            "total_tests": len(self.test_results),
            "nvidia_wins": nvidia_wins,
            "deepseek_wins": deepseek_wins,
            "nvidia_win_rate": nvidia_wins / len(self.test_results) if self.test_results else 0
        }


# Global A/B testing instance
_ab_testing = ABTestingFramework()


def get_ab_testing() -> ABTestingFramework:
    """Get global A/B testing instance."""
    return _ab_testing
