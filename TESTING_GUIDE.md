# API Testing Script Usage Guide

## Overview
The `test_api_endpoints.py` script is a comprehensive testing tool for the Indian Language Localizer Backend API. It tests all endpoints using files from the `testing_files/` directory and displays both input and output in the terminal.

## Features
- ✅ Tests all API endpoints systematically
- 📁 Uses actual files from `testing_files/` directory
- 🖥️ Shows detailed request/response information in terminal
- 🎨 Color-coded output for easy reading
- 🧹 Automatic cleanup of uploaded files
- ⚡ Real-time testing with live server

## Prerequisites
1. **Server Running**: Make sure your API server is running on `http://localhost:8000`
2. **Testing Files**: Ensure `testing_files/` directory contains:
   - `demo.mp4` (3.0MB video file)
   - `demo1.mp4` (1.6MB video file) 
   - `domo.mp3` (822KB audio file)
3. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r test_requirements.txt
   ```

## Usage

### Basic Usage
```bash
python test_api_endpoints.py
```

### Custom Server URL
```bash
python test_api_endpoints.py --url http://localhost:8080
```

### Skip Cleanup
```bash
python test_api_endpoints.py --no-cleanup
```

### Help
```bash
python test_api_endpoints.py --help
```

## Test Coverage

The script tests the following API categories:

### 1. Health & Monitoring
- ✅ Basic health check (`GET /`)
- ✅ Detailed health check (`GET /health/detailed`)
- ✅ System information (`GET /system/info`)
- ✅ Performance metrics (`GET /performance`)

### 2. Content Management
- ✅ File upload (`POST /content/upload`)
- ✅ Simple upload (`POST /upload`)
- ✅ List files (`GET /content/files`)
- ✅ Get file details (`GET /content/files/{id}`)

### 3. Translation Services
- ✅ Supported languages (`GET /supported-languages`)
- ✅ Language detection (`POST /detect-language`)
- ✅ Text translation (`POST /translate`)
- ✅ File translation (`POST /translate`)
- ✅ Context localization (`POST /localize/context`)
- ✅ Translation statistics (`GET /stats`)

### 4. Speech Processing
- ✅ Speech-to-Text (`POST /speech/stt`)
- ✅ Text-to-Speech (`POST /speech/tts`)
- ✅ Audio localization (`POST /speech/localize`)
- ✅ Subtitle generation (`POST /speech/subtitles`)

### 5. Video Processing
- ✅ Video localization (`POST /video/localize`)
- ✅ Audio extraction (`POST /video/extract-audio`)

### 6. Assessment Translation
- ✅ Sample formats (`GET /assessment/sample-formats`)
- ✅ Assessment validation (`POST /assessment/validate`)
- ✅ Assessment translation (`POST /assessment/translate`)

### 7. Job Management
- ✅ List jobs (`GET /jobs`)
- ✅ Trigger retraining (`POST /jobs/retrain`)
- ✅ Job status (`GET /jobs/{job_id}`)

### 8. LMS Integration
- ✅ Service status (`GET /integration/status`)
- ✅ Integration upload (`POST /integration/upload`)
- ✅ Get results (`GET /integration/results/{job_id}`)

### 9. Feedback System
- ✅ Submit feedback (`POST /feedback`)
- ✅ List feedback (`GET /feedback`)
- ✅ Get specific feedback (`GET /feedback/{id}`)

### 10. Error Handling
- ✅ Invalid language codes
- ✅ Non-existent files
- ✅ Invalid endpoints

## Output Format

The script provides detailed output for each test:

```
REQUEST:
  Method: POST
  URL: http://localhost:8000/translate
  Data:
    {
        "text": "Hello world",
        "source_language": "en",
        "target_languages": ["hi", "bn"]
    }

RESPONSE:
  Status Code: 200
  Headers:
    content-type: application/json
    content-length: 245
  Body:
    {
        "source_text": "Hello world",
        "results": [
            {
                "target_language": "hi",
                "translated_text": "नमस्ते दुनिया",
                "confidence": 0.95
            }
        ]
    }

POST /translate: PASS
  Details: Status: 200
```

## Test Results Summary

From the test run, we can see:

### ✅ Working Endpoints
- Health checks and system info
- File uploads and management
- Speech-to-Text processing
- Translation statistics
- Supported languages

### ⚠️ Issues Found
1. **Content-Type Issues**: Some POST endpoints expect JSON but receive form data
2. **Timeout Issues**: Some processing endpoints take longer than 60 seconds
3. **Status Code Mismatches**: Some endpoints return 201 instead of expected 200

### 🔧 Recommendations
1. Fix content-type handling for JSON endpoints
2. Increase timeout for processing endpoints
3. Update expected status codes in documentation
4. Add proper error handling for long-running operations

## Troubleshooting

### Server Not Running
```
ERROR: Cannot connect to server at http://localhost:8000
TIP: Make sure the server is running on http://localhost:8000
```
**Solution**: Start your API server before running tests

### Missing Testing Files
```
ERROR: Testing files directory not found: testing_files
```
**Solution**: Ensure `testing_files/` directory exists with required files

### Unicode Encoding Issues (Windows)
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**Solution**: The script includes Windows console encoding fixes

## Customization

You can modify the script to:
- Add new test cases
- Change timeout values
- Modify expected status codes
- Add custom validation logic
- Test different file types

## Contributing

To add new tests:
1. Create a new test method following the pattern `test_*_endpoints()`
2. Use `self.make_request()` for HTTP calls
3. Add the new test to `run_all_tests()` method
4. Update this documentation

## Notes

- The script automatically cleans up uploaded files after testing
- Some tests may take longer due to AI model processing
- The script handles both successful and error responses
- All output is color-coded for better readability
- Windows console encoding issues are automatically handled
