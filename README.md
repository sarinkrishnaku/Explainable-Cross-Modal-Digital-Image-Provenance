# Explainable Cross-Modal Digital Image Provenance for AI-Generated Image Detection

A Python-based digital image forensics application that combines AI-generated image detection with traditional forensic indicators to support explainable image authenticity and provenance assessment.

The application analyzes an uploaded image using multiple sources of evidence, combines the findings through a weighted evidence-fusion mechanism, and generates an explainable forensic assessment.

> **Note:** This is an academic research prototype. Its heuristic forensic scores and AI detector output are supporting indicators, not definitive proof of image authenticity, manipulation, or AI generation.

## Features

- **Image Upload and Validation:** Accepts JPG, JPEG, PNG, WEBP, TIFF, and BMP images.
- **File Integrity:** Calculates the SHA-256 hash of the uploaded image.
- **Metadata Analysis:** Extracts available EXIF metadata and identifies relevant observations.
- **Error Level Analysis (ELA):** Examines image recompression differences.
- **Frequency Analysis:** Uses FFT-based analysis to examine frequency-domain characteristics.
- **Noise Analysis:** Examines high-pass residual characteristics.
- **Provenance Analysis:** Combines metadata and forensic observations to provide provenance-related indicators.
- **AI-Generated Image Detection:** Uses a pretrained image classification model.
- **Weighted Evidence Fusion:** Combines individual forensic and AI detection scores.
- **Explainable Assessment:** Displays findings and explanations behind the assessment.
- **Forensic Report Generation:** Allows users to download analysis results in TXT and JSON formats.

## System Architecture

The application follows a modular architecture.

```text
                 User
                  |
                  v
             Streamlit UI
                app.py
                  |
                  v
          Image Upload/Validation
                  |
        +---------+----------+
        |                    |
        v                    v
  Forensic Analysis     AI Detection
  analyzer.py           ai_detector.py
        |                    |
        v                    v
  Metadata / EXIF       Pretrained Model
  ELA                   Inference
  Frequency Analysis
  Noise Analysis
  Provenance
        |                    |
        +---------+----------+
                  |
                  v
           Evidence Fusion
                  |
                  v
         Explainable Assessment
                  |
                  v
           Report Generation
              report.py
                  |
                  v
             TXT / JSON
```

## Technology Stack

- **Python** – Main programming language.
- **Streamlit** – Web-based user interface.
- **PyTorch** – Deep learning inference.
- **Hugging Face Transformers** – Loading and using the pretrained image classification model.
- **Pillow (PIL)** – Image processing and metadata extraction.
- **OpenCV** – Image processing operations.
- **NumPy** – Numerical and frequency-domain calculations.
- **hashlib** – SHA-256 file hashing.
- **ReportLab** – Report-related functionality.
- **pytest** – Automated testing.

## AI Detection Model

The project uses the pretrained model:

`delpot/steganograph-ia-detector`

The model is loaded through Hugging Face Transformers and used for inference. The project does not train this model.

The AI detector output is treated as one source of evidence and is combined with the other forensic indicators.

## Evidence Fusion

The current implementation uses a weighted evidence-fusion approach.

| Evidence Feature | Weight |
|---|---:|
| AI Detection | 0.30 |
| Metadata | 0.15 |
| Error Level Analysis | 0.20 |
| Frequency Analysis | 0.15 |
| Noise Analysis | 0.10 |
| Provenance | 0.10 |

The combined score is a heuristic anomaly-evidence score on a 0–100 scale. It is not a calibrated probability that an image is fake or AI-generated.

## Project Structure

```text
digital_evidence_forensics/
|
|-- app.py
|-- README.md
|-- requirements.txt
|-- requirements_dev.txt
|-- .gitignore
|
|-- forensics/
|   |-- analyzer.py
|   |-- ai_detector.py
|   |-- report.py
|
|-- tests/
    |-- test_pipeline.py
    |-- test_full_analysis.py
    |-- test_ai_detector.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd digital_evidence_forensics
```

Replace `YOUR_REPOSITORY_URL` with the actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Install a compatible PyTorch build for your system if necessary:

https://pytorch.org/get-started/locally/

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your default browser.

The first AI detection may take longer because the pretrained model needs to be downloaded and loaded.

## Testing

The project contains test scripts for the analysis pipeline, full forensic analysis, and AI detection.

To run the automated pipeline test:

```bash
pytest -v tests/test_pipeline.py
```

The full-analysis and AI-detector scripts use external image files. Provide suitable images and update their paths before running them.

## Limitations

- The forensic thresholds and fusion weights are preliminary heuristics.
- The fusion score is not a calibrated probability of manipulation or AI generation.
- Missing EXIF metadata does not prove that an image has been manipulated.
- SHA-256 verifies file-byte identity when compared with a trusted hash; it does not independently establish authenticity or authorship.
- The pretrained AI detector may not generalize to every image generator, image format, resolution, or editing operation.
- The pilot evaluation uses a limited CIFAKE test subset and does not establish performance on all real-world images.
- The application does not reconstruct a complete chain of custody or establish legal admissibility.
- The application is intended as a research and educational prototype and does not replace expert forensic examination.

## Future Improvements

- Evaluate the system on larger and more diverse image datasets.
- Improve robustness against resizing, compression, and image transformations.
- Calibrate forensic thresholds and evidence-fusion weights using controlled experiments.
- Explore stronger explainability methods for AI detector predictions.
- Expand provenance analysis and evidence tracking.

## Disclaimer

This project is developed for academic research and educational purposes. All automated findings should be interpreted as supporting evidence and reviewed alongside other relevant information.