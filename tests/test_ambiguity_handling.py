#!/usr/bin/env python3
"""
Tests for ambiguity handling functionality in the personal agent.
"""

import sys
import os
import unittest
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_agent.conversation.ambiguity_detector import AmbiguityDetector, AmbiguityType
from personal_agent.conversation.question_generator import QuestionGenerator
from personal_agent.conversation.interface import EnhancedConversationInterface
from personal_agent.conversation.state import DialogueAct
from personal_agent.core.agent import Agent


class TestAmbiguityDetector(unittest.TestCase):
    """Test cases for the AmbiguityDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = AmbiguityDetector()
    
    def test_entity_ambiguity_detection(self):
        """Test detection of entity ambiguities."""
        test_cases = [
            "What about it?",
            "Can you help me with them?",
            "I need that thing",
            "Tell me about this one"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                ambiguities = self.detector.detect_ambiguities(text)
                entity_ambiguities = [a for a in ambiguities if a.type == AmbiguityType.ENTITY_AMBIGUITY]
                self.assertGreater(len(entity_ambiguities), 0, 
                                 f"Should detect entity ambiguity in: {text}")
                self.assertGreaterEqual(entity_ambiguities[0].confidence, 0.5,
                                      f"Confidence should be reasonable for: {text}")
    
    def test_scope_ambiguity_detection(self):
        """Test detection of scope ambiguities."""
        test_cases = [
            "I want all of them",
            "Some of it would be fine",
            "A few of those things"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                ambiguities = self.detector.detect_ambiguities(text)
                scope_ambiguities = [a for a in ambiguities if a.type == AmbiguityType.SCOPE_AMBIGUITY]
                self.assertGreater(len(scope_ambiguities), 0,
                                 f"Should detect scope ambiguity in: {text}")
    
    def test_intent_ambiguity_detection(self):
        """Test detection of intent ambiguities."""
        test_cases = [
            "Can you help me?",
            "Could you do something?",
            "I need help with this"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                ambiguities = self.detector.detect_ambiguities(text)
                intent_ambiguities = [a for a in ambiguities if a.type == AmbiguityType.INTENT_AMBIGUITY]
                self.assertGreater(len(intent_ambiguities), 0,
                                 f"Should detect intent ambiguity in: {text}")
    
    def test_no_ambiguity_detection(self):
        """Test that clear requests don't trigger ambiguity detection."""
        test_cases = [
            "Set a reminder for 3 PM today",
            "Play classical music",
            "Search for Python programming tutorials",
            "Turn on the lights in the living room"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                ambiguities = self.detector.detect_ambiguities(text)
                high_confidence_ambiguities = [a for a in ambiguities if a.confidence >= 0.7]
                self.assertEqual(len(high_confidence_ambiguities), 0,
                               f"Should not detect high-confidence ambiguities in: {text}")
    
    def test_ambiguity_threshold(self):
        """Test the has_ambiguity method with different thresholds."""
        ambiguous_text = "What about it?"
        clear_text = "Set a timer for 10 minutes"
        
        # Test with default threshold
        self.assertTrue(self.detector.has_ambiguity(ambiguous_text))
        self.assertFalse(self.detector.has_ambiguity(clear_text))
        
        # Test with higher threshold
        self.assertFalse(self.detector.has_ambiguity(ambiguous_text, min_confidence=0.9))
        
        # Test with lower threshold
        # Even clear text might have some low-confidence ambiguities
        # So we'll test with a very clear command
        very_clear_text = "Turn off the bedroom light"
        self.assertFalse(self.detector.has_ambiguity(very_clear_text, min_confidence=0.3))


class TestQuestionGenerator(unittest.TestCase):
    """Test cases for the QuestionGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = QuestionGenerator()
        self.detector = AmbiguityDetector()
    
    def test_generate_clarification_question(self):
        """Test generation of clarification questions."""
        # Create a sample ambiguity detection
        ambiguity = self.detector.get_highest_confidence_ambiguity("What about it?")
        
        self.assertIsNotNone(ambiguity, "Should detect ambiguity in test text")
        
        # Generate a clarification question
        question = self.generator.generate_clarification_question(ambiguity)
        
        self.assertIsInstance(question, str, "Generated question should be a string")
        self.assertGreater(len(question), 0, "Generated question should not be empty")
        self.assertIn("?", question, "Generated question should contain a question mark")
    
    def test_generate_multiple_questions(self):
        """Test generation of multiple clarification questions."""
        # Detect ambiguities in a text with multiple ambiguities
        ambiguities = self.detector.detect_ambiguities("What about it and when?")
        
        self.assertGreater(len(ambiguities), 1, "Should detect multiple ambiguities")
        
        # Generate multiple questions
        questions = self.generator.generate_multiple_questions(ambiguities, max_questions=2)
        
        self.assertIsInstance(questions, list, "Generated questions should be a list")
        self.assertGreater(len(questions), 0, "Should generate at least one question")
        self.assertLessEqual(len(questions), 2, "Should not exceed max_questions limit")
        
        for question in questions:
            self.assertIsInstance(question, str, "Each question should be a string")
            self.assertIn("?", question, "Each question should contain a question mark")
    
    def test_generate_contextual_question(self):
        """Test generation of contextual questions."""
        question = self.generator.generate_contextual_question(
            "Can you help me?", 
            DialogueAct.REQUEST
        )
        
        self.assertIsInstance(question, str, "Generated question should be a string")
        self.assertGreater(len(question), 0, "Generated question should not be empty")


class TestConversationInterfaceWithAmbiguity(unittest.TestCase):
    """Test cases for the EnhancedConversationInterface with ambiguity handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.interface = EnhancedConversationInterface("test_user")
    
    def test_process_ambiguous_input(self):
        """Test processing of ambiguous user input."""
        ambiguous_input = "What about it?"
        
        response = self.interface.process_input(ambiguous_input)
        
        self.assertIsInstance(response, str, "Response should be a string")
        self.assertGreater(len(response), 0, "Response should not be empty")
        self.assertIn("?", response, "Response to ambiguous input should contain a question")
        
        # Check that the conversation state is now ASKING_CLARIFICATION
        context = self.interface.get_conversation_context()
        self.assertEqual(context["state"], "asking_clarification",
                        "Conversation state should be ASKING_CLARIFICATION after ambiguous input")
    
    def test_process_clear_input(self):
        """Test processing of clear user input."""
        clear_input = "What is the weather today?"
        
        response = self.interface.process_input(clear_input, "The weather is sunny.")
        
        self.assertIsInstance(response, str, "Response should be a string")
        self.assertGreater(len(response), 0, "Response should not be empty")
        # For clear input, we shouldn't be asking for clarification
        # (This assumes the template response doesn't happen to contain a question mark)
    
    def test_conversation_flow_with_ambiguity(self):
        """Test conversation flow with ambiguity handling."""
        # First, send an ambiguous input
        ambiguous_input = "Can you help me with this?"
        response1 = self.interface.process_input(ambiguous_input)
        
        # Check that we're asking for clarification
        context = self.interface.get_conversation_context()
        self.assertEqual(context["state"], "asking_clarification",
                        "Should be asking for clarification after ambiguous input")
        
        # Send a clarification response
        clarification_response = "I need help with my homework."
        response2 = self.interface.process_input(clarification_response)
        
        # Check that we're back to normal conversation flow
        context = self.interface.get_conversation_context()
        # After a clarification response, the state might be providing_information or in_progress
        # depending on how the dialogue act recognizer classifies the clarification response
        self.assertIn(context["state"], ["in_progress", "providing_information"],
                    "Should be in normal conversation flow after clarification")


class TestAgentWithAmbiguityHandling(unittest.TestCase):
    """Test cases for the Agent with ambiguity handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = Agent(user_id="test_user")
    
    def test_agent_handles_ambiguous_input(self):
        """Test that the agent can handle ambiguous input."""
        ambiguous_input = "What about it?"
        
        response = self.agent.process_input(ambiguous_input)
        
        self.assertIsInstance(response, str, "Response should be a string")
        self.assertGreater(len(response), 0, "Response should not be empty")
        self.assertIn("?", response, "Response to ambiguous input should contain a question")
        
        # Check conversation history
        self.assertGreaterEqual(len(self.agent.conversation_history), 2,
                               "Conversation history should contain at least 2 messages")
        self.assertEqual(self.agent.conversation_history[-2]["role"], "user",
                        "Second to last message should be from user")
        self.assertEqual(self.agent.conversation_history[-1]["role"], "assistant",
                        "Last message should be from assistant")
    
    def test_agent_handles_clarification_response(self):
        """Test that the agent can handle responses to clarification questions."""
        # First, send an ambiguous input to trigger a clarification question
        ambiguous_input = "Can you help me with this?"
        response1 = self.agent.process_input(ambiguous_input)
        
        # Verify we got a clarification question
        self.assertIn("?", response1, "First response should be a clarification question")
        
        # Send a clarification response
        clarification_response = "I need help with my homework."
        response2 = self.agent.process_input(clarification_response)
        
        # Verify we got an acknowledgment and follow-up
        self.assertIn("Thank you", response2, "Response should acknowledge clarification")
        self.assertIn("?", response2, "Response should contain a follow-up question")


def run_tests():
    """Run all tests for ambiguity handling."""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestAmbiguityDetector))
    suite.addTest(unittest.makeSuite(TestQuestionGenerator))
    suite.addTest(unittest.makeSuite(TestConversationInterfaceWithAmbiguity))
    suite.addTest(unittest.makeSuite(TestAgentWithAmbiguityHandling))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running ambiguity handling tests...")
    success = run_tests()
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)