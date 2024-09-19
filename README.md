
# Book Summarization Pipeline for English and Arabic

This project provides an end-to-end pipeline for summarizing books in both English and Arabic. The pipeline extracts text from a PDF, divides the text into semantically meaningful chunks, applies language-specific summarization models, and generates a PDF with the summarized content.

## Features

- **Text Extraction**: Extracts raw text from PDF files.
- **Language Detection**: Automatically detects if the text is in English or Arabic.
- **Semantic Chunking**: Divides text into semantically meaningful chunks.
  - English: Utilizes `Sentence-BERT` for semantic chunking.
  - Arabic: Uses `Stanza` to chunk Arabic text.
- **Text Summarization**:
  - English: Uses the BART model (`facebook/bart-large-cnn`).
  - Arabic: Uses the mT5 model (`csebuetnlp/mT5_multilingual_XLSum`).
- **PDF Generation**: Generates a final PDF output with the summarized text.

## Setup Instructions

### Step 1: Install Required Libraries

The following libraries are required to run the notebook:

```bash
pip install PyMuPDF pdfplumber transformers arabic_reshaper python-bidi matplotlib reportlab fpdf2
pip install spacy camel-tools sentence-transformers fpdf PyPDF2 stanza langdetect
```

### Step 2: Download the Arabic Language Model for Stanza

Before running the summarization pipeline for Arabic books, you need to download the Arabic language model for Stanza:

```python
import stanza
stanza.download('ar')
```

### Step 3: Clone the Repository and Update File Paths

Ensure you clone this repository to get the required resources, like the font files necessary for PDF generation:

```bash
git clone <repository-url>
cd <repository-folder>
```

You will need to make the following changes in the notebook:

1. **PDF File Path (`pdf_path`)**:
   - In the notebook, update the `pdf_path` variable to point to the PDF file you want to summarize.
   - Example: 
     ```python
     pdf_path = "/path/to/your/book.pdf"  # Update this to your file's location
     ```

2. **Font File Paths (`/path/to/DejaVuSans-Bold.ttf`, `/path/to/DejaVuSans.ttf`)**:
   - These are required for proper text rendering in the generated PDF. Replace the placeholders with the paths to the DejaVu Sans fonts, which are provided in this repository.
   - Example:
     ```python
     pdf.add_font('DejaVu', '', '/path/to/DejaVuSans.ttf', uni=True)
     pdf.add_font('DejaVu', 'B', '/path/to/DejaVuSans-Bold.ttf', uni=True)
     ```
   - Use the paths of the font files included in the repo:
     ```
     /path/to/repository/fonts/DejaVuSans-Bold.ttf
     /path/to/repository/fonts/DejaVuSans.ttf
     ```

## Notebook Overview

### Pipeline Steps

1. **Text Extraction**: 
   - Extracts text from the input PDF using `pdfplumber`.
   
2. **Language Detection**: 
   - Detects whether the input text is in English or Arabic using the `langdetect` library.
   
3. **Semantic Chunking**:
   - English: Uses the `Sentence-BERT` model to divide the text into semantically meaningful chunks.
   - Arabic: Uses `Stanza` to tokenize and chunk Arabic text into coherent blocks.

4. **Summarization**:
   - English: Summarized using the BART model (`facebook/bart-large-cnn`).
   - Arabic: Summarized using the mT5 model (`csebuetnlp/mT5_multilingual_XLSum`).

5. **PDF Generation**:
   - The summarized text is formatted and saved as a PDF using the `FPDF` library. Proper Arabic text direction and reshaping are handled for Arabic content.

### Functions Breakdown

- **`extract_text_from_pdf(pdf_path)`**: Extracts the raw text from the provided PDF file.
- **`divide_by_semantics_with_length(text)`**: Divides the English text into chunks based on semantic similarity.
- **`chunk_arabic_text(text)`**: Breaks Arabic text into chunks using Stanza.
- **`summarize_chunks(chunks, summarizer)`**: Summarizes each chunk using the appropriate model.
- **`generate_pdf(summary_text, pdf_output_path, language='en')`**: Generates a PDF from the summarized text.

### Running the Notebook

1. **PDF Path**: Update the `pdf_path` to the location of your book in the notebook.
2. **Fonts**: Update the font file paths (`DejaVuSans.ttf` and `DejaVuSans-Bold.ttf`) to their correct locations.
3. **Run**: Execute the notebook to extract text, detect the language, chunk the text, summarize it, and generate a PDF with the summarized content.

### Example

Here’s an example of how to run the summarization for a book:

```python
pdf_path = "/path/to/your/book.pdf"
final_summary = detect_language_and_summarize(pdf_path)
```

This will:
- Automatically detect the language.
- Run the appropriate summarization pipeline.
- Output a summarized version of the book as a PDF.

### Output

The final output will be a PDF file containing the summarized text of the input book. The output PDF will be saved as either `english_summary.pdf` or `arabic_summary.pdf` depending on the language detected.

---

## Files in the Repository

- **fonts/DejaVuSans-Bold.ttf**: Bold font file for PDF generation.
- **fonts/DejaVuSans.ttf**: Regular font file for PDF generation.
- **book-summarization-pipeline-for-english-and-arabic.ipynb**: The main notebook that contains the summarization pipeline.
- **sample-book.pdf**: A sample PDF book (optional) for testing the pipeline.

## Troubleshooting

- **GPU Usage**: Make sure your environment has access to a GPU for faster summarization, especially for large books.
- **Font Issues**: Ensure the font paths in the notebook are updated correctly, or you might encounter issues with text rendering in the generated PDFs.
  
