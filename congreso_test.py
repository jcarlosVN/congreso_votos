import anthropic
import os
from dotenv import load_dotenv
import mimetypes
from pathlib import Path

def get_file_info(file_path):
    """Get file information and determine if it's an image or document"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    # Document extensions  
    document_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    
    extension = file_path.suffix.lower()
    
    if extension in image_extensions:
        return {
            'type': 'image',
            'mime_type': f'image/{extension[1:]}' if extension != '.jpg' else 'image/jpeg'
        }
    elif extension in document_extensions:
        mime_type = 'application/pdf' if extension == '.pdf' else 'application/octet-stream'
        return {
            'type': 'document', 
            'mime_type': mime_type
        }
    else:
        # Try to detect from MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('image/'):
            return {'type': 'image', 'mime_type': mime_type}
        else:
            return {'type': 'document', 'mime_type': mime_type or 'application/octet-stream'}

def analyze_file(file_path, custom_prompt=None):
    """Analyze a file (PDF or image) using Claude API"""
    load_dotenv()
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found. Please check your .env file")
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Get file information
    file_info = get_file_info(file_path)
    file_name = Path(file_path).name
    
    print(f"📁 Processing: {file_name}")
    print(f"📋 Type: {file_info['type']}")
    print(f"🔍 MIME: {file_info['mime_type']}")
    print("-" * 40)
    
    # Upload the file
    with open(file_path, "rb") as f:
        file_upload = client.beta.files.upload(
            file=(file_name, f, file_info['mime_type'])
        )
    
    # Set default prompt based on file type
    if custom_prompt:
        prompt_text = custom_prompt
    elif file_info['type'] == 'image':
        prompt_text = "Please give me the resut."
    else:  # document
        prompt_text = "Please give me the resut"
    
    # Create content based on file type
    if file_info['type'] == 'image':
        content = [
            {
                "type": "image",
                "source": {
                    "type": "file",
                    "file_id": file_upload.id
                }
            },
            {
                "type": "text",
                "text": prompt_text
            }
        ]
    else:  # document
        content = [
            {
                "type": "document",
                "source": {
                    "type": "file",
                    "file_id": file_upload.id
                }
            },
            {
                "type": "text",
                "text": prompt_text
            }
        ]
    
    # Create message
    message = client.beta.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=5000,
        temperature=0.3,
        system="you are a assitant that analize the preruvian congressman votes. the votes have a format that allows read easyly: APP ACUÑA PERALTA, MARÍA GRIMANEZA SI +++ {team: APP} {congressman name: ACUÑA PERALTA, MARÍA GRIMANEZA} {vote result: SI +++}; PP CALLE LOBATÓN, DIGNA LP {team: PP} {congressman name: CALLE LOBATÓN, DIGNA} {vote result: LP}; AP-PIS TUDELA GUTIÉRREZ, ADRIANA JOSEFINA aus {team: AP-PIS} {congressman name: TUDELA GUTIÉRREZ, ADRIANA JOSEFINA} {vote result: aus}; BM TELLO MONTES, NIVARDO EDGAR SI +++ {team: BM} {congressman name: TELLO MONTES, NIVARDO EDGAR} {vote result: SI +++}. focused in these section (with the example structure), give me the results like: [APP, ACUÑA PERALTA, MARÍA GRIMANEZA, SI], [PP, CALLE LOBATÓN, DIGNA, LP], etc.",
        betas=["files-api-2025-04-14"],
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    )
    
    return message

# Configuration - Change this to analyze different files
file_to_analyze = "prueba3.pdf"
#file_to_analyze = "congres_vote_image2.png"

try:
    # Analyze the file
    message = analyze_file(file_to_analyze)
    
    # Extract readable content and save to file
    output_content = ""
    for content_block in message.content:
        if content_block.type == 'text':
            output_content += content_block.text
            #print(content_block.text)
            #print("\n" + "="*50 + "\n")
    
    # Save results to file
    output_file = "resultado_votes.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"✅ Results saved to: {output_file}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure:")
    print("1. The file exists in the current directory")
    print("2. Your .env file contains ANTHROPIC_API_KEY")
    print("3. The file is a supported format (PDF, JPG, PNG, etc.)")

