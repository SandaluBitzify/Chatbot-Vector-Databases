import fitz  # PyMuPDF
import pdfplumber
import tabula
import camelot
from pdfminer.high_level import extract_text as pdfminer_extract
from pdfminer.layout import LAParams
import PyPDF2
import pandas as pd
import re
import io
from typing import List, Dict, Tuple, Any

class ComprehensivePDFExtractor:
    """
    Comprehensive PDF extractor that uses multiple libraries to ensure no data is missed.
    """
    
    def __init__(self):
        self.extracted_data = {
            'text_content': '',
            'tables': [],
            'metadata': {},
            'total_records': 0,
            'extraction_methods': []
        }
    
    def extract_all_data(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        Extract all possible data from PDF using multiple methods.
        """
        print(f"📄 Starting comprehensive PDF extraction from: {pdf_path}")
        
        # Method 1: PyMuPDF (fitz) - Good for general text and layout
        self._extract_with_pymupdf(pdf_path)
        
        # Method 2: pdfplumber - Excellent for tables and structured data
        self._extract_with_pdfplumber(pdf_path)
        
        # Method 3: tabula - Specialized for tables
        self._extract_tables_with_tabula(pdf_path)
        
        # Method 4: camelot - Another table extraction specialist
        self._extract_tables_with_camelot(pdf_path)
        
        # Method 5: pdfminer - Good for complex layouts
        self._extract_with_pdfminer(pdf_path)
        
        # Method 6: PyPDF2 - Fallback method
        self._extract_with_pypdf2(pdf_path)
        
        # Combine and clean all extracted data
        combined_text = self._combine_and_clean_data()
        
        # Count records
        self.extracted_data['total_records'] = self._count_records(combined_text)
        
        # Create metadata
        metadata = {
            'total_records': self.extracted_data['total_records'],
            'extraction_methods': self.extracted_data['extraction_methods'],
            'tables_found': len(self.extracted_data['tables']),
            'text_length': len(combined_text)
        }
        
        print(f"📄 PDF extraction complete: {metadata['total_records']} records found using {len(metadata['extraction_methods'])} methods")
        
        return combined_text, metadata
    
    def _extract_with_pymupdf(self, pdf_path: str):
        """Extract using PyMuPDF (fitz) - good for general text and images."""
        try:
            print("📄 Extracting with PyMuPDF...")
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"\n--- Page {page_num + 1} (PyMuPDF) ---\n{text}")
                
                # Extract text with layout information
                text_dict = page.get_text("dict")
                structured_text = self._parse_pymupdf_dict(text_dict, page_num + 1)
                if structured_text:
                    text_parts.append(structured_text)
                
                # Extract tables if any
                tables = page.find_tables()
                for table_num, table in enumerate(tables):
                    try:
                        table_data = table.extract()
                        if table_data:
                            table_text = self._format_table_data(table_data, f"Page {page_num + 1} Table {table_num + 1}")
                            text_parts.append(table_text)
                            self.extracted_data['tables'].append({
                                'source': 'PyMuPDF',
                                'page': page_num + 1,
                                'data': table_data
                            })
                    except Exception as e:
                        print(f"⚠️ Error extracting table from page {page_num + 1}: {e}")
            
            doc.close()
            
            if text_parts:
                self.extracted_data['text_content'] += "\n\n".join(text_parts)
                self.extracted_data['extraction_methods'].append('PyMuPDF')
                print(f"✅ PyMuPDF extracted {len(text_parts)} text sections")
            
        except Exception as e:
            print(f"❌ PyMuPDF extraction failed: {e}")
    
    def _extract_with_pdfplumber(self, pdf_path: str):
        """Extract using pdfplumber - excellent for tables and structured data."""
        try:
            print("📄 Extracting with pdfplumber...")
            text_parts = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"\n--- Page {page_num + 1} (pdfplumber) ---\n{text}")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table:
                            table_text = self._format_table_data(table, f"Page {page_num + 1} Table {table_num + 1}")
                            text_parts.append(table_text)
                            self.extracted_data['tables'].append({
                                'source': 'pdfplumber',
                                'page': page_num + 1,
                                'data': table
                            })
                    
                    # Extract text with coordinates for better structure
                    words = page.extract_words()
                    if words:
                        structured_text = self._parse_pdfplumber_words(words, page_num + 1)
                        if structured_text:
                            text_parts.append(structured_text)
            
            if text_parts:
                self.extracted_data['text_content'] += "\n\n" + "\n\n".join(text_parts)
                self.extracted_data['extraction_methods'].append('pdfplumber')
                print(f"✅ pdfplumber extracted {len(text_parts)} sections")
            
        except Exception as e:
            print(f"❌ pdfplumber extraction failed: {e}")
    
    def _extract_tables_with_tabula(self, pdf_path: str):
        """Extract tables using tabula-py."""
        try:
            print("📄 Extracting tables with tabula...")
            
            # Extract all tables from all pages
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, pandas_options={'header': None})
            
            text_parts = []
            for table_num, df in enumerate(tables):
                if not df.empty:
                    table_text = f"\n--- Tabula Table {table_num + 1} ---\n"
                    table_text += df.to_string(index=False, na_rep='')
                    text_parts.append(table_text)
                    
                    self.extracted_data['tables'].append({
                        'source': 'tabula',
                        'table_num': table_num + 1,
                        'data': df.values.tolist()
                    })
            
            if text_parts:
                self.extracted_data['text_content'] += "\n\n" + "\n\n".join(text_parts)
                self.extracted_data['extraction_methods'].append('tabula')
                print(f"✅ tabula extracted {len(tables)} tables")
            
        except Exception as e:
            print(f"❌ tabula extraction failed: {e}")
    
    def _extract_tables_with_camelot(self, pdf_path: str):
        """Extract tables using camelot."""
        try:
            print("📄 Extracting tables with camelot...")
            
            # Extract tables using both lattice and stream methods
            text_parts = []
            
            # Method 1: Lattice (for tables with clear borders)
            try:
                tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
                for table_num, table in enumerate(tables_lattice):
                    if not table.df.empty:
                        table_text = f"\n--- Camelot Lattice Table {table_num + 1} (Page {table.page}) ---\n"
                        table_text += table.df.to_string(index=False, na_rep='')
                        text_parts.append(table_text)
                        
                        self.extracted_data['tables'].append({
                            'source': 'camelot_lattice',
                            'page': table.page,
                            'accuracy': table.accuracy,
                            'data': table.df.values.tolist()
                        })
                
                print(f"✅ camelot lattice extracted {len(tables_lattice)} tables")
            except Exception as e:
                print(f"⚠️ camelot lattice failed: {e}")
            
            # Method 2: Stream (for tables without clear borders)
            try:
                tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
                for table_num, table in enumerate(tables_stream):
                    if not table.df.empty:
                        table_text = f"\n--- Camelot Stream Table {table_num + 1} (Page {table.page}) ---\n"
                        table_text += table.df.to_string(index=False, na_rep='')
                        text_parts.append(table_text)
                        
                        self.extracted_data['tables'].append({
                            'source': 'camelot_stream',
                            'page': table.page,
                            'accuracy': table.accuracy,
                            'data': table.df.values.tolist()
                        })
                
                print(f"✅ camelot stream extracted {len(tables_stream)} tables")
            except Exception as e:
                print(f"⚠️ camelot stream failed: {e}")
            
            if text_parts:
                self.extracted_data['text_content'] += "\n\n" + "\n\n".join(text_parts)
                self.extracted_data['extraction_methods'].append('camelot')
            
        except Exception as e:
            print(f"❌ camelot extraction failed: {e}")
    
    def _extract_with_pdfminer(self, pdf_path: str):
        """Extract using pdfminer - good for complex layouts."""
        try:
            print("📄 Extracting with pdfminer...")
            
            # Configure layout analysis parameters
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5,
                all_texts=False
            )
            
            text = pdfminer_extract(pdf_path, laparams=laparams)
            
            if text and text.strip():
                formatted_text = f"\n--- pdfminer extraction ---\n{text}"
                self.extracted_data['text_content'] += "\n\n" + formatted_text
                self.extracted_data['extraction_methods'].append('pdfminer')
                print(f"✅ pdfminer extracted {len(text)} characters")
            
        except Exception as e:
            print(f"❌ pdfminer extraction failed: {e}")
    
    def _extract_with_pypdf2(self, pdf_path: str):
        """Extract using PyPDF2 - fallback method."""
        try:
            print("📄 Extracting with PyPDF2...")
            text_parts = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"\n--- Page {page_num + 1} (PyPDF2) ---\n{text}")
            
            if text_parts:
                self.extracted_data['text_content'] += "\n\n" + "\n\n".join(text_parts)
                self.extracted_data['extraction_methods'].append('PyPDF2')
                print(f"✅ PyPDF2 extracted {len(text_parts)} pages")
            
        except Exception as e:
            print(f"❌ PyPDF2 extraction failed: {e}")
    
    def _parse_pymupdf_dict(self, text_dict: Dict, page_num: int) -> str:
        """Parse PyMuPDF text dictionary for structured data."""
        try:
            structured_parts = []
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    block_text = []
                    for line in block["lines"]:
                        line_text = []
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                line_text.append(text)
                        if line_text:
                            block_text.append(" ".join(line_text))
                    
                    if block_text:
                        structured_parts.append("\n".join(block_text))
            
            if structured_parts:
                return f"\n--- Page {page_num} Structured (PyMuPDF) ---\n" + "\n\n".join(structured_parts)
            
        except Exception as e:
            print(f"⚠️ Error parsing PyMuPDF dict: {e}")
        
        return ""
    
    def _parse_pdfplumber_words(self, words: List[Dict], page_num: int) -> str:
        """Parse pdfplumber words for better structure."""
        try:
            if not words:
                return ""
            
            # Group words by approximate line (y-coordinate)
            lines = {}
            for word in words:
                y = round(word['top'], 1)  # Round to group nearby words
                if y not in lines:
                    lines[y] = []
                lines[y].append((word['x0'], word['text']))
            
            # Sort lines by y-coordinate (top to bottom)
            sorted_lines = []
            for y in sorted(lines.keys()):
                # Sort words in each line by x-coordinate (left to right)
                line_words = sorted(lines[y], key=lambda x: x[0])
                line_text = " ".join([word[1] for word in line_words])
                if line_text.strip():
                    sorted_lines.append(line_text.strip())
            
            if sorted_lines:
                return f"\n--- Page {page_num} Structured (pdfplumber) ---\n" + "\n".join(sorted_lines)
            
        except Exception as e:
            print(f"⚠️ Error parsing pdfplumber words: {e}")
        
        return ""
    
    def _format_table_data(self, table_data: List[List], title: str) -> str:
        """Format table data into readable text."""
        if not table_data:
            return ""
        
        formatted_lines = [f"\n--- {title} ---"]
        
        for row_num, row in enumerate(table_data):
            if row and any(cell for cell in row if cell and str(cell).strip()):
                # Clean and format each cell
                cleaned_row = []
                for cell in row:
                    if cell is not None:
                        cell_str = str(cell).strip()
                        if cell_str:
                            cleaned_row.append(cell_str)
                        else:
                            cleaned_row.append("")
                    else:
                        cleaned_row.append("")
                
                if any(cell for cell in cleaned_row):
                    formatted_lines.append(f"Row {row_num + 1}: {' | '.join(cleaned_row)}")
        
        return "\n".join(formatted_lines)
    
    def _combine_and_clean_data(self) -> str:
        """Combine and clean all extracted data."""
        print("📄 Combining and cleaning extracted data...")
        
        # Start with basic text content
        combined_text = self.extracted_data['text_content']
        
        # Add summary of extraction methods
        if self.extracted_data['extraction_methods']:
            summary = f"\nPDF EXTRACTION SUMMARY:\n"
            summary += f"Extraction methods used: {', '.join(self.extracted_data['extraction_methods'])}\n"
            summary += f"Tables found: {len(self.extracted_data['tables'])}\n"
            summary += f"Total text length: {len(combined_text)} characters\n\n"
            combined_text = summary + combined_text
        
        # Clean up the text
        combined_text = self._clean_extracted_text(combined_text)
        
        return combined_text
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve structure
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        
        # Remove common PDF artifacts
        text = re.sub(r'\x0c', '\n', text)  # Form feed to newline
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)  # Control characters
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('–', '-')
        text = text.replace('—', '-')
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        
        return text.strip()
    
    def _count_records(self, text: str) -> int:
        """Count the number of data records in the extracted text."""
        if not text:
            return 0
        
        # Count different types of potential records
        record_indicators = [
            r'Row \d+:',  # Table rows
            r'Record \d+:',  # Explicit records
            r'^\d+\.',  # Numbered items
            r'^\d+\)',  # Numbered items with parentheses
            r'^\d+\s+[A-Za-z]',  # Number followed by text
            r'[A-Z][a-z]+\s+\d+',  # Name followed by number
            r'\d{4}-\d{2}-\d{2}',  # Dates
            r'\$\d+',  # Currency amounts
        ]
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        record_count = 0
        
        for line in lines:
            # Skip headers and metadata lines
            if any(skip in line.lower() for skip in ['page', '---', 'extraction', 'summary', 'table', 'method']):
                continue
            
            # Check if line matches any record pattern
            if any(re.search(pattern, line) for pattern in record_indicators):
                record_count += 1
            # Also count lines that look like data (have both text and numbers)
            elif re.search(r'[A-Za-z]', line) and re.search(r'\d', line) and len(line) > 10:
                record_count += 1
        
        # Also count table records
        table_records = sum(len(table['data']) for table in self.extracted_data['tables'] if table['data'])
        
        # Return the higher count (text-based or table-based)
        final_count = max(record_count, table_records)
        
        print(f"📊 Record counting: {record_count} from text, {table_records} from tables, final: {final_count}")
        
        return final_count

# Main extraction function
def extract_from_pdf_comprehensive(pdf_path: str) -> Tuple[str, Dict]:
    """
    Comprehensive PDF extraction using multiple methods.
    """
    extractor = ComprehensivePDFExtractor()
    return extractor.extract_all_data(pdf_path)
