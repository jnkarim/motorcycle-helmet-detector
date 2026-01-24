# Helmet Violation Detection System using YOLOv8

## 📌 Project Overview

This project aims to build a computer vision–based traffic violation detection system that identifies **motorcycle riders without helmets** and captures their **vehicle license plates** for enforcement purposes.

The system follows a **conditional detection pipeline** to ensure efficiency, accuracy, and industry-level design standards.

---

## 🎯 Objectives

1. Detect motorcycles in traffic images
2. Detect whether the rider is wearing a helmet
3. If **no helmet** is detected, locate the **license plate**
4. (Future Scope) Apply OCR on detected license plates to extract registration numbers

---

## 📂 Project Structure

```
helmet_violation_project/
│
├── datasets/
│   ├── bike/
│   ├── helmet/
│   └── plate/
│
├── training/
│   ├── bike_detection/
│   ├── helmet_detection/
│   └── plate_detection/
│
├── inference/
│   └── pipeline.py
│
├── results/
│   ├── metrics/
│   └── sample_outputs/
│
├── report/
│   └── final_report.pdf
│
└── README.md
```

## 🧠 System Architecture

The system uses a **multi-stage conditional pipeline**:


This approach:
- Reduces unnecessary computation
- Minimizes false detections
- Aligns with real-world traffic enforcement systems

---

## 🛠️ Technologies Used

- **YOLOv8** (Ultralytics)
- **Roboflow** (Dataset management & annotation)
- **Google Colab** (Training & experimentation)
- **Python**
- **OpenCV** (Inference & visualization)

---

## 🚦 Scope & Limitations

### Included
- Detection-based system
- Image-based input (initial phase)
- Conditional inference logic

### Not Included (Current Version)
- OCR / number recognition
- Face recognition
- Rider identification
- Real-time government deployment

---

## 🔮 Future Enhancements

- Integrate OCR (EasyOCR / PaddleOCR / Tesseract)
- Extend system to video streams
- Deploy on edge devices (e.g., Jetson Nano)
- Add violation logging and analytics dashboard

---

## 🌏 Use Case Relevance

This system is highly applicable to:
- Smart traffic monitoring
- Helmet law enforcement
- Smart city surveillance systems
- Developing-country traffic conditions (e.g., Bangladesh)

---

