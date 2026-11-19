import io
import json
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError

from forensics.analyzer import analyze_image
from forensics.report import build_report_text, build_report_json, build_report_pdf


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Digital Evidence Forensics",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        color: #666;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        padding: 0.8rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }

    .small-note {
        font-size: 0.85rem;
        color: #666;

    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🔎 Digital Evidence Forensics</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">'
    'Explainable image authenticity, integrity and evidence assessment'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "Research/educational prototype: the displayed findings are heuristic "
    "decision-support indicators. They do not by themselves prove authenticity, "
    "manipulation, AI generation, or legal admissibility."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Application")

    st.caption(
        "Provides the investigator-facing interface, result visualization, "
        "explainability, AI detection and report generation."
    )

    st.divider()

    st.subheader("Supported files")

    st.write(
        "JPG / JPEG / PNG / WEBP / TIFF / BMP"
    )

    st.divider()

    st.subheader("Workflow")

    st.write("1. Upload evidence")
    st.write("2. Validate evidence")
    st.write("3. Analyze evidence")
    st.write("4. Review AI detection")
    st.write("5. Review forensic indicators")
    st.write("6. Inspect evidence fusion")
    st.write("7. Export report")


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "Upload a digital image for forensic analysis",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
        "tif",
        "tiff",
        "bmp",
    ],
    help=(
        "Upload the original evidence file when possible. "
        "Avoid editing or re-saving it before analysis."
    ),
)


if not uploaded:

    st.markdown("### Start an analysis")

    st.write(
        "Upload an image above. The application will calculate its SHA-256 "
        "hash and analyze metadata, AI-generation indicators, pixel/frequency "
        "features, provenance indicators and evidence fusion."
    )

    st.stop()


# ============================================================
# READ AND VALIDATE IMAGE
# ============================================================

data = uploaded.getvalue()

try:

    image = Image.open(io.BytesIO(data))

    image.verify()

    # Re-open after verify()
    image = Image.open(io.BytesIO(data))

except (UnidentifiedImageError, OSError) as exc:

    st.error(
        f"The uploaded file is not a readable image: {exc}"
    )

    st.stop()


# ============================================================
# RUN FORENSIC ANALYSIS
# ============================================================

with st.spinner("Running forensic analysis..."):

    try:

        result = analyze_image(
            data,
            uploaded.name,
        )

    except Exception as exc:

        st.error(
            f"Analysis failed: {exc}"
        )

        st.exception(exc)

        st.stop()


# ============================================================
# GET COMMON RESULT OBJECTS
# ============================================================

file_info = result.get("file", {})
metadata = result.get("metadata", {})
pixel = result.get("pixel", {})
provenance = result.get("provenance", {})
fusion = result.get("fusion", {})
assessment = result.get("assessment", {})

ai_detection = result.get(
    "ai_detection",
    {},
)

feature_data = result.get(
    "feature_scores",
    {},
)


# ============================================================
# EVIDENCE OVERVIEW
# ============================================================

st.header("1. Evidence Overview")

preview_col, info_col = st.columns(
    [1.15, 1]
)


# ------------------------------------------------------------
# Image preview
# ------------------------------------------------------------

with preview_col:

    st.image(
        image,
        caption=uploaded.name,
        use_container_width=True,
    )


# ------------------------------------------------------------
# File information
# ------------------------------------------------------------

with info_col:

    st.subheader("File Information")

    st.write(
        f"**Filename:** "
        f"{file_info.get('name', uploaded.name)}"
    )

    st.write(
        f"**Format:** "
        f"{file_info.get('format', 'N/A')}"
    )

    st.write(
        f"**File size:** "
        f"{file_info.get('size_bytes', 0):,} bytes"
    )

    st.write(
        f"**Dimensions:** "
        f"{file_info.get('width', 'N/A')} × "
        f"{file_info.get('height', 'N/A')}"
    )

    st.write(
        f"**SHA-256:** "
        f"`{file_info.get('sha256', 'N/A')}`"
    )

    st.caption(
        "SHA-256 fingerprints the exact uploaded byte content."
    )


# ============================================================
# AI DETECTION
# ============================================================

st.header("2. AI Image Detection")

if ai_detection:

    ai_label = ai_detection.get(
        "label",
        "N/A",
    )

    ai_probability = float(
        ai_detection.get(
            "ai_probability",
            0.0,
        )
    )

    real_probability = float(
        ai_detection.get(
            "real_probability",
            0.0,
        )
    )

    model_name = ai_detection.get(
        "model",
        "N/A",
    )

    ai1, ai2, ai3 = st.columns(3)

    ai1.metric(
        "Prediction",
        ai_label,
    )

    ai2.metric(
        "AI Probability",
        f"{ai_probability * 100:.2f}%",
    )

    ai3.metric(
        "Real Probability",
        f"{real_probability * 100:.2f}%",
    )

    st.write(
        f"**Model:** `{model_name}`"
    )

    st.caption(
        "The AI detector provides model-based evidence and should be "
        "interpreted together with the other forensic indicators."
    )

