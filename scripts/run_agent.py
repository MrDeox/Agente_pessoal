#!/usr/bin/env python3
"""
Main entry point for the Personal Agent conversation interface.

This script provides a simple command-line interface for interacting with the personal agent.
"""

import sys
import os

# Add the src directory to the Python path so we can import the agent module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_agent.core.agent import Agent

def main():
    """
    Main function to run the conversation interface.
    """
    # Display LLM setup instructions if needed
    print("Personal Agent - LLM Integration")
    print("=" * 35)
    print("To use the LLM features, you can use either OpenAI or OpenRouter:")
    print("For OpenAI:")
    print("  export PA_LLM__PROVIDER='openai'")
    print("  export PA_LLM__API_KEY='your-openai-api-key'")
    print("  export PA_LLM__MODEL='gpt-4'  # or gpt-3.5-turbo, etc.")
    print("")
    print("For OpenRouter (free option available):")
    print("  export PA_LLM__PROVIDER='openrouter'")
    print("  export PA_LLM__API_KEY='your-openrouter-api-key'")
    print("  export PA_LLM__MODEL='qwen/qwen3-coder:free'  # or other models")
    print("")
    
    # Create an instance of the agent
    user_id = input("Enter your user ID (or press Enter for 'default_user'): ").strip()
    if not user_id:
        user_id = "default_user"
    
    agent = Agent(user_id=user_id)
    
    # Display welcome message
    welcome_message = agent.get_welcome_message()
    print(welcome_message)
    print("-" * 50)
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\nAgent: {agent.process_input(user_input)}")
                break
            
            # Handle special commands
            if user_input.lower() == 'remember preference':
                preference = input("What preference would you like me to remember? ").strip()
                if agent.remember_preference(preference):
                    print("Agent: I've remembered that preference.")
                else:
                    print("Agent: Sorry, I couldn't remember that preference.")
                continue
            
            if user_input.lower() == 'remember fact':
                fact = input("What fact would you like me to remember? ").strip()
                if agent.remember_fact(fact):
                    print("Agent: I've remembered that fact.")
                else:
                    print("Agent: Sorry, I couldn't remember that fact.")
                continue
            
            if user_input.lower() == 'feedback stats':
                stats = agent.get_feedback_statistics()
                print(f"Agent: Your feedback statistics:")
                print(f"  Total feedback: {stats.get('total_feedback', 0)}")
                print(f"  Average rating: {stats.get('average_rating', 0):.2f}")
                print(f"  Positive feedback: {stats.get('positive_feedback', 0)}")
                print(f"  Negative feedback: {stats.get('negative_feedback', 0)}")
                continue
            
            # Handle empty input
            if not user_input:
                print("Agent: Please enter a message or type 'quit' to exit.")
                continue
            
            # Process input and get response
            response = agent.process_input(user_input)
            
            # Get the ID of the last assistant response
            response_id = None
            if agent.conversation_history and agent.conversation_history[-1].get("role") == "assistant":
                response_id = agent.conversation_history[-1].get("id")
            
            print(f"Agent: {response}")
            
            # Display conversation state for debugging
            if agent.config.debug:
                context = agent.conversation_interface.get_conversation_context()
                print(f"[DEBUG] State: {context['state']}, Act: {context['dialogue_act']}, Turn: {context['turn_count']}")
            
            # Ask for feedback on the response
            if response_id:
                feedback_input = input("\nHow was this response? (1-5 for rating, or 's' to skip): ").strip()
                if feedback_input.lower() != 's' and feedback_input:
                    try:
                        if feedback_input in ['+', 'thumbs up']:
                            agent.collect_thumbs_feedback(response_id, True)
                            print("Thanks for the positive feedback!")
                        elif feedback_input in ['-', 'thumbs down']:
                            agent.collect_thumbs_feedback(response_id, False)
                            print("Thanks for the feedback. I'll try to improve.")
                        else:
                            rating = int(feedback_input)
                            if 1 <= rating <= 5:
                                comment = input("Any additional comments? (optional): ").strip()
                                if agent.collect_rating_feedback(response_id, rating, comment or None):
                                    print("Thanks for your feedback!")
                                else:
                                    print("Sorry, there was an issue saving your feedback.")
                            else:
                                print("Please enter a rating between 1 and 5.")
                    except ValueError:
                        print("Invalid input. Skipping feedback collection.")
            
        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye! Have a great day!")
            break
        except EOFError:
            print("\n\nAgent: Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\nAgent: Sorry, I encountered an error: {str(e)}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()