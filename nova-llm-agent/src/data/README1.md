# PDFs Directory

This directory is where you should place your PDF documents for Nova to process and use in its responses.

## Sample PDF Structure

For testing purposes, you can create a simple text file with the following content and convert it to PDF:

```text
Healthcare Receptionist Guidelines

1. Patient Demographics Collection
   - Full Name
   - Date of Birth
   - Address
   - Contact Information
   - Preferred Language
   - Special Needs

2. Insurance Verification Process
   - Collect Insurance Card Number
   - Verify Coverage Status
   - Check Plan Type (HMO/PPO)
   - Validate Deductible/Co-pay Status
   - Confirm Authorization Requirements

3. Appointment Scheduling Protocol
   - Verify Provider Availability
   - Check Patient Preferences
   - Confirm Insurance Coverage
   - Schedule Follow-up if Needed
   - Send Confirmation

4. Warm Handoff Procedures
   - Clinical Triage → Clara
   - Financial Counseling → Ray
   - Specialized Intake → Ivy
   - Emergency Services → 911

5. Security Verification
   - Required Security Questions
   - Identity Verification Steps
   - HIPAA Compliance Measures
```

## Converting to PDF

You can convert this text to PDF using any text editor or word processor:
1. Copy the content above
2. Paste into a text editor
3. Save as PDF

## Testing the System

After adding PDFs:
1. Run the processing script:
   ```bash
   npm run process-pdfs
   ```
2. Check the logs for successful processing
3. Test Nova's responses to verify the content is being used 