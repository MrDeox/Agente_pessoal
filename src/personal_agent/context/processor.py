"""
Context Processor for Personal Agent

This module provides functionality for processing and understanding context in conversations.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from ..memory.models import MemoryItem
from ..llm.models import Message
import re


@dataclass
class Entity:
    """Represents an entity extracted from text."""
    id: str
    type: str  # person, organization, location, date, etc.
    value: str
    confidence: float
    metadata: Dict[str, Any] = None


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float
    metadata: Dict[str, Any] = None


@dataclass
class ContextRelevanceScore:
    """Represents a context relevance score."""
    score: float  # 0.0 to 1.0
    reasoning: str
    factors: Dict[str, float]


class ContextProcessor:
    """Processes and understands context in conversations."""
    
    def __init__(self):
        """Initialize the context processor."""
        self.entity_patterns = {
            "person": r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
            "date": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
            "time": r"\b(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            "url": r"\b(?:https?://|www\.)[^\s]+\b"
        }
    
    def create_context_aware_prompt(self, user_input: str, conversation_history: List[Dict[str, str]], 
                                  memory_context: str) -> List[Message]:
        """
        Create a context-aware prompt for the LLM.
        
        Args:
            user_input (str): The current user input
            conversation_history (List[Dict[str, str]]): Recent conversation history
            memory_context (str): Retrieved context from memory
            
        Returns:
            List[Message]: Context-aware messages for the LLM
        """
        messages = []
        
        # Add system message with context-aware instructions
        system_prompt = self._generate_context_aware_system_prompt()
        messages.append(Message(role="system", content=system_prompt))
        
        # Add context information
        if memory_context:
            context_message = f"Use the following context to inform your response:\n\n{memory_context}"
            messages.append(Message(role="system", content=context_message))
        
        # Add conversation history
        for turn in conversation_history[-6:]:  # Last 3 turns (6 messages)
            messages.append(Message(role=turn["role"], content=turn["content"]))
        
        # Add current user input
        messages.append(Message(role="user", content=user_input))
        
        return messages
    
    def _generate_context_aware_system_prompt(self) -> str:
        """Generate a context-aware system prompt."""
        return """You are an AI assistant with advanced context understanding capabilities. 
Your responses should be informed by the provided context and conversation history.

When responding:
1. Use relevant information from the provided context to inform your response
2. Maintain consistency with previous conversation turns
3. Identify and extract key entities and relationships from the conversation
4. Focus on the most relevant context for the current query
5. If the context contains conflicting information, acknowledge it and explain
6. When appropriate, ask clarifying questions to better understand the user's needs