else:

    st.warning(
        "AI detection information is not available in the current analysis result."
    )


# ============================================================
# ASSESSMENT SUMMARY
# ============================================================

st.header("3. Assessment Summary")

assessment_authenticity = assessment.get(
    "authenticity",
    "N/A",
)

assessment_integrity = assessment.get(
    "integrity",
    "N/A",
)

assessment_reliability = assessment.get(
    "reliability",
    "N/A",
)

fusion_score = float(
    fusion.get(
        "score",
        0.0,
    )
)

fusion_level = fusion.get(
    "level",
    "N/A",
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Authenticity",
    assessment_authenticity,
)

c2.metric(
    "Integrity",
    assessment_integrity,
)

c3.metric(
    "Reliability",
    assessment_reliability,
)

c4.metric(
    "Fusion Score",
    f"{fusion_score:.2f}/100",
)


st.progress(
    max(
        0.0,
        min(
            1.0,
            fusion_score / 100.0,
        ),
    )
)

st.caption(
    f"Evidence level: **{fusion_level}**"
)


# ============================================================
# FEATURE SCORES
# ============================================================

st.header("4. Individual Feature Scores")

# ------------------------------------------------------------
# Get feature scores
# ------------------------------------------------------------

if isinstance(feature_data, dict) and "scores" in feature_data:

    feature_scores = feature_data["scores"]

else:

    feature_scores = feature_data


# ------------------------------------------------------------
# Fallback calculation
# ------------------------------------------------------------

if not feature_scores:

    ai_score = ai_probability * 100.0 if ai_detection else 0.0

    metadata_score = (
        75.0
        if not metadata.get("exif_present", False)
        else 0.0
    )

    ela_score = (
        100.0
        if pixel.get("ela_mean_error", 0.0) > 8
        else 20.0
    )

    frequency_score = (
        90.0
        if pixel.get("high_frequency_ratio", 0.0) > 0.18
        else 0.0
    )

    noise_score = (
        80.0
        if pixel.get("noise_std", 0.0) < 3
        else 0.0
    )

    provenance_score = (
        30.0
        if not metadata.get("exif_present", False)
        else 0.0
    )

    feature_scores = {
        "ai_detection": ai_score,
        "metadata": metadata_score,
        "ela": ela_score,
        "frequency": frequency_score,
        "noise": noise_score,
        "provenance": provenance_score,
    }


# ------------------------------------------------------------
# Display feature scores
# ------------------------------------------------------------

score_names = [
    "ai_detection",
    "metadata",
    "ela",
    "frequency",
    "noise",
    "provenance",
]


score_labels = {
    "ai_detection": "AI Detection",
    "metadata": "Metadata",
    "ela": "ELA",
    "frequency": "Frequency",
    "noise": "Noise",
    "provenance": "Provenance",
}


score_values = {}


for name in score_names:

    raw_score = feature_scores.get(
        name,
        0.0,
    )

    if isinstance(raw_score, dict):

        raw_score = raw_score.get(
            "score",
            0.0,
        )

    try:

        raw_score = float(raw_score)

    except (
        TypeError,
        ValueError,
    ):

        raw_score = 0.0

    score_values[name] = raw_score


cols = st.columns(3)

for index, name in enumerate(score_names):

    with cols[index % 3]:

        st.metric(
            score_labels[name],
            f"{score_values[name]:.2f}/100",
        )


# ============================================================
# WEIGHTS AND CONTRIBUTIONS
# ============================================================

st.header("5. Evidence Fusion")

weights = {
    "ai_detection": 0.30,
    "metadata": 0.15,
    "ela": 0.20,
    "frequency": 0.15,
    "noise": 0.10,
    "provenance": 0.10,
}


fusion_col1, fusion_col2 = st.columns(
    2
)


# ------------------------------------------------------------
# Weights
# ------------------------------------------------------------

with fusion_col1:

    st.subheader("Feature Weights")

    for name in score_names:

        st.write(
            f"**{score_labels[name]}:** "
            f"{weights[name]:.2f}"
        )


# ------------------------------------------------------------
# Contributions
# ------------------------------------------------------------

with fusion_col2:

    st.subheader("Weighted Contributions")

    for name in score_names:

        contribution = (
            score_values[name]
            * weights[name]
        )

        st.write(
            f"**{score_labels[name]}:** "
            f"{contribution:.2f}"
        )


st.divider()

st.metric(
    "Final Evidence-Fusion Score",
    f"{fusion_score:.2f}/100",
)

st.write(
    f"**Evidence Level:** {fusion_level}"
)


if fusion.get("evidence"):

    st.subheader(
        "Evidence Contributing to Result"
    )

    for item in fusion["evidence"]:

        st.write(
            "•",
            item,
        )


# ============================================================
# DETAILED FORENSIC FINDINGS
# ============================================================

