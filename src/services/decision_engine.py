"""Advanced decision engine for complex logical reasoning and evaluation."""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from ..core.config import get_settings
from ..core.gemini_client import get_gemini_client


class DecisionEngine:
    """Advanced decision engine with multi-step reasoning capabilities."""
    
    def __init__(self):
        """Initialize the decision engine."""
        self.settings = get_settings()
        self.gemini_client = get_gemini_client()
    
    async def analyze_complex_query(
        self, 
        query: str, 
        retrieved_chunks: List[Dict[str, Any]],
        domain_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complex multi-step analysis of a query against document chunks.
        
        Args:
            query: The user query
            retrieved_chunks: Relevant document chunks
            domain_context: Optional domain-specific context
            
        Returns:
            Comprehensive analysis result
        """
        try:
            # Step 1: Decompose complex query into sub-questions
            sub_questions = await self._decompose_query(query, domain_context)
            
            # Step 2: Analyze each sub-question
            sub_analyses = []
            for sub_q in sub_questions:
                analysis = await self._analyze_sub_question(sub_q, retrieved_chunks)
                sub_analyses.append(analysis)
            
            # Step 3: Synthesize results with logical reasoning
            final_analysis = await self._synthesize_analysis(
                query, sub_questions, sub_analyses, retrieved_chunks
            )
            
            # Step 4: Validate consistency and detect contradictions
            validated_analysis = await self._validate_consistency(final_analysis, retrieved_chunks)
            
            return validated_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze complex query: {e}")
            raise
    
    async def _decompose_query(self, query: str, domain_context: Optional[str] = None) -> List[str]:
        """
        Decompose a complex query into simpler sub-questions.
        
        Args:
            query: The complex query to decompose
            domain_context: Domain-specific context
            
        Returns:
            List of sub-questions
        """
        try:
            decomposition_prompt = f"""
            Analyze the following query and break it down into simpler, more specific sub-questions that need to be answered to fully address the original query.
            
            Original Query: "{query}"
            Domain Context: {domain_context or "General"}
            
            Guidelines:
            - Each sub-question should be specific and answerable
            - Cover all aspects of the original query
            - Include questions about conditions, limitations, exceptions
            - Consider temporal aspects (when, how long, etc.)
            - Include questions about scope and applicability
            
            Respond with a JSON array of sub-questions:
            ["sub-question 1", "sub-question 2", ...]
            
            Example for "Does this policy cover knee surgery?":
            ["Is knee surgery explicitly mentioned as covered?", "Are there any exclusions for knee surgery?", "What conditions must be met for knee surgery coverage?", "Are there waiting periods for knee surgery?", "What documentation is required for knee surgery claims?"]
            """
            
            response = await self.gemini_client.generate_content(decomposition_prompt)
            
            try:
                sub_questions = json.loads(response.strip())
                logger.debug(f"Decomposed query into {len(sub_questions)} sub-questions")
                return sub_questions
            except json.JSONDecodeError:
                logger.warning("Failed to parse sub-questions, using original query")
                return [query]
                
        except Exception as e:
            logger.error(f"Failed to decompose query: {e}")
            return [query]
    
    async def _analyze_sub_question(
        self, 
        sub_question: str, 
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a single sub-question against document chunks.
        
        Args:
            sub_question: The sub-question to analyze
            retrieved_chunks: Relevant document chunks
            
        Returns:
            Analysis result for the sub-question
        """
        try:
            # Prepare context from chunks
            context_parts = []
            for i, chunk in enumerate(retrieved_chunks[:5]):  # Limit to top 5 chunks
                context_parts.append(f"Chunk {i+1}: {chunk.get('text', '')}")
            
            context = "\n\n".join(context_parts)
            
            analysis_prompt = f"""
            Analyze the following sub-question based on the provided document context.
            
            Sub-question: "{sub_question}"
            
            Document Context:
            {context}
            
            Provide a detailed analysis in JSON format:
            {{
                "sub_question": "{sub_question}",
                "is_addressed": true/false,
                "evidence": ["specific text from document that supports the answer"],
                "answer": "direct answer to the sub-question",
                "confidence": 0.0-1.0,
                "limitations": ["any limitations or conditions found"],
                "source_chunks": [chunk indices that provided evidence]
            }}
            
            Guidelines:
            - Be precise and specific
            - Quote exact text from the document as evidence
            - Note any ambiguities or unclear areas
            - Consider both explicit and implicit information
            """
            
            response = await self.gemini_client.generate_content(analysis_prompt)
            
            try:
                analysis = json.loads(response.strip())
                return analysis
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse sub-question analysis for: {sub_question}")
                return {
                    "sub_question": sub_question,
                    "is_addressed": False,
                    "evidence": [],
                    "answer": "Unable to analyze due to parsing error",
                    "confidence": 0.0,
                    "limitations": ["Analysis parsing failed"],
                    "source_chunks": []
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze sub-question '{sub_question}': {e}")
            return {
                "sub_question": sub_question,
                "is_addressed": False,
                "evidence": [],
                "answer": f"Analysis failed: {str(e)}",
                "confidence": 0.0,
                "limitations": ["Analysis error"],
                "source_chunks": []
            }
    
    async def _synthesize_analysis(
        self,
        original_query: str,
        sub_questions: List[str],
        sub_analyses: List[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize sub-question analyses into a comprehensive answer.
        
        Args:
            original_query: The original query
            sub_questions: List of sub-questions
            sub_analyses: Analysis results for each sub-question
            retrieved_chunks: Original document chunks
            
        Returns:
            Synthesized analysis result
        """
        try:
            # Prepare synthesis context
            synthesis_context = []
            for i, analysis in enumerate(sub_analyses):
                synthesis_context.append(f"""
                Sub-question {i+1}: {analysis.get('sub_question', '')}
                Answer: {analysis.get('answer', '')}
                Evidence: {analysis.get('evidence', [])}
                Confidence: {analysis.get('confidence', 0.0)}
                Limitations: {analysis.get('limitations', [])}
                """)
            
            synthesis_prompt = f"""
            Based on the analysis of sub-questions, provide a comprehensive answer to the original query.
            
            Original Query: "{original_query}"
            
            Sub-question Analyses:
            {chr(10).join(synthesis_context)}
            
            Synthesize this information into a comprehensive response in JSON format:
            {{
                "isCovered": true/false,
                "conditions": ["list of all conditions and requirements"],
                "limitations": ["list of all limitations and exclusions"],
                "clause_reference": {{
                    "page": "page number or null",
                    "clause_title": "relevant clause title or null"
                }},
                "rationale": "comprehensive explanation combining all sub-analyses",
                "confidence_score": 0.0-1.0,
                "evidence_strength": "weak/moderate/strong",
                "completeness": "partial/complete",
                "contradictions": ["any contradictions found in the analysis"],
                "gaps": ["information gaps or unclear areas"]
            }}
            
            Guidelines:
            - Synthesize information from all sub-analyses
            - Identify and resolve any contradictions
            - Provide a clear, definitive answer when possible
            - Note any uncertainties or information gaps
            - Calculate overall confidence based on sub-analysis confidence scores
            """
            
            response = await self.gemini_client.generate_content(synthesis_prompt)
            
            try:
                synthesis = json.loads(response.strip())
                logger.debug("Successfully synthesized complex analysis")
                return synthesis
            except json.JSONDecodeError:
                logger.warning("Failed to parse synthesis result")
                return self._create_fallback_synthesis(original_query, sub_analyses)
                
        except Exception as e:
            logger.error(f"Failed to synthesize analysis: {e}")
            return self._create_fallback_synthesis(original_query, sub_analyses)
    
    async def _validate_consistency(
        self, 
        analysis: Dict[str, Any], 
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate the consistency of the analysis and detect contradictions.
        
        Args:
            analysis: The synthesized analysis
            retrieved_chunks: Original document chunks
            
        Returns:
            Validated and potentially corrected analysis
        """
        try:
            validation_prompt = f"""
            Review the following analysis for logical consistency and potential contradictions.
            
            Analysis to Validate:
            {json.dumps(analysis, indent=2)}
            
            Check for:
            1. Internal logical consistency
            2. Contradictions between conditions and limitations
            3. Alignment between confidence score and evidence strength
            4. Completeness of the rationale
            
            Provide validation results in JSON format:
            {{
                "is_consistent": true/false,
                "consistency_issues": ["list of any consistency problems found"],
                "suggested_corrections": {{
                    "field_name": "corrected_value"
                }},
                "validation_confidence": 0.0-1.0,
                "final_recommendation": "accept/revise/reject"
            }}
            """
            
            response = await self.gemini_client.generate_content(validation_prompt)
            
            try:
                validation = json.loads(response.strip())
                
                # Apply corrections if suggested
                if validation.get("suggested_corrections"):
                    for field, correction in validation["suggested_corrections"].items():
                        if field in analysis:
                            analysis[field] = correction
                
                # Add validation metadata
                analysis["validation"] = {
                    "is_consistent": validation.get("is_consistent", True),
                    "consistency_issues": validation.get("consistency_issues", []),
                    "validation_confidence": validation.get("validation_confidence", 1.0),
                    "recommendation": validation.get("final_recommendation", "accept")
                }
                
                logger.debug("Analysis validation completed")
                return analysis
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse validation result")
                analysis["validation"] = {
                    "is_consistent": True,
                    "consistency_issues": ["Validation parsing failed"],
                    "validation_confidence": 0.5,
                    "recommendation": "accept"
                }
                return analysis
                
        except Exception as e:
            logger.error(f"Failed to validate consistency: {e}")
            analysis["validation"] = {
                "is_consistent": True,
                "consistency_issues": [f"Validation error: {str(e)}"],
                "validation_confidence": 0.5,
                "recommendation": "accept"
            }
            return analysis
    
    def _create_fallback_synthesis(
        self, 
        original_query: str, 
        sub_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a fallback synthesis when the main synthesis fails.
        
        Args:
            original_query: The original query
            sub_analyses: Sub-question analyses
            
        Returns:
            Fallback synthesis result
        """
        # Simple aggregation of sub-analyses
        all_conditions = []
        all_limitations = []
        all_evidence = []
        confidence_scores = []
        
        for analysis in sub_analyses:
            if analysis.get("limitations"):
                all_limitations.extend(analysis["limitations"])
            if analysis.get("evidence"):
                all_evidence.extend(analysis["evidence"])
            if analysis.get("confidence"):
                confidence_scores.append(analysis["confidence"])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "isCovered": any(a.get("is_addressed", False) for a in sub_analyses),
            "conditions": all_conditions,
            "limitations": all_limitations,
            "clause_reference": {"page": None, "clause_title": "Multiple sources"},
            "rationale": f"Analysis based on {len(sub_analyses)} sub-questions. Fallback synthesis used due to processing limitations.",
            "confidence_score": avg_confidence,
            "evidence_strength": "moderate" if avg_confidence > 0.6 else "weak",
            "completeness": "partial",
            "contradictions": [],
            "gaps": ["Detailed synthesis unavailable"]
        }


# Global decision engine instance
_decision_engine = None


def get_decision_engine() -> DecisionEngine:
    """Get or create the global decision engine instance."""
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionEngine()
    return _decision_engine
