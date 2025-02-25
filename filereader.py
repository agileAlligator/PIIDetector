import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import subprocess
from tess import wrapper
import cv2
import numpy as np
import fitz
# Set this globally for ALL calls through this module
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class FileReader:
    @staticmethod
    def extract_text(file_path: str, mime_type: str) -> str:
        """Extract text based on file type (returns empty string if unsupported)."""
        try:
            if mime_type.startswith("text/"):
                return FileReader._read_text(file_path)
            elif mime_type == "application/pdf":
                return FileReader._extract_from_pdf(file_path)
            elif mime_type.startswith("application/vnd.openxmlformats-officedocument"):
                return FileReader._extract_from_docx(file_path)
            elif mime_type == "application/msword":
                return FileReader._extract_from_legacy_doc(file_path)
            elif mime_type.startswith("image/"):
                imagefile=cv2.imread(file_path)
                return FileReader._ocr_image(imagefile)
            else:
                return ""
        except Exception as e:
            print(f"[ERROR] Failed to extract from {file_path}: {e}")
            return ""

    @staticmethod
    def _read_text(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extracts text from a PDF using pdfplumber and OCR for image-heavy pages."""
        full_text = ""

        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # Extract text using pdfplumber
                text = page.extract_text()

                # If text is found AND no images, use pdfplumber text only
                if text and not page.images:
                    full_text += text + "\n"
                else:
                    print(f"[INFO] Page {page_number} contains images or no text, performing OCR...")
                    full_text += FileReader._ocr_pdf_page(file_path, page_number)
        return full_text.strip()

    @staticmethod
    def _ocr_pdf_page(file_path: str, page_number: int) -> str:
        """Extracts the entire page as an image and runs OCR."""
        extracted_text = ""

        # Open the PDF using PyMuPDF
        pdf_document = fitz.open(file_path)
        page = pdf_document[page_number - 1]  # PyMuPDF is 0-indexed, pdfplumber is 1-indexed

        # Convert the entire page to an image
        pix = page.get_pixmap(dpi=300)  # Render at 300 DPI for better OCR accuracy
        image_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

        # Perform OCR on the entire page
        ocr_text = FileReader._ocr_image(image_cv)
        extracted_text += ocr_text + "\n"

        print(f"[INFO] OCR completed for full page {page_number}.")

        pdf_document.close()
        return extracted_text.strip()

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)

    @staticmethod
    def _extract_from_legacy_doc(file_path: str) -> str:
        result = subprocess.run(["catdoc", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode("utf-8", errors='ignore')

    @staticmethod
    def _ocr_image(imagefile):
        image=imagefile
        image,flag=wrapper(image)
        if flag==0:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Perform OCR
        text = pytesseract.image_to_string(image)
        return text.strip()

    @staticmethod
    def extract_from_scanned_pdf(file_path: str) -> str:
        images = convert_from_path(file_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text
