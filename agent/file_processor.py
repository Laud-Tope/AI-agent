# agent/file_processor.py - Handles reading different file types
import os
import json
import pandas as pd
from pathlib import Path
import PyPDF2
import docx
from typing import Dict, Any

class FileProcessor:
    """Handles reading and extracting content from various file types"""
    
    def __init__(self):
        self.supported_formats = {'.txt', '.pdf', '.docx', '.csv', '.json', '.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    def can_process(self, file_path: str) -> bool:
        """Check if we can process this file type"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content from a file and return structured data
        
        Returns:
            dict: Contains 'content', 'file_type', 'metadata'
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': extension,
            'size_bytes': file_path.stat().st_size,
            'content': '',
            'metadata': {}
        }
        
        try:
            if extension == '.txt':
                result['content'] = self._read_text_file(file_path)
            elif extension == '.pdf':
                result['content'] = self._read_pdf_file(file_path)
            elif extension == '.docx':
                result['content'] = self._read_docx_file(file_path)
            elif extension == '.csv':
                result['content'], result['metadata'] = self._read_csv_file(file_path)
            elif extension == '.json':
                result['content'] = self._read_json_file(file_path)
            elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                result['content'], result['metadata'] = self._read_image_file(file_path)
            
            print(f"✓ Processed {file_path.name} ({extension})")
            return result
            
        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _read_text_file(self, file_path: Path) -> str:
        """Read plain text files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _read_pdf_file(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        content = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content
    
    def _read_docx_file(self, file_path: Path) -> str:
        """Extract text from Word documents"""
        doc = docx.Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    
    def _read_csv_file(self, file_path: Path) -> tuple:
        """Read CSV files and return both content and structure info"""
        df = pd.read_csv(file_path)
        
        # Create a summary of the CSV
        content = f"CSV file with {len(df)} rows and {len(df.columns)} columns.\n"
        content += f"Columns: {', '.join(df.columns)}\n"
        content += f"First few rows:\n{df.head().to_string()}"
        
        metadata = {
            'rows': len(df),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict()
        }
        
        return content, metadata
    
    def _read_json_file(self, file_path: Path) -> str:
        """Read and summarize JSON files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to readable format
        return json.dumps(data, indent=2)
    
    def _read_image_file(self, file_path: Path) -> tuple:
        """Process image files and extract metadata"""
        try:
            from PIL import Image
            import os
            
            # Open image to get metadata
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
            file_size = os.path.getsize(file_path)
            
            content = f"Image file: {file_path.name}\n"
            content += f"Format: {format_name}\n"
            content += f"Dimensions: {width}x{height} pixels\n"
            content += f"Color mode: {mode}\n"
            content += f"File size: {file_size} bytes"
            
            metadata = {
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'file_size': file_size
            }
            
            return content, metadata
            
        except ImportError:
            # Fallback if PIL is not installed
            content = f"Image file: {file_path.name}\n"
            content += f"Format: {file_path.suffix.upper()}\n"
            content += "Basic image processing (install Pillow for advanced features)"
            
            metadata = {'basic_info': True}
            return content, metadata
        except Exception as e:
            content = f"Image file: {file_path.name} (Error reading metadata: {str(e)})"
            metadata = {'error': str(e)}
            return content, metadata