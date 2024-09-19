
# Book Summarization Pipeline for English and Arabic

## Overview

This project provides a complete pipeline for summarizing both **English** and **Arabic** books. It extracts text from a PDF, divides the text into semantically coherent chunks, summarizes each chunk, and generates a PDF output of the summary. The pipeline automatically detects the language of the book and applies the appropriate summarization model for each language. The summarization models are optimized for GPU use to handle large texts efficiently.

## Pipeline Breakdown

1. **Text Extraction**: Extracts text from the PDF using `PyMuPDF` and `pdfplumber`.
2. **Language Detection**: Uses `langdetect` to determine if the text is in English or Arabic.
3. **Semantic Chunking**:
   - For **English**: Utilizes `Sentence-BERT` embeddings to divide text into coherent chunks.
   - For **Arabic**: Uses `stanza` for natural language chunking.
4. **Text Summarization**:
   - **English**: Uses `facebook/bart-large-cnn` to summarize the text.
   - **Arabic**: Uses `csebuetnlp/mT5_multilingual_XLSum` for Arabic summarization.
5. **PDF Generation**: Outputs the summarized text into a PDF using `FPDF`.

## Key Files

- `requirements.txt`: Lists all the dependencies needed to run the project.
- `README.md`: Contains detailed instructions on how to set up and run the pipeline.
- `fonts/DejaVuSans-Bold.ttf` and `fonts/DejaVuSans.ttf`: Required fonts for generating PDFs with proper Unicode and language support (used in the Arabic text direction fixing).
  
## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
```

Navigate into the project directory:

```bash
cd <project-directory>
```

### 2. Install Dependencies

To install all necessary dependencies, simply run:

```bash
pip install -r requirements.txt
```

This will install libraries such as `PyMuPDF`, `pdfplumber`, `transformers`, `sentence-transformers`, `FPDF`, and `stanza`.

### 3. Update File Paths in the Notebook

Before running the notebook, **you need to update the following file paths**:

- **PDF File**: Update the path to the PDF file you want to summarize:
  
  ```python
  pdf_path = "/path/to/your/pdf-file.pdf"  # Replace with the correct PDF path
  ```

- **Font Files**: The DejaVu fonts used in the PDF generation must also be provided:
  
  ```python
  pdf.add_font('DejaVu', '', '/path/to/DejaVuSans.ttf', uni=True)
  pdf.add_font('DejaVu', 'B', '/path/to/DejaVuSans-Bold.ttf', uni=True)
  ```

  **Important**: These font files are already included in the repository under the `fonts/` directory. Replace the above paths with the actual location in the cloned repository:
  
  ```python
  pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
  pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
  ```

### 4. Run the Notebook

After updating the paths, open the Jupyter notebook and execute the cells. The notebook will:

1. Extract text from the PDF.
2. Detect the language of the text (either English or Arabic).
3. Summarize the content.
4. Generate a summarized PDF output.

### 5. Results

Once the notebook runs successfully, you will find a summarized version of the book saved as a PDF file in the specified output path.

## Models Used

- **English Summarization**: `facebook/bart-large-cnn` — a large CNN-based summarization model.
- **Arabic Summarization**: `csebuetnlp/mT5_multilingual_XLSum` — a multi-lingual summarization model fine-tuned for various languages, including Arabic.
- **Sentence Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` — used to divide English text into coherent semantic chunks.

## Example

To run the summarization on a sample PDF:

1. Ensure the PDF path is set correctly:

   ```python
   pdf_path = "samples/sample-book.pdf"  # Replace with your actual file
   ```

2. Ensure the font files are correctly referenced:

   ```python
   pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
   pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
   ```

3. Execute the notebook, and the summarized PDF will be saved in the specified output path.

## License

This project is open-source under the MIT License. Feel free to use, modify, and distribute.

## Contact

For any questions or suggestions, feel free to reach out or open an issue in the repository.
