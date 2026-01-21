import anthropic
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def summarize_pdf(pdf_path, api_key, page_number=None, custom_prompt=None):
    """Summarize PDF using Claude API with direct PDF processing"""
    # Initialize Claude
    client = anthropic.Anthropic(api_key=api_key)
    
    # Read PDF as binary and encode to base64
    with open(pdf_path, "rb") as pdf_file:
        pdf_data = base64.standard_b64encode(pdf_file.read()).decode("utf-8")
    
    # Create prompt based on whether a specific page is requested
    if page_number:
        if custom_prompt:
            # Use custom prompt but prepend page specification
            prompt_text = f"Analiza ÚNICAMENTE la página {page_number} de este documento PDF.\n\n{custom_prompt}"
        else:
            # Use default detailed prompt
            prompt_text = f"""Analiza ÚNICAMENTE la página {page_number} de este documento PDF y proporciona un análisis DETALLADO:

1. **Texto exacto del encabezado/título**: Transcribe literalmente el título o encabezado principal de esta página
2. **Contenido específico**: Resume el contenido de esta página
3. **Datos numéricos**: Lista TODOS los números, porcentajes, fechas o estadísticas que aparezcan
4. **Nombres propios**: Lista TODOS los nombres de personas, lugares o instituciones mencionados
5. **Tablas o listas**: Si hay tablas, transcribe sus datos. Si hay listas, enuméralas completamente
6. **Resultados de votación (si aplica)**: 
   - Votos a favor
   - Votos en contra
   - Abstenciones
   - Ausentes
   - Nombres de votantes y su voto

Sé MUY específico y detallado. Quiero verificar que realmente estás leyendo esta página exacta."""
    else:
        prompt_text = """Please provide a one-sentence summary for each page of this PDF document. 

Format your response as:

**Page 1:** [summary]
**Page 2:** [summary]
...

Keep each summary concise and focus on the main topic or action of that page."""
    
    # Create prompt with PDF document
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,  # Increased for longer documents
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt_text
                    }
                ],
            }
        ],
    )
    
    return message.content[0].text

# Run it
if __name__ == "__main__":
    import sys
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    print("="*80)
    print("PDF ANALYZER CON CLAUDE")
    print("="*80 + "\n")
    
    # Ask for PDF name
    pdf_path = input("Ingresa el nombre del archivo PDF (ej: documento.pdf): ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"Error: Archivo no encontrado: {pdf_path}")
        sys.exit(1)
    
    # Ask for page number(s)
    page_input = input("\nIngresa número de página (deja vacío para resumir todo el PDF): ").strip()
    page_number = int(page_input) if page_input else None
    
    # Ask for prompt type
    if page_number:
        print("\nOpciones de análisis:")
        print("1. Usar prompt de resumen detallado (por defecto)")
        print("2. Ingresar mi propio prompt")
        
        prompt_choice = input("\nElige opción (1 o 2): ").strip()
        
        if prompt_choice == "2":
            custom_prompt = input("\nIngresa tu prompt personalizado: ").strip()
            if custom_prompt:
                # Modify the function to accept custom prompt
                print(f"\nAnalizando página {page_number} con tu prompt personalizado...")
        else:
            custom_prompt = None
            print(f"\nAnalizando página {page_number} con prompt detallado...")
    else:
        custom_prompt = None
        print(f"\nResumiendo todas las páginas de {pdf_path}...")
    
    print("(Claude procesará el PDF incluyendo OCR si es necesario...)\n")
    
    # Call function with custom prompt if provided
    if custom_prompt and page_number:
        # We need to modify summarize_pdf to accept custom prompt
        result = summarize_pdf(pdf_path, api_key, page_number, custom_prompt)
    else:
        result = summarize_pdf(pdf_path, api_key, page_number)
    
    print("\n" + "="*80)
    if page_number:
        print(f"ANÁLISIS - PÁGINA {page_number}")
    else:
        print("RESÚMENES POR PÁGINA")
    print("="*80 + "\n")
    print(result)