import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import requests


def format_text(text):
    return text  # Return plain text without Markdown formatting

def find_line(text, query):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if query.lower() in line.lower():
            return index + 1  # Return line number (1-indexed)
    return None

def text_to_pdf(text, background_color):
    pdf = FPDF()
    pdf.add_page()
    
    # Set background color
    try:
        r, g, b = int(background_color[1:3], 16), int(background_color[3:5], 16), int(background_color[5:7], 16)
    except ValueError:
        st.error("Invalid color format. Please use a hex code (e.g., #FF5733).")
        return None
    
    pdf.set_fill_color(r, g, b)  
    pdf.rect(0, 0, 210, 297, 'F')  # Fill the background

    # Set default font since no customization is needed
    pdf.set_font('Arial', size=12)

    # Split the text into lines and add them to the PDF
    for line in text.splitlines():
        pdf.cell(0, 10, line, ln=True)
    
    # Save the PDF to a BytesIO object
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

# Function to send feedback using emailjs
def send_feedback_email(feedback):
    service_id = 'service_nad8kld'  # Your EmailJS service ID
    template_id = 'template_snk0jx8'  # Your EmailJS template ID
    user_id = 'MOXRLVXq1C0FiX6fe'  # Your EmailJS user ID (public key)

    # Create the data payload for emailjs API
    data = {
        'service_id': service_id,
        'template_id': template_id,
        'user_id': user_id,
        'template_params': {
            'user_email': user_id,
            'message': feedback
        }
    }

    # Send the POST request to emailjs
    response = requests.post('https://api.emailjs.com/api/v1.0/email/send', json=data)

    if response.status_code == 200:
        st.success("Thank you for your feedback! It has been sent.")
    else:
        st.error(f"Error sending feedback: {response.status_code} - {response.text}")  # Include response text for debugging

def main():
    st.title("PDF Summarizer and Text to PDF Converter")

    # Section for uploading PDF file
    st.subheader("Upload PDF for Summarization")
    uploaded_file = st.file_uploader("Drag and drop a PDF file here", type="pdf", label_visibility="collapsed")
    
    if uploaded_file is not None:
        # Read the PDF file
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None case for empty pages

        # Display the extracted text
        st.subheader("Extracted Text")
        st.text_area("Extracted Text", text, height=300, disabled=True)  # Read-only text area for extracted text

        # User input for Q&A
        user_input = st.text_input("Ask a question about the document:")
        
        if st.button("Submit Question"):
            if user_input:
                line_number = find_line(text, user_input)
                if line_number:
                    response = f"The answer is written on line **{line_number}**."
                else:
                    response = "Sorry, the document does not contain information regarding that."
                
                st.write(response)
            else:
                st.error("Please enter a question.")
    
    # Section for writing text to create PDF
    st.subheader("Create a PDF from Text")
    input_text = st.text_area("Enter text to create a PDF:", height=150)
    
    # Input for PDF customization
    background_color = st.color_picker("Choose Background Color:", "#FFFFFF")
    
    if st.button("Generate PDF"):
        if input_text:
            pdf_output = text_to_pdf(input_text, background_color)
            if pdf_output:
                st.success("PDF has been generated! Click the button below to download.")
                st.download_button(
                    label="Download Generated PDF",
                    data=pdf_output,
                    file_name="generated_text.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("Please enter some text to create a PDF.")
    
    # Feedback Section
    st.subheader("Provide Feedback")
    st.write("This is a prototype. We value your feedback to improve the tool!")
    
    feedback = st.text_area("Please provide your feedback here:", height=100)
    
    if st.button("Submit Feedback"):
        if feedback:
            send_feedback_email(feedback)
        else:
            st.error("Please write some feedback before submitting.")

# Set a custom background for Streamlit app
st.markdown(
    """
    <style>
    .stApp {
        color: white;  /* White text */
    }
    </style>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()
