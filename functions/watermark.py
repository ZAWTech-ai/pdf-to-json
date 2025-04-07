import boto3
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from pdf2image import convert_from_path
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")

# AWS S3 Configuration
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

def create_repeating_rotated_text_watermark(watermark_text, width, height, angle=45):
    """Create a rotated watermark from text using ReportLab and repeat it."""
    watermark_stream = io.BytesIO()
    c = canvas.Canvas(watermark_stream, pagesize=(width, height))
    
    c.setFillAlpha(0.1)  # Set transparency for the watermark
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
    """Flatten a PDF by converting each page to images and recombining them into a single PDF."""
    
    # Create a temporary file to hold the PDF data
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        # Write the BytesIO stream to the temporary file
        temp_pdf_file.write(pdf_stream.read())
        temp_pdf_path = temp_pdf_file.name  # Get the temp file path
    
    try:
        # Convert the PDF to images using the temp file path
        images = convert_from_path(temp_pdf_path)

        # Prepare an output stream to save the flattened PDF
        output_pdf_stream = io.BytesIO()

        # Convert the images back to a PDF
        images[0].save(output_pdf_stream, save_all=True, append_images=images[1:], format="PDF")
        output_pdf_stream.seek(0)  # Rewind the stream to the beginning
        
        # Return the flattened PDF stream
        return output_pdf_stream

    finally:
        # Clean up: Remove the temporary file after conversion
        os.remove(temp_pdf_path)
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

def process_pdf_with_repeating_text_watermark(input_pdf_key, output_pdf_key, watermark_text):
    """Process the PDF by adding a repeating text watermark."""
    bucket_name = aws_bucket_name
    # Download the original PDF from S3
    original_pdf_stream = download_file_from_s3(bucket_name, input_pdf_key)
    
    # Create a watermark from text with the dimensions of the PDF page
    watermark_stream = create_repeating_rotated_text_watermark(watermark_text, letter[0], letter[1])
    
    # Add the watermark to the original PDF
    watermarked_pdf_stream = add_watermark_to_pdf(original_pdf_stream, watermark_stream)
    
    # Upload the watermarked PDF back to S3
    upload_file_to_s3(bucket_name, output_pdf_key, watermarked_pdf_stream)
