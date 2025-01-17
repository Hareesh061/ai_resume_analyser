
import pdfplumber
import openai

#OpenAI API key
openai.api_key = 'ADD-your-api-key-here'

def parse_resume(file_path):
    try:
        # Extracting text
        with pdfplumber.open(file_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)

        if not text.strip():
            raise ValueError("No text found in the PDF file.")
        
        prompt = f"""
        Extract the following fields from the resume text:
        - Name
        - Contact details
        - University
        - Year of Study
        - Course
        - Discipline
        - CGPA/Percentage
        - Key Skills
        - Gen AI Experience Score (1-3)
        - AI/ML Experience Score (1-3)
        - Supporting Information (certifications, internships, projects)

        Resume Text: {text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts information from resumes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        extracted_data = response['choices'][0]['message']['content'].strip()
        return parse_response_to_dict(extracted_data)
    
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return None

def parse_response_to_dict(response_text):
    try:
        
        lines = response_text.split("\n")
        data = {}
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                data[key.strip()] = value.strip()
        return data
    except Exception as e:
        print(f"Error parsing response: {e}")
        return {}


if __name__ == "__main__":
    file_path = "Hareesh_Naik_Resume.pdf"  
    extracted_data = parse_resume(file_path)
    if extracted_data:
        print("Extracted Resume Data:")
        for key, value in extracted_data.items():
            print(f"{key}: {value}")
