import anthropic
from django.conf import settings
import re

def extract_text_from_image(image_data):
    """Extract and simplify text from image using Claude"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Extract the text from this image without any formatting or prefixes."""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
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
        
        content = str(message.content)
        
        if 'TextBlock' in content:
            match = re.search(r"text=['\"](.+?)['\"],\s*type=['\"]text['\"]", content, re.DOTALL)
            if match:
                content = match.group(1)
        
        return content.replace('\\n', ' ').replace('\n\n\n', '\n\n').strip()

    except Exception as e:
        print(f"Error with Claude API: {str(e)}")
        raise

def simplify_text(text):
    """Simplifies text using Claude API"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Simplify this text to make it easier to understand. Replace hard or complicated words with simple reallyeasy to understand words. Use clear, simple language while keeping the important information without removing anything or adding extra things. Just modify the sentences in easy to understand format and do not remove any sentence. Make it more readable but maintain the key points. Return just the simplified text without any prefixes or formatting and if the text is too short orthe input doesnt make sense, say so that its not a correct word, do not make up a sentence do only what is necessary. 
        And if the input it is in another language, translate it to english without modifying the context and the meaning, the output should be gramatically correct, and then simplify. Also do not add any prefixes or suffixes, just return the output directly
         :

        {text}"""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt.format(text=text)}]
        )

        content = str(message.content)
        
        if 'TextBlock' in content:
            match = re.search(r"text=['\"](.+?)['\"],\s*type=['\"]text['\"]", content, re.DOTALL)
            if match:
                content = match.group(1)
        
        return content.strip()

    except Exception as e:
        print(f"Error with Claude API: {str(e)}")
        raise

def suggest_title(text):
    """Generate a title suggestion using Claude API"""
    try:
        client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        prompt = """Generate a short, descriptive title (2-4 words) for this text. The title should be concise but meaningful. Just return the title directly without any explanation or prefix:

        {text}"""
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt.format(text=text)}]
        )
        
        response_text = str(message.content)
        
        if 'TextBlock' in response_text:
            match = re.search(r"text='(.*?)', type='text'", response_text)
            if match:
                return match.group(1)
                
        return response_text or "Untitled Book"

    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return "Untitled Book" 