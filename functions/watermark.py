import boto3
import pikepdf
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from pdf2image import convert_from_path
from tempfile import NamedTemporaryFile

# AWS S3 Configuration
s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='ap-southeast-1')

def create_repeating_rotated_text_watermark(watermark_text, width, height, angle=45):
    """Create a rotated watermark from text using ReportLab and repeat it."""
    watermark_stream = io.BytesIO()
    c = canvas.Canvas(watermark_stream, pagesize=(width, height))
    
    c.setFillAlpha(0.3)  # Set transparency for the watermark
    c.setFont("Helvetica", 40)

    # Define starting position and spacing
    spacing = 200  # Distance between repeated watermarks
    x_positions = range(0, int(width), spacing)
    y_positions = range(0, int(height), spacing)

    for x in x_positions:
        for y in y_positions:
            c.saveState()
            c.translate(x, y)  # Move to position (x, y)
            c.rotate(angle)     # Rotate the text
            c.drawCentredString(0, 0, watermark_text)  # Draw the text at the new origin
            c.restoreState()

    c.save()
    watermark_stream.seek(0)
    
    return watermark_stream

def flatten_pdf_with_images(pdf_stream):
    """Flatten a PDF by converting it to images and saving it back as a PDF."""
    # Create a temporary file for the PDF
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        temp_pdf_file.write(pdf_stream.read())
        temp_pdf_path = temp_pdf_file.name
    
    # Convert PDF to images using the temp file path
    try:
        images = convert_from_path(temp_pdf_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None
    
    # Remove the temporary PDF file after conversion
    os.remove(temp_pdf_path)
    
    # Save the images as a new PDF
    output_pdf_stream = io.BytesIO()
    images[0].save(output_pdf_stream, save_all=True, append_images=images[1:])
    
    output_pdf_stream.seek(0)
    return output_pdf_stream
    
def add_watermark_to_pdf(pdf_file, watermark_stream):
    """Add a watermark to each page of the PDF."""
    original_pdf = PdfReader(pdf_file)
    watermark_pdf = PdfReader(watermark_stream)
    
    pdf_writer = PdfWriter()
    watermark_page = watermark_pdf.pages[0]
    
    for page_number in range(len(original_pdf.pages)):
        page = original_pdf.pages[page_number]
        page.merge_page(watermark_page)  # Merge the watermark onto the page
        pdf_writer.add_page(page)
    
    output_stream = io.BytesIO()
    pdf_writer.write(output_stream)
    output_stream.seek(0)
    
    # Flatten the watermarked PDF using image conversion
    flattened_pdf = flatten_pdf_with_images(output_stream)
    
    return flattened_pdf

def download_file_from_s3(bucket_name, s3_file_key):
    """Download file from S3."""
    s3_object = s3.get_object(Bucket=bucket_name, Key=s3_file_key)
    return io.BytesIO(s3_object['Body'].read())

def upload_file_to_s3(bucket_name, s3_file_key, file_stream):
    """Upload file to S3."""
    s3.put_object(Bucket=bucket_name, Key=s3_file_key, Body=file_stream)

def process_pdf_with_repeating_text_watermark(bucket_name, input_pdf_key, output_pdf_key, watermark_text):
    """Process the PDF by adding a repeating text watermark."""
    # Download the original PDF from S3
    original_pdf_stream = download_file_from_s3(bucket_name, input_pdf_key)
    
    # Create a watermark from text with the dimensions of the PDF page
    watermark_stream = create_repeating_rotated_text_watermark(watermark_text, letter[0], letter[1])
    
    # Add the watermark to the original PDF
    watermarked_pdf_stream = add_watermark_to_pdf(original_pdf_stream, watermark_stream)
    
    # Upload the watermarked PDF back to S3
    upload_file_to_s3(bucket_name, output_pdf_key, watermarked_pdf_stream)
