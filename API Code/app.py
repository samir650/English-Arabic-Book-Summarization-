from flask import Flask, request, jsonify, render_template, send_file
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import re
import os
from langdetect import detect
import arabic_reshaper
from bidi.algorithm import get_display
import stanza
from fpdf import FPDF
import torch

# Initialize Flask app
app = Flask(__name__)

# Download the Arabic language model for Stanza (ensure this is done before initializing the pipeline)
stanza.download('ar')

# Set device to GPU if available, else CPU
device = 0 if torch.cuda.is_available() else -1

# Load models with the appropriate device
model_en = SentenceTransformer('all-MiniLM-L6-v2', device=device)
summarizer_en = pipeline("summarization", model="facebook/bart-large-cnn", device=device)
summarizer_ar = pipeline('summarization', model='csebuetnlp/mT5_multilingual_XLSum', device=device)
nlp_ar = stanza.Pipeline('ar', processors='tokenize', use_gpu=(device != -1))

# Helper functions

# Function: Extract text from the PDF file using pdfplumber
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

# Function: Clean the text by removing URLs, numbers, and extra spaces
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\b[A-Za-z]\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Function: Arabic Text Reshaping and Bidi Fix
def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# Function: Semantic Chunking (English)
def divide_by_semantics_with_length(text, threshold=0.6, max_words=800, min_words=400):
    sentences = re.split(r'(?<=[.!؟])\s+', text)  # Split on punctuation followed by space
    embeddings = model_en.encode(sentences, convert_to_tensor=True)
    chunks = []
    current_chunk = sentences[0]

    for i in range(1, len(sentences)):
        similarity = util.pytorch_cos_sim(embeddings[i], embeddings[i - 1])
        current_word_count = len(current_chunk.split())

        if similarity < threshold or current_word_count + len(sentences[i].split()) > max_words:
            if current_word_count >= min_words:
                chunks.append(current_chunk.strip())
                current_chunk = sentences[i]
            else:
                current_chunk += ' ' + sentences[i]
        else:
            current_chunk += ' ' + sentences[i]

    if len(current_chunk.split()) >= min_words:
        chunks.append(current_chunk.strip())

    return chunks

# Function: Semantic Chunking (Arabic)
def chunk_arabic_text(text, min_words=300, max_words=500):
    """Break the Arabic text into semantically meaningful chunks."""
    doc = nlp_ar(text)
    chunks = []
    current_chunk = []
    current_chunk_word_count = 0

    for sentence in doc.sentences:
        sentence_text = sentence.text
        sentence_word_count = len(sentence_text.split())

        # If the sentence is too long, split it into smaller sentences
        if sentence_word_count > max_words:
            split_sentences = split_long_sentence(sentence_text, max_words)
        else:
            split_sentences = [sentence_text]

        # Add the split sentences to the current chunk
        for split_sentence in split_sentences:
            split_sentence_word_count = len(split_sentence.split())
            if current_chunk_word_count + split_sentence_word_count > max_words and current_chunk_word_count >= min_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_chunk_word_count = 0

            current_chunk.append(split_sentence)
            current_chunk_word_count += split_sentence_word_count

    # Add the last chunk if it meets the minimum word requirement
    if current_chunk_word_count >= min_words:
        chunks.append(' '.join(current_chunk))

    return chunks

# Helper function to split long Arabic sentences
def split_long_sentence(sentence_text, max_words):
    words = sentence_text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# Function: Summarize text chunks
def summarize_chunks(chunks, summarizer, min_chunk_length=50, max_summary_length=300, min_summary_length=80):
    summaries = []
    for chunk in chunks:
        if len(chunk.split()) > min_chunk_length:
            try:
                summary = summarizer(chunk, max_length=max_summary_length, min_length=min_summary_length, do_sample=False)[0]['summary_text']
                summaries.append(summary)
            except Exception as e:
                print(f"Error summarizing chunk: {e}")
                summaries.append(chunk)
        else:
            summaries.append(chunk)
    return summaries

# PDF Generation Class

reshaped_text = arabic_reshaper.reshape("ملخص الكتاب")
_text = get_display(reshaped_text)


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('DejaVu', 'B', 12)
            title = _text if getattr(self, 'language', 'en') == 'ar' else 'Book Summary'
            self.cell(0, 10, title, ln=True, align='C')
            self.ln(10)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 12)
        align = 'R' if getattr(self, 'language', 'en') == 'ar' else 'L'
        self.multi_cell(0, 10, body, align=align)
        self.ln()

    def add_text(self, text):
        self.add_page()
        self.chapter_body(text)

# Helper function to generate the PDF
def generate_pdf(summary_text, pdf_output_path, language='en'):
    pdf = PDF()
    pdf.language = language
    pdf.add_font('DejaVu', '', './fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', './fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.add_text(summary_text)
    pdf.output(pdf_output_path)

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Summarize PDF
@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.pdf'):
        upload_dir = './uploads'
        output_dir = './output'

        # Create directories if they don't exist
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = os.path.join(upload_dir, file.filename)
        file.save(pdf_path)

        try:
            text = extract_text_from_pdf(pdf_path)
            if not text:
                return jsonify({"error": "Failed to extract text from PDF."}), 400

            language = detect(text)

            if language == 'ar':
                print("Detected Arabic. Running Arabic summarization pipeline...")
                fixed_text = fix_arabic_text(text)
                chunks = chunk_arabic_text(fixed_text)
                summarized_chunks = summarize_chunks(chunks, summarizer_ar)
                final_summary = ' '.join(summarized_chunks)
                final_summary_arabic = fix_arabic_text(final_summary)
                pdf_output_path = os.path.join(output_dir, 'arabic_summary.pdf')
                generate_pdf(final_summary_arabic, pdf_output_path, language='ar')
            else:
                print("Detected English. Running English summarization pipeline...")
                chunks = divide_by_semantics_with_length(text)
                summarized_chunks = summarize_chunks(chunks, summarizer_en)
                final_summary = '\n\n'.join(summarized_chunks)
                pdf_output_path = os.path.join(output_dir, 'english_summary.pdf')
                generate_pdf(final_summary, pdf_output_path, language='en')

            return send_file(pdf_output_path, as_attachment=True)

        except Exception as e:
            print(f"Error during summarization: {e}")
            return jsonify({"error": "An error occurred during summarization."}), 500

    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF file."}), 400

if __name__ == '__main__':
    app.run(debug=True)
