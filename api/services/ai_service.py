"""
AI Service provider for text processing and image analysis.
Supports both Claude and Gemini AI models through environment-based configuration.
"""

import anthropic
import google.generativeai as genai
from django.conf import settings
import re
import base64

class AIServiceProvider:

    def __init__(self):
        """Initialize the AI service with the configured provider"""
        self.provider = 'gemini' if settings.GEMINI_API_KEY else 'claude'
        if self.provider == 'gemini':
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        else:
            self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)

    def clean_response(self, response):
        """Clean response text from any TextBlock prefixes/suffixes"""
        text = str(response)
        # Remove TextBlock prefixes and suffixes
        text = re.sub(r'\[?TextBlock\(text=[\'"]*', '', text)
        text = re.sub(r'[\'"]*,?\s*type=[\'"]text[\'"]\)?]?', '', text)
        # Clean up any remaining artifacts
        text = text.replace('\\n', '\n').strip()
        return text

    def extract_text_from_image(self, image_data):
        """
        Extract text from image using selected AI provider.
        
        Args:
            image_data (str): Base64 encoded image data
            
        Returns:
            str: Extracted text from the image
            
        Raises:
            Exception: If there's an error in API processing
        """
        try:
            if self.provider == 'gemini-1.5-flash':
                image_bytes = base64.b64decode(image_data)
                response = self.vision_model.generate_content(
                    ["Extract the text from this image without any formatting or prefixes.",
                     {"mime_type": "image/jpeg", "data": image_bytes}]
                )
                return self.clean_response(response.text)
            else:
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract the text from this image without any formatting or prefixes."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            }
                        ]
                    }]
                )
                return str(message.content).strip()

        except Exception as e:
            print(f"Error with {self.provider} API: {str(e)}")
            raise

    def simplify_text(self, text):
        """
        Simplify text using selected AI provider.
        
        Args:
            text (str): Text to simplify
            
        Returns:
            str: Simplified text
            
        Raises:
            Exception: If there's an error in API processing
        """
        try:
            prompt = """Simplify this text to make it easier to understand. Replace hard or complicated words with simple easy to understand words. Use clear, simple language while keeping the important information without removing anything or adding extra things. Just modify the sentences in easy to understand format and do not remove any sentence. Make it more readable but maintain the key points. If the text is too short or doesn't make sense, say it's not a correct word, do not make up a sentence. If the input is in another language, translate it to English without modifying the context and meaning, the output should be grammatically correct, and then simplify, do not add any prefixes such as [TextBlock(text= and any other prefixes:

            {text}"""

            if self.provider == 'gemini':
                response = self.model.generate_content(prompt.format(text=text))
                return self.clean_response(response.text)
            else:
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt.format(text=text)}]
                )
                return str(message.content).strip()

        except Exception as e:
            print(f"Error with {self.provider} API: {str(e)}")
            raise

    def suggest_title(self, text):
        """
        Generate title suggestion using selected AI provider.
        
        Args:
            text (str): Text to generate title for
            
        Returns:
            str: Generated title or "Untitled Book" if generation fails
            
        Raises:
            Exception: If there's an error in API processing
        """
        try:
            prompt = """Generate a short, descriptive title (2-4 words) for this text. The title should be concise but meaningful. Just return the title directly without any explanation or prefix:

            {text}"""

            if self.provider == 'gemini':
                response = self.model.generate_content(prompt.format(text=text))
                return self.clean_response(response.text)
            else:
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=50,
                    messages=[{"role": "user", "content": prompt.format(text=text)}]
                )
                return str(message.content).strip() or "Untitled Book"

        except Exception as e:
            print(f"Error generating title: {str(e)}")
            return "Untitled Book"


ai_service = AIServiceProvider()

def extract_text_from_image(image_data):
    """Wrapper function for extract_text_from_image"""
    return ai_service.extract_text_from_image(image_data)

def simplify_text(text):
    """Wrapper function for simplify_text"""
    return ai_service.simplify_text(text)

def suggest_title(text):
    """Wrapper function for suggest_title"""
    return ai_service.suggest_title(text)
