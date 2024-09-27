import boto3
import pikepdf
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

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
    """Create a watermark from text using ReportLab and repeat it."""
    # Create an in-memory stream for the watermark PDF
    watermark_stream = io.BytesIO()
    c = canvas.Canvas(watermark_stream, pagesize=(width, height))
    
    # Set transparency for watermark (optional)
    c.setFillAlpha(0.3)
    
    # Set font and size
    c.setFont("Helvetica", 40)
    
    # Repeat the watermark across the page
    x, y = 100, 400  # Starting position
    spacing = 300    # Space between repeated watermarks
    for i in range(5):  # Adjust the range for more/less repetition
        for j in range(5):  # Adjust for more rows
            c.translate(300,500)
            c.rotate(45)
            c.drawString(x + i * spacing, y - j * 100, watermark_text)
    
    # Finish the PDF and save the stream
    c.save()
    watermark_stream.seek(0)
    
    return watermark_stream

def flatten_pdf(pdf_stream):
    """Flatten a PDF to make annotations, forms, and watermarks uneditable."""
    output_pdf = io.BytesIO()
    
    # Open the PDF with pikepdf and save it as a flattened version
    with pikepdf.open(pdf_stream) as pdf:
        for page in pdf.pages:
            if page.get("/Annots") is not None:
                page.flatten_annotations()  # Flatten annotations if they exist
        pdf.save(output_pdf)
    
    output_pdf.seek(0)
    return output_pdf
    
def add_watermark_to_pdf(pdf_file, watermark_stream):
    """Add a watermark to each page of the PDF."""
    original_pdf = PdfReader(pdf_file)
    watermark_pdf = PdfReader(watermark_stream)
    
    pdf_writer = PdfWriter()
    watermark_page = watermark_pdf.pages[0]
    
    for page_number in range(len(original_pdf.pages)):
        page = original_pdf.pages[page_number]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)
    
    output_stream = io.BytesIO()
    pdf_writer.write(output_stream)
    output_stream.seek(0)
    
    # Flatten the watermarked PDF
    flattened_pdf = flatten_pdf(output_stream)
    
    return flattened_pdf
def download_file_from_s3(bucket_name, s3_file_key):
    """Download file from S3."""
    s3_object = s3.get_object(Bucket=bucket_name, Key=s3_file_key)
    return io.BytesIO(s3_object['Body'].read())

def upload_file_to_s3(bucket_name, s3_file_key, file_stream):
    """Upload file to S3."""
    s3.put_object(Bucket=bucket_name, Key=s3_file_key, Body=file_stream)

def process_pdf_with_repeating_text_watermark(bucket_name, input_pdf_key, output_pdf_key, watermark_text):
    # Download the original PDF from S3
    original_pdf_stream = download_file_from_s3(bucket_name, input_pdf_key)
    
    # Create a watermark from text with the dimensions of the PDF page
    watermark_stream = create_repeating_rotated_text_watermark(watermark_text, letter[0], letter[1])
    
    # Add the watermark to the original PDF
    watermarked_pdf_stream = add_watermark_to_pdf(original_pdf_stream, watermark_stream)
    
    # Upload the watermarked PDF back to S3
    upload_file_to_s3('edhubshop', output_pdf_key, watermarked_pdf_stream)