st.header("6. Detailed Forensic Findings")

tab1, tab2, tab3 = st.tabs(
    [
        "Metadata / EXIF",
        "Pixel / Frequency",
        "Provenance",
    ]
)


# ============================================================
# METADATA TAB
# ============================================================

with tab1:

    st.subheader(
        "Metadata / EXIF Analysis"
    )

    exif_present = metadata.get(
        "exif_present",
        False,
    )

    st.write(
        f"**EXIF present:** "
        f"{'Yes' if exif_present else 'No'}"
    )

    fields = metadata.get(
        "fields",
        {},
    )

    if fields:

        st.json(fields)

    else:

        st.warning(
            "No readable EXIF fields were found."
        )

    indicators = metadata.get(
        "indicators",
        [],
    )

    if indicators:

        st.markdown(
            "**Metadata Indicators**"
        )

        for item in indicators:

            st.write(
                "•",
                item,
            )


# ============================================================
# PIXEL TAB
# ============================================================

with tab2:

    st.subheader(
        "Pixel and Frequency Analysis"
    )

    pc1, pc2, pc3 = st.columns(3)

    pc1.metric(
        "ELA Mean Error",
        f"{pixel.get('ela_mean_error', 0.0):.3f}",
    )

    pc2.metric(
        "High-Frequency Ratio",
        f"{pixel.get('high_frequency_ratio', 0.0):.3f}",
    )

    pc3.metric(
        "Noise Std. Deviation",
        f"{pixel.get('noise_std', 0.0):.3f}",
    )

    st.write(
        "**JPEG quantization tables:** "
        f"{'Detected' if pixel.get('jpeg_quantization_detected', False) else 'Not detected'}"
    )

    ela_image = pixel.get(
        "ela_image_png"
    )

    if ela_image:

        st.image(
            ela_image,
            caption="Error Level Analysis (ELA) Visualization",
            use_container_width=True,
        )

    indicators = pixel.get(
        "indicators",
        [],
    )

    if indicators:

        st.markdown(
            "**Pixel / Frequency Indicators**"
        )

        for item in indicators:

            st.write(
                "•",
                item,
            )


# ============================================================
# PROVENANCE TAB
# ============================================================

with tab3:

    st.subheader(
        "Provenance and Integrity"
    )

    observations = provenance.get(
        "observations",
        [],
    )

    if observations:

        for item in observations:

            st.write(
                "•",
                item,
            )

    else:

        st.info(
            "No additional provenance observations are available."
        )


# ============================================================
# EXPLAINABLE ASSESSMENT
# ============================================================

st.header("7. Explainable Assessment")

explanations = result.get(
    "explanation",
    [],
)

if explanations:

    for explanation in explanations:

        st.write(
            "•",
            explanation,
        )

else:

    st.info(
        "No explanation entries were generated."
    )


st.subheader("Recommendation")

st.write(
    assessment.get(
        "recommendation",
        "No recommendation available.",
    )
)


# ============================================================
# REPORTING
# ============================================================

st.header("8. Forensic Reporting")

st.write(
    "The report contains the evidence identity, metadata findings, "
    "AI detection, pixel/frequency findings, provenance observations, "
    "individual feature scores, evidence-fusion result, assessment, "
    "explanation, recommendation and prototype disclaimer."
)


# ------------------------------------------------------------
# Build reports
# ------------------------------------------------------------

try:

    report_text = build_report_text(
        result
    )

    report_json = build_report_json(
        result
    )

    report_pdf = build_report_pdf(result)

except Exception as exc:

    st.error(
        f"Report generation failed: {exc}"
    )

    report_text = ""
    report_json = ""


base_name = Path(
    uploaded.name
).stem


r1, r2, r3 = st.columns(3)


with r1:

    if report_text:

        st.download_button(
            "📄 Download forensic report (.txt)",
            data=report_text.encode(
                "utf-8"
            ),
            file_name=(
                f"{base_name}_forensic_report.txt"
            ),
            mime="text/plain",
            use_container_width=True,
        )


with r2:

    if report_json:

        st.download_button(
            "🧾 Download analysis data (.json)",
            data=report_json.encode(
                "utf-8"
            ),
            file_name=(
                f"{base_name}_forensic_analysis.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

with r3:

    st.download_button(
        "📑 Download forensic report (.pdf)",
        data=report_pdf,
        file_name=f"{base_name}_forensic_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ============================================================
# DEVELOPER VIEW
# ============================================================

with st.expander(
    "Developer view – structured analysis result"
):

    debug_result = json.loads(
        json.dumps(
            result,
            default=str,
        )
    )

    # Do not expose binary ELA data
    debug_result.get(
        "pixel",
        {}
    ).pop(
        "ela_image_png",
        None,
    )

    st.json(
        debug_result
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Digital Evidence Forensics Prototype • "
    "Application & Reporting Module • "
    "Use findings together with case context and expert examination."
)