Remember to be helpful, accurate, and concise in your responses."""
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text (str): Text to extract entities from
            
        Returns:
            List[Entity]: List of extracted entities
        """
        entities = []
        entity_id_counter = 0
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_id_counter += 1
                entities.append(Entity(
                    id=f"entity_{entity_id_counter}",
                    type=entity_type,
                    value=match.group(),
                    confidence=0.8 if entity_type in ["email", "phone", "url"] else 0.6,
                    metadata={"position": match.span()}
                ))
        
        # Additional entity extraction for specific patterns
        # Extract quoted phrases as potential entities
        quoted_matches = re.finditer(r'"([^"]*)"', text)
        for match in quoted_matches:
            entity_id_counter += 1
            entities.append(Entity(
                id=f"entity_{entity_id_counter}",
                type="quoted_phrase",
                value=match.group(1),
                confidence=0.7,
                metadata={"position": match.span()}
            ))
        
        return entities
    
    def extract_relationships(self, entities: List[Entity], text: str) -> List[Relationship]:
        """
        Extract relationships between entities from text.
        
        Args:
            entities (List[Entity]): List of entities
            text (str): Text to extract relationships from
            
        Returns:
            List[Relationship]: List of extracted relationships
        """
        relationships = []
        relationship_id_counter = 0
        
        # Simple relationship extraction based on proximity and keywords
        relationship_keywords = [
            "works at", "works for", "employed by", "member of", 
            "located in", "based in", "from", "to", "between",
            "associated with", "connected to", "related to"
        ]
        
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities):
                if i != j:
                    # Check if entities are close to each other in text
                    pos1 = entity1.metadata.get("position", (0, 0))
                    pos2 = entity2.metadata.get("position", (0, 0))
                    
                    # If entities are within 50 characters of each other
                    if abs(pos1[0] - pos2[0]) < 50:
                        # Check for relationship keywords between entities
                        start = min(pos1[1], pos2[1])
                        end = max(pos1[0], pos2[0])
                        between_text = text[start:end].lower()
                        
                        for keyword in relationship_keywords:
                            if keyword in between_text:
                                relationship_id_counter += 1
                                relationships.append(Relationship(
                                    source_entity_id=entity1.id,
                                    target_entity_id=entity2.id,
                                    relationship_type=keyword,
                                    confidence=0.7,
                                    metadata={"keyword": keyword, "text": between_text}
                                ))
                                break
        
        return relationships
    
    def score_context_relevance(self, user_input: str, context_items: List[MemoryItem]) -> List[Tuple[MemoryItem, ContextRelevanceScore]]:
        """
        Score the relevance of context items to the user input.
        
        Args:
            user_input (str): The current user input
            context_items (List[MemoryItem]): List of context items to score
            
        Returns:
            List[Tuple[MemoryItem, ContextRelevanceScore]]: List of context items with relevance scores
        """
        scored_items = []
        
        # Extract keywords from user input
        user_keywords = set(re.findall(r'\b\w+\b', user_input.lower()))
        
        for item in context_items:
            score, reasoning, factors = self._calculate_relevance_score(user_input, user_keywords, item)
            relevance_score = ContextRelevanceScore(
                score=score,
                reasoning=reasoning,
                factors=factors
            )
            scored_items.append((item, relevance_score))
        
        # Sort by relevance score (descending)
        scored_items.sort(key=lambda x: x[1].score, reverse=True)
        
        return scored_items
    
    def _calculate_relevance_score(self, user_input: str, user_keywords: set, context_item: MemoryItem) -> Tuple[float, str, Dict[str, float]]:
        """
        Calculate the relevance score for a context item.
        
        Args:
            user_input (str): The current user input
            user_keywords (set): Keywords extracted from user input
            context_item (MemoryItem): The context item to score
            
        Returns:
            Tuple[float, str, Dict[str, float]]: Score, reasoning, and factors
        """
        factors = {}
        
        # Convert context item content to string for comparison
        context_content = str(context_item.content).lower()
        context_keywords = set(re.findall(r'\b\w+\b', context_content))
        
        # Keyword overlap factor (0.0 to 1.0)
        if user_keywords and context_keywords:
            overlap = len(user_keywords.intersection(context_keywords))
            keyword_factor = overlap / len(user_keywords)
        else:
            keyword_factor = 0.0
        factors["keyword_overlap"] = keyword_factor
        
        # Type relevance factor
        type_relevance = {
            "conversation": 0.7,
            "knowledge": 0.9,
            "task": 0.6,
            "skill": 0.5
        }
        type_factor = type_relevance.get(context_item.type, 0.5)
        factors["type_relevance"] = type_factor
        
        # Recency factor (newer items are more relevant)
        # This would require timestamp information which we'll assume is available
        recency_factor = 1.0  # Simplified for now
        factors["recency"] = recency_factor
        
        # Calculate weighted score
        score = (
            0.5 * keyword_factor +
            0.3 * type_factor +
            0.2 * recency_factor
        )
        
        # Generate reasoning
        reasoning = f"Keyword overlap: {keyword_factor:.2f}, Type relevance: {type_factor:.2f}, Recency: {recency_factor:.2f}"
        
        return score, reasoning, factors
    
    def enhance_memory_with_context(self, memory_item: MemoryItem, entities: List[Entity], 
                                  relationships: List[Relationship]) -> MemoryItem:
        """
        Enhance a memory item with extracted entities and relationships.
        
        Args:
            memory_item (MemoryItem): The memory item to enhance
            entities (List[Entity]): List of extracted entities
            relationships (List[Relationship]): List of extracted relationships
            
        Returns:
            MemoryItem: Enhanced memory item
        """
        # Add entities and relationships to memory item metadata
        if memory_item.metadata is None:
            memory_item.metadata = {}
        
        memory_item.metadata["entities"] = [
            {
                "id": entity.id,
                "type": entity.type,
                "value": entity.value,
                "confidence": entity.confidence
            }
            for entity in entities
        ]
        
        memory_item.metadata["relationships"] = [
            {
                "source_entity_id": rel.source_entity_id,
                "target_entity_id": rel.target_entity_id,
                "relationship_type": rel.relationship_type,
                "confidence": rel.confidence
            }
            for rel in relationships
        ]
        
        return memory_item