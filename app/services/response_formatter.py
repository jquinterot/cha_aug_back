"""
Response formatter service for generating polite and customer-focused responses.
"""
import random
import re
from typing import Dict, List, Optional, Any

class ResponseFormatter:
    """Handles formatting responses to be more polite and customer-focused."""
    
    # Common polite phrases
    _ACKNOWLEDGEMENTS = [
        "Thank you for your question about {topic}.",
        "I appreciate you asking about {topic}.",
        "That's a great question about {topic}.",
        "I'm happy to help with your question about {topic}.",
        "Thanks for your interest in {topic}.",
        "I'd be glad to share what I know about {topic}.",
    ]
    
    _POSITIVE_LEADS = [
        "I found that ",
        "Based on the information available, ",
        "According to our records, ",
        "I can share that ",
        "Here's what I know: ",
        "From what I understand, ",
        "I've learned that ",
    ]
    
    _UNABLE_TO_FIND = [
        "I'm sorry, but I couldn't find specific information about {topic} in our knowledge base.",
        "I apologize, but I don't have detailed information about {topic} at the moment.",
        "I regret to inform you that I couldn't locate specific details about {topic} in our records.",
        "I'm afraid I don't have specific information about {topic} available right now.",
    ]
    
    _APOLOGIES = [
        "I apologize for any inconvenience this may cause.",
        "I'm sorry I couldn't be more helpful with this specific question.",
        "I regret that I don't have that information available.",
    ]
    
    _SUGGESTIONS = [
        "Would you like me to search for something else related to this topic?",
        "Is there another aspect of this topic I can help you with?",
        "Would you like me to rephrase the search with different terms?",
        "Could you provide more details about what specific information you're looking for?",
        "Would you like me to look for similar information that might be helpful?",
    ]
    
    _CLOSINGS = [
        "Please don't hesitate to ask if you have any other questions!",
        "Feel free to reach out if there's anything else I can assist you with!",
        "I'm here to help with any other questions you might have!",
        "Let me know if you'd like to explore this topic further!",
        "Is there anything else you'd like to know about this topic?",
    ]
    
    _EMPTY_QUERY_RESPONSES = [
        "I noticed your message was empty. I'm here to help! Could you tell me what you'd like to know?",
        "Hello! I didn't receive your question. What can I help you with today?",
        "I'm ready to assist you! Could you please share your question or topic of interest?",
    ]
    
    _EMPTY_QUERY_SUGGESTIONS = [
        "You might want to ask about:",
        "Here are some topics you could ask about:",
        "Consider asking about:",
        "Some popular topics include:",
    ]
    
    _SAMPLE_TOPICS = [
        "our products and services",
        "pricing information",
        "how to get started",
        "feature details",
    ]
    
    @classmethod
    def _get_topic(cls, query: str) -> str:
        """Extract the main topic from the query."""
        # Clean and get first meaningful words as topic
        query = query.strip()
        if not query:
            return "this topic"
            
        # Remove question marks and split
        clean_query = query.rstrip('?').strip()
        
        # Skip common question starters
        question_starters = ["what is", "what's", "who is", "who's", "tell me", "how to", 
                           "can you", "could you", "would you", "please", "i need"]
        
        for starter in question_starters:
            if clean_query.lower().startswith(starter):
                clean_query = clean_query[len(starter):].strip()
                break
                
        # Get first few words as topic
        words = clean_query.split()
        if len(words) > 5:
            return ' '.join(words[:5]) + '...'
        return clean_query or "this topic"
    
    @classmethod
    def _format_sources(cls, sources: List[Dict]) -> str:
        """Format sources into a readable string."""
        if not sources:
            return ""
            
        parts = ["\n\nHere are the sources I found:"]
        for i, source in enumerate(sources[:3], 1):  # Limit to top 3 sources
            source_name = source.get('source', 'a document')
            
            # Handle special test document naming
            if isinstance(source_name, str):
                # Check if this is the weird test document
                if 'weird' in source_name.lower() and 'test' in source_name.lower():
                    source_name = 'Weird Test Document for RAG System'
                else:
                    # Clean up other document names
                    if source_name.startswith('/'):
                        source_name = source_name.split('/')[-1]  # Get filename
                    source_name = source_name.replace('_', ' ').replace('.pdf', '').title()
            
            # Only show score in debug mode or if explicitly enabled
            score_str = ""
            if False:  # Change to True to enable score display
                score = source.get('score', 0)
                if isinstance(score, (int, float)):
                    score_str = f" (relevance: {score:.2f})"
            
            parts.append(f"{i}. Source: {source_name}{score_str}")
            
        return "\n".join(parts)
    
    @classmethod
    def _clean_response_text(cls, text: str) -> str:
        """Clean up response text formatting and remove technical markers."""
        if not text:
            return ""
            
        # Remove special test markers and clean up their content
        text = re.sub(
            r'SPECIAL_TEST_INFO_START\s*(.*?)\s*SPECIAL_TEST_INFO_END', 
            lambda m: cls._format_special_content(m.group(1)), 
            text, 
            flags=re.DOTALL
        )
        
        # Clean up any remaining technical markers or weird formatting
        text = re.sub(r'WEIRD_ENTRY_\d+:', '', text)  # Remove WEIRD_ENTRY_X: prefixes
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Fix common punctuation and formatting issues
        text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
        text = re.sub(r'\.{3,}', '...', text)  # Normalize ellipses
        text = re.sub(r'\s*\n\s*', '\n', text)  # Clean up line breaks
        
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
            
        # Ensure proper sentence spacing
        text = re.sub(r'\.(\s*[A-Z])', lambda m: '. ' + m.group(1).strip().upper(), text)
            
        return text
    
    @classmethod
    def _format_special_content(cls, content: str) -> str:
        """Format special content blocks from the PDF."""
        if not content:
            return ""
            
        # Split into lines and clean each line
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Remove WEIRD_ENTRY_X: prefixes and clean up each line
        cleaned_lines = []
        for line in lines:
            # Remove WEIRD_ENTRY_X: prefix if present
            line = re.sub(r'^WEIRD_ENTRY_\d+:\s*', '', line)
            if line:  # Only add non-empty lines
                cleaned_lines.append(line)
        
        # Join with proper punctuation and formatting
        formatted = "\n• " + "\n• ".join(cleaned_lines)
        
        return formatted
    
    @classmethod
    def _clean_and_format_list(cls, text: str) -> str:
        """Clean and format a list-style response with proper bullet points and indentation."""
        if not text:
            return ""
            
        # Split into lines and clean each line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Format each line with bullet points
        formatted_lines = []
        for line in lines:
            # Handle different list markers (e.g., "-", "*", "•", numbers, etc.)
            if re.match(r'^[\-\*•]\s+', line):
                # Replace bullet point with a clean one
                line = '• ' + re.sub(r'^[\-\*•]\s+', '', line)
            elif re.match(r'^\d+\.\s+', line):
                # Keep numbered lists as is
                pass
            else:
                # Add bullet point to lines that don't have one
                line = '• ' + line
                
            # Ensure proper capitalization and punctuation
            if not line.endswith(('.', '!', '?')):
                line = line.rstrip('.') + '.'
                
            formatted_lines.append(line)
            
        return '\n'.join(formatted_lines)

    @classmethod
    def _format_factual_response(
        cls,
        topic: str,
        facts: List[str],
        sources: List[Dict]
    ) -> str:
        """Format a factual response with a friendly tone."""
        # Start with a friendly introduction
        introduction = random.choice([
            f"I'd be happy to share some information about {topic}!",
            f"Here's what I know about {topic}:",
            f"Let me tell you about {topic}:",
            f"I can share some interesting details about {topic}:"
        ])
        
        # Format the facts with bullet points
        formatted_facts = "\n\n" + "\n".join([f"• {fact}" for fact in facts])
        
        # Add a friendly closing
        closing = random.choice([
            "\n\nI hope you found this information about {topic} helpful!",
            "\n\nIs there anything specific about {topic} you'd like to explore further?",
            "\n\nLet me know if you'd like to know more about {topic} or any related topics!",
            "\n\n{pronoun} is quite fascinating, don't you think? Let me know if you have any other questions!"
        ]).format(
            topic=topic,
            pronoun=random.choice(["It", "This place", "This country", "This region"])
        )
        
        # Add sources if available
        sources_text = cls._format_sources(sources) if sources else ""
        
        # Combine all parts
        return f"{introduction}{formatted_facts}{sources_text}{closing}"

    @classmethod
    def format_response(
        cls,
        response_text: str,
        query: str,
        sources: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """
        Format a response to be more polite and customer-focused.
        
        Args:
            response_text: The raw response text from the RAG system
            query: The user's original query
            sources: List of source documents (optional)
            
        Returns:
            Dict containing formatted response and sources
        """
        # Handle empty query
        if not query.strip():
            return cls.format_empty_query()
            
        # Extract main topic from query
        topic = cls._get_topic(query)
        sources = sources or []
        
        # Clean the response text
        response_text = cls._clean_response_text(response_text)
        
        # Check if this is a factual response that could benefit from bullet points
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        # If we have multiple lines that look like facts, format them nicely
        if len(lines) > 2 and any('*' in line or '-' in line or line[0].isdigit() for line in lines):
            # Extract facts from bullet points or numbered lists
            facts = []
            for line in lines:
                # Remove bullet points or numbers
                line = re.sub(r'^[\s*\-•]\s*', '', line)  # Remove bullet points
                line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove numbers
                if line and len(line.split()) > 2:  # Only include lines with actual content
                    facts.append(line)
            
            if facts:
                return {
                    "answer": cls._format_factual_response(topic, facts, sources),
                    "sources": sources
                }
        
        # For regular responses, use the standard formatting
        parts = []
        
        # Start with a friendly greeting
        greeting = random.choice([
            f"I'd be happy to share what I know about {topic}.\n\n",
            f"Here's some information about {topic} that might help.\n\n",
            f"I can certainly help with information about {topic}.\n\n",
            f"Thanks for asking about {topic}. Here's what I found:\n\n"
        ])
        parts.append(greeting)
        
        # Add the actual response text
        if response_text.strip():
            parts.append(response_text)
        
        # Add a friendly closing
        closing = random.choice([
            "\n\nI hope this information is helpful!",
            "\n\nLet me know if you'd like to know more!",
            "\n\nIs there anything specific you'd like to know more about?",
            "\n\nFeel free to ask if you have any other questions!"
        ])
        parts.append(closing)
        
        # Combine all parts and clean up
        formatted_response = ''.join(parts)
        formatted_response = cls._clean_response_text(formatted_response)
        
        # Ensure proper capitalization and spacing
        if formatted_response:
            formatted_response = formatted_response[0].upper() + formatted_response[1:]
        
        return {
            "answer": formatted_response,
            "sources": sources
        }
    
    @classmethod
    def format_empty_query(cls) -> Dict[str, any]:
        """Format a response for empty queries."""
        response = [
            random.choice(cls._EMPTY_QUERY_RESPONSES),
            random.choice(cls._EMPTY_QUERY_SUGGESTIONS),
            ", ".join(cls._SAMPLE_TOPICS[:-1]) + ", or " + cls._SAMPLE_TOPICS[-1] + "."
        ]
        
        return {
            "answer": " ".join(response),
            "sources": []
        }
    
    @classmethod
    def format_not_found_response(cls, query: str) -> Dict[str, any]:
        """Format a response when no information is found."""
        topic = cls._get_topic(query)
        
        # Build a comprehensive not-found response
        response = [
            random.choice(cls._UNABLE_TO_FIND).format(topic=topic),
            random.choice(cls._APOLOGIES),
            random.choice(cls._SUGGESTIONS),
            "\n" + random.choice(cls._CLOSINGS)
        ]
        
        # Clean up and join
        response_text = " ".join([r for r in response if r])
        response_text = cls._clean_response_text(response_text)
        
        return {
            "answer": response_text,
            "sources": []
        }
