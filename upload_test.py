import requests
import json

# File path and patient info
file_path = "uploads/audio/eSOAP Sample Encounter.mp4"
patient_info = {
    "name": "John Doe",
    "mrn": "12345",
    "age": 45,
    "gender": "Male",
    "chief_complaint": "Chest pain"
}

print("Starting upload test...")
print(f"File path: {file_path}")
print(f"Patient info: {json.dumps(patient_info, indent=2)}")

# Make the request
with open(file_path, 'rb') as f:
    print("Sending request to /upload-audio...")
    response = requests.post(
        'http://127.0.0.1:8000/upload-audio',
        files={'file': f},
        data={'patient_info': json.dumps(patient_info)}
    )

# Print the response
print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2)) 