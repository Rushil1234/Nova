# Data Directory

This directory contains the data files used by Nova, the healthcare receptionist AI.

## Directory Structure

```
data/
├── pdfs/           # PDF documents for RAG (Retrieval-Augmented Generation)
└── README.md       # This file
```

## PDFs Directory

The `pdfs` directory is used to store PDF documents that Nova uses to provide accurate and up-to-date information. These documents are processed and their content is used to enhance Nova's responses.

### Supported PDF Types
- Healthcare policies and procedures
- Insurance coverage documents
- Appointment scheduling guidelines
- Clinical service descriptions
- Patient care protocols

### Adding New PDFs
1. Place your PDF files in the `pdfs` directory
2. Run the PDF processing script:
   ```bash
   npm run process-pdfs
   ```
3. The system will automatically:
   - Extract text from the PDFs
   - Create embeddings
   - Store them in the vector database
   - Make them available for Nova's responses

### Best Practices
- Use clear, descriptive filenames
- Ensure PDFs are text-based (not scanned images)
- Keep documents up to date
- Remove outdated documents
- Use consistent formatting

### File Naming Convention
Use the following format for PDF filenames:
```
category_subcategory_description_version.pdf
```
Example: `insurance_coverage_medicare_2024.pdf` 