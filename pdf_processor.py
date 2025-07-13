import PyPDF2
import os
from io import BytesIO

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_pages(self, input_pdf_path, start_page, end_page, output_path=None):
        """
        Extract pages from a PDF file.
        
        Args:
            input_pdf_path (str): Path to the input PDF file
            start_page (int): Starting page number (1-indexed)
            end_page (int): Ending page number (1-indexed)
            output_path (str, optional): Path for the output PDF file
            
        Returns:
            str: Path to the extracted PDF file or BytesIO object
        """
        try:
            # Open the input PDF file
            with open(input_pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                # Validate page numbers
                total_pages = len(reader.pages)
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    raise ValueError(f"Invalid page range. PDF has {total_pages} pages. "
                                   f"Requested range: {start_page}-{end_page}")
                
                # Extract pages (convert to 0-indexed)
                for page_num in range(start_page - 1, end_page):
                    page = reader.pages[page_num]
                    writer.add_page(page)
                
                # If output_path is provided, save to file
                if output_path:
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    return output_path
                else:
                    # Return BytesIO object for direct download
                    output_buffer = BytesIO()
                    writer.write(output_buffer)
                    output_buffer.seek(0)
                    return output_buffer
                    
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def get_page_count(self, pdf_path):
        """
        Get the total number of pages in a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            int: Total number of pages
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def validate_pdf(self, pdf_path):
        """
        Validate if the file is a valid PDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                # Try to access the first page
                if len(reader.pages) > 0:
                    return True
                return False
        except:
            return False 