""" Veri-Quick Scanner"
 Making Documentation paperless


Access: Limited and under copyright license  
Classification: Private/Proprietary Software
Security Level: Restricted

License: Proprietary - All Rights Reserved
Copyright: © 2025 Veriquick LLC. All rights reserved.
Permission required to edit and modify the code  

Owner details: https://www.github.com/DebashishRana
Github Repository: https://www.github.com/DebashishRana/Veri-Quick-Proto
Documentation:https://drive.google.com/drive/folders/1_LY23TwtPzPlkIbBl1gZK9wA2B6DXCRY?usp=sharing
Mail: mailto:dimareznokov@gmail.com
Phone: callto:+91 9304211754
Linkedin: https://www.linkedin.com/in/devarana 

Permission required to edit and modify the code 

Date of update : 10-07-2025

Version : 2.3.0

"""

# Importing necessary modules
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol
import webbrowser
import pygame
import sys
import json
import os
import time
import io
try:
    import qrcode
except ImportError:
    qrcode = None
from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget, 
                            QHBoxLayout, QPushButton, QStatusBar, QMessageBox, QScrollArea, QFrame,
                            QProgressBar, QGraphicsOpacityEffect, QGridLayout)
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal

# Initialize pygame mixer and preload sounds for faster access
pygame.mixer.init()
# Use relative paths for sound files to make the application more portable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "assets")
APP_ICON_PATH = os.path.join(SOUND_DIR, "favicon.ico")
SPLASH_LOGO_PATH = APP_ICON_PATH
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
SUCCESS_SOUND = os.path.join(SOUND_DIR, "document_loaded.mp3")
AADHAAR_DETECTED_SOUND = os.path.join(SOUND_DIR, "aadhar_detected.mp3")
PAN_VERIFICATION_SOUND = os.path.join(SOUND_DIR, "pan_detected.mp3")
MANUAL_VERIFICATION_SOUND = os.path.join(SOUND_DIR, "verification_unsuccessful.mp3")
ERROR_SCANNING = os.path.join(SOUND_DIR,"Scan_error.mp3")
PRIMARY_READY_SOUND = os.path.join(SOUND_DIR, "EDV_R.mp3")


# Fallback to absolute paths if relative paths don't exist
if not os.path.exists(SOUND_DIR):
    SUCCESS_SOUND = r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Veriquick assets\Application Assets\Success.mp3"
    AADHAAR_DETECTED_SOUND = r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Veriquick assets\Application Assets\AadharLV.mp3"
    PAN_VERIFICATION_SOUND = r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Veriquick assets\Application Assets\PANLV.mp3"
    MANUAL_VERIFICATION_SOUND = r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Veriquick assets\Application Assets\Verification Failure.mp3"
    ERROR_SCANNING = r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Veriquick assets\Application Assets\EDV_R.mp3"

# Candidate paths for EDV ready sound; scanned in order
READY_SOUND_CANDIDATES = [PRIMARY_READY_SOUND,
    r"D:\Python\Main Python Directory\Mega projects\Prototype assets\Project Veriquick\Application Assets\EDV_R.mp3"
]
# Normalize and drop duplicates while preserving order
normalized_candidates = []
seen_ready_paths = set()
for candidate in READY_SOUND_CANDIDATES:
    if not candidate:
        continue
    normalized = os.path.normpath(candidate)
    if normalized in seen_ready_paths:
        continue
    normalized_candidates.append(normalized)
    seen_ready_paths.add(normalized)
READY_SOUND_CANDIDATES = normalized_candidates
# application images

if not os.path.exists(APP_ICON_PATH):
    app_icon = r"D:\Python\Main Python Directory\Mega projects\Veri-Quick-Proto\favicon.ico"
    SPLASH_LOGO_PATH = app_icon
else:
    app_icon = APP_ICON_PATH



class IntroSplash(QWidget):
    """Intro animation with logo fade-in and progress bar."""

    finished = pyqtSignal()

    def __init__(self, logo_path, duration=1800, parent=None):
        super().__init__(parent)
        self.logo_path = logo_path
        self.duration = duration
        self.elapsed = 0
        self.timer_interval = 25

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: #151515; border-radius: 16px;")
        self.setFixedSize(520, 360)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(36, 36, 36, 36)
        outer_layout.setSpacing(24)
        self.setLayout(outer_layout)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(self.logo_path)
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_logo)
        else:
            self.logo_label.setText("Veriquick")
            self.logo_label.setFont(QFont("Arial", 28, QFont.Bold))
            self.logo_label.setStyleSheet("color: #ffffff;")

        self.status_label = QLabel("Initializing modules...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #f5f5f5; font-size: 13px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet(
            "QProgressBar {background-color: #2b2b2b; border-radius: 6px;}"
            "QProgressBar::chunk {background-color: #ff6f00; border-radius: 6px;}"
        )

        outer_layout.addStretch()
        outer_layout.addWidget(self.logo_label)
        outer_layout.addStretch()
        outer_layout.addWidget(self.status_label)
        outer_layout.addWidget(self.progress_bar)

        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)

        self.logo_effect = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(self.logo_effect)

        self.logo_animation = QPropertyAnimation(self.logo_effect, b"opacity", self)
        self.logo_animation.setDuration(900)
        self.logo_animation.setStartValue(0.0)
        self.logo_animation.setEndValue(1.0)
        self.logo_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.move(screen_geometry.center() - self.rect().center())

    def start(self):
        self.progress_bar.setValue(0)
        self.elapsed = 0
        self.show()
        QTimer.singleShot(0, self.center_on_screen)
        self.logo_animation.start()
        self.progress_timer.start(self.timer_interval)

    def update_progress(self):
        self.elapsed += self.timer_interval
        progress = min(100, int((self.elapsed / self.duration) * 100))
        self.progress_bar.setValue(progress)

        if progress < 35:
            self.status_label.setText("Loading camera interface...")
        elif progress < 70:
            self.status_label.setText("Preparing verification modules...")
        else:
            self.status_label.setText("Starting Veri-Quick Scanner...")

        if progress >= 100:
            self.progress_timer.stop()
            QTimer.singleShot(180, self.finished.emit)


class InfoOverlay(QWidget):
    """Overlay that summarizes verification details with QR and metadata."""

    dismissed = pyqtSignal()

    DETAIL_LABELS = {
        "document_type": "Document Type",
        "file_name": "Document Name",
        "document_number": "Document Number",
        "document_id": "Document ID",
        "holder_name": "Holder Name",
        "document_holder": "Document Holder",
        "customer_name": "Customer Name",
        "aadhaar_numbers": "Aadhaar Number(s)",
        "pan_numbers": "PAN Number(s)",
        "gst_numbers": "GST Number(s)",
        "cin_numbers": "CIN Number(s)",
        "mobile_number": "Mobile Number",
        "expiry_date": "Expiry Date",
        "expires_on": "Expiry Date",
        "issued_on": "Issued On",
        "document_url": "Document URL",
    }

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName("InfoOverlay")

        self.auto_close_ms = 12000
        self.remaining_seconds = self.auto_close_ms // 1000

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame()
        self.container.setStyleSheet(
            "QFrame { background-color: rgba(12, 12, 16, 235); border-radius: 24px; }"
        )
        outer_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(28, 24, 28, 24)
        container_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        self.title_label = QLabel("Verification Details")
        self.title_label.setStyleSheet("color: #f5f5f5; font-size: 18px; font-weight: 600;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.countdown_label = QLabel("Auto closing in 12s")
        self.countdown_label.setStyleSheet("color: #9aa0b1; font-size: 12px;")
        header_layout.addWidget(self.countdown_label)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setCursor(Qt.PointingHandCursor)
        self.skip_button.setStyleSheet(
            "QPushButton { background: #ff7043; color: #fff; border: none;"
            "padding: 6px 16px; border-radius: 14px; font-weight: 600; }"
            "QPushButton:hover { background: #ff5722; }"
        )
        self.skip_button.clicked.connect(self.hide_overlay)
        header_layout.addWidget(self.skip_button)

        container_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        container_layout.addLayout(content_layout)

        # Left panel with QR and summary
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(260)
        self.left_panel.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #3730a3, stop:1 #5b21b6); border-radius: 20px; }"
        )
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(18)

        self.summary_label = QLabel("Verified Document")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        left_layout.addWidget(self.summary_label)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(180, 180)
        self.qr_label.setStyleSheet(
            "background: rgba(255, 255, 255, 26); border-radius: 18px;"
        )
        left_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        self.primary_details_label = QLabel()
        self.primary_details_label.setWordWrap(True)
        self.primary_details_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px;")
        left_layout.addWidget(self.primary_details_label)

        left_layout.addStretch()

        content_layout.addWidget(self.left_panel)

        # Right panel with detail cards
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet(
            "QFrame { background: transparent; }"
        )
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        self.details_grid = QGridLayout()
        self.details_grid.setSpacing(16)
        right_layout.addLayout(self.details_grid)
        right_layout.addStretch()

        content_layout.addWidget(self.right_panel, 1)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_overlay)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_overlay()

    def showEvent(self, event):
        super().showEvent(event)
        self.position_overlay()

    def position_overlay(self):
        parent = self.parentWidget()
        if parent:
            parent_rect = parent.rect()
            overlay_rect = self.frameGeometry()
            x = parent_rect.center().x() - overlay_rect.width() // 2
            y = parent_rect.center().y() - overlay_rect.height() // 2
            self.move(max(20, x), max(20, y))

    def show_info(self, files, qr_data):
        if not files:
            return

        self.hide_timer.stop()
        self.countdown_timer.stop()

        self.populate_left_panel(files[0], qr_data)
        self.populate_details(files)

        self.remaining_seconds = self.auto_close_ms // 1000
        self.countdown_label.setText(f"Auto closing in {self.remaining_seconds}s")
        self.hide_timer.start(self.auto_close_ms)
        self.countdown_timer.start(1000)

        self.setFixedSize(900, 420)
        self.show()
        self.raise_()

    def populate_left_panel(self, primary_doc, qr_data):
        doc_type = primary_doc.get("document_type", "Document")
        file_name = primary_doc.get("file_name", "")
        holder = (primary_doc.get("holder_name") or primary_doc.get("document_holder")
                  or primary_doc.get("customer_name") or "")

        summary_text = f"{doc_type}"
        if holder:
            summary_text += f"\nfor {holder}"
        self.summary_label.setText(summary_text)

        details_lines = []
        if file_name:
            details_lines.append(f"Document: <b>{file_name}</b>")
        key_options = ["document_number", "aadhaar_numbers", "pan_numbers", "gst_numbers", "cin_numbers"]
        for key in key_options:
            value = primary_doc.get(key)
            if value:
                formatted = self.format_value(value)
                details_lines.append(f"ID: {formatted}")
                break
        expiry = primary_doc.get("expiry_date") or primary_doc.get("expires_on")
        if expiry:
            details_lines.append(f"Valid till {expiry}")
        issued = primary_doc.get("issued_on")
        if issued:
            details_lines.append(f"Issued on {issued}")

        self.primary_details_label.setText("<br/>".join(details_lines))

        pixmap = self.generate_qr_pixmap(qr_data)
        if pixmap:
            scaled = pixmap.scaled(self.qr_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled)
            self.qr_label.setStyleSheet(
                "background: rgba(255, 255, 255, 26); border-radius: 18px;"
            )
        else:
            truncated = (qr_data[:120] + "...") if len(qr_data) > 120 else qr_data
            self.qr_label.setPixmap(QPixmap())
            self.qr_label.setText(truncated)
            self.qr_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.qr_label.setStyleSheet(
                "color: #f5f5f5; padding: 12px; background: rgba(0,0,0,0.25); border-radius: 18px;"
            )

    def populate_details(self, files):
        while self.details_grid.count():
            item = self.details_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for index, doc in enumerate(files):
            card = self.build_detail_card(doc, index)
            row, col = divmod(index, 2)
            self.details_grid.addWidget(card, row, col)

    def build_detail_card(self, doc, index):
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: rgba(28, 31, 43, 0.95); border-radius: 16px;"
            "border: 1px solid rgba(255,255,255,0.04); }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        title = QLabel(doc.get("file_name") or f"Document {index + 1}")
        title.setStyleSheet("color: #e5e7ff; font-size: 14px; font-weight: 600;")
        layout.addWidget(title)

        subtitle = QLabel(doc.get("document_type", "Unknown"))
        subtitle.setStyleSheet("color: #8b90a7; font-size: 12px;")
        layout.addWidget(subtitle)

        for key, label in self.DETAIL_LABELS.items():
            if key not in doc:
                continue
            value = doc[key]
            if not value:
                continue
            formatted_value = self.format_value(value)
            if not formatted_value:
                continue
            detail_label = QLabel(f"<span style='color:#6b7280;'>{label}</span><br/>"
                                  f"<span style='color:#f3f4f6; font-size:12px;'>{formatted_value}</span>")
            detail_label.setTextFormat(Qt.RichText)
            detail_label.setWordWrap(True)
            layout.addWidget(detail_label)

        layout.addStretch()
        return card

    @staticmethod
    def format_value(value):
        if isinstance(value, list):
            return ", ".join(str(v) for v in value if v)
        if isinstance(value, dict):
            parts = []
            for k, v in value.items():
                if v:
                    parts.append(f"{k}: {v}")
            return ", ".join(parts)
        return str(value)

    def generate_qr_pixmap(self, qr_data):
        if not qr_data or qrcode is None:
            return None
        try:
            qr_img = qrcode.make(qr_data)
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), "PNG")
            return pixmap
        except Exception as exc:
            print(f"QR generation failed: {exc}")
            return None

    def update_countdown(self):
        self.remaining_seconds = max(0, self.remaining_seconds - 1)
        self.countdown_label.setText(f"Auto closing in {self.remaining_seconds}s")
        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()

    def hide_overlay(self):
        self.hide_timer.stop()
        self.countdown_timer.stop()
        self.hide()
        self.dismissed.emit()

class QRScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = None
        self.initialize_camera()

        # Set initial flags and timers
        self.qr_data = None
        self.browser_opened = False
        self.last_scan_time = 0
        self.scan_cooldown = 10  # seconds between scans
        self.sound_queue = []  # Queue for sounds to play
        self.is_playing_sound = False
        self.last_result = None  # Store last scan result
        self.ready_sound_path = next((path for path in READY_SOUND_CANDIDATES if os.path.exists(path)), None)
        if not self.ready_sound_path:
            checked_paths = " | ".join(READY_SOUND_CANDIDATES)
            print(f"EDV ready sound file not found; checked: {checked_paths}")
        else:
            print(f"EDV ready sound loaded from: {self.ready_sound_path}")
        self.current_sound = None
        
        # Main timer for camera updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Frame rate control
        
        # Timer for sound queue processing
        self.sound_timer = QTimer()
        self.sound_timer.timeout.connect(self.process_sound_queue)
        self.sound_timer.start(100)  # Check sound queue every 100ms

        # Detail labels mapping
        self.DETAIL_LABELS = {
            "document_type": "Document Type",
            "file_name": "Document Name",
            "document_number": "Document Number",
            "document_id": "Document ID",
            "holder_name": "Holder Name",
            "document_holder": "Document Holder",
            "customer_name": "Customer Name",
            "aadhaar_numbers": "Aadhaar Number(s)",
            "pan_numbers": "PAN Number(s)",
            "gst_numbers": "GST Number(s)",
            "cin_numbers": "CIN Number(s)",
            "mobile_number": "Mobile Number",
            "expiry_date": "Expiry Date",
            "expires_on": "Expiry Date",
            "issued_on": "Issued On",
            "document_url": "Document URL",
        }

    def initUI(self):
        self.setWindowTitle("Veriquick™️ - Scanner")
        self.setWindowIcon(QIcon(app_icon))
        self.setMinimumSize(1000, 600)
        # Dark theme for entire application
        self.setStyleSheet("background-color: #0f0f14;")

        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Camera view (left)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(600, 500)
        self.image_label.setStyleSheet("background: #1a1a1f; border-radius: 18px; margin: 20px;")
        main_layout.addWidget(self.image_label, 2)

        # Details panel (right, scrollable)
        self.details_panel = QScrollArea()
        self.details_panel.setWidgetResizable(True)
        self.details_panel.setMinimumWidth(400)
        self.details_panel.setStyleSheet('''
            QScrollArea { background: #1a1a1f; border-radius: 18px; margin: 20px; border: none; }
        ''')
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_layout.setAlignment(Qt.AlignTop)
        self.details_layout.setSpacing(20)
        self.details_layout.setContentsMargins(20, 20, 20, 20)
        self.details_widget.setLayout(self.details_layout)
        self.details_panel.setWidget(self.details_widget)
        self.details_panel.hide()  # Hide until scan
        main_layout.addWidget(self.details_panel, 1)

        # Main vertical layout (for status bar)
        outer_layout = QVBoxLayout()
        outer_layout.addLayout(main_layout)

        # Status bar at the bottom
        self.status_label = QLabel("Ready to scan QR codes")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.status_label.setStyleSheet("background: rgba(28, 31, 43, 0.8); color: #ff7043; padding: 8px; border-radius: 8px; margin: 8px 32px 8px 32px;")
        outer_layout.addWidget(self.status_label)

        # Reset button below status bar
        self.reset_button = QPushButton("Reset for Next Scan")
        self.reset_button.setStyleSheet('''
            QPushButton { background: #43a047; color: #fff; border-radius: 8px; padding: 10px 24px; font-size: 15px; margin-bottom: 16px; }
            QPushButton:hover { background: #388e3c; }
        ''')
        self.reset_button.clicked.connect(self.reset_for_next_scan)
        outer_layout.addWidget(self.reset_button, alignment=Qt.AlignCenter)

        self.setLayout(outer_layout)

    def initialize_camera(self):
        """Initialize the camera with error handling."""
        try:
            # Try DirectShow first for better performance on Windows
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                raise Exception("Unable to access camera please allow access to camera")
                
            # Set camera properties for optimal QR scanning
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
            
            # Verify camera is working
            ret, _ = self.cap.read()
            if not ret:
                raise Exception("Camera is not returning frames. Check your camera")
                
            self.status_label.setText("Camera initialized successfully")
            
        except Exception as e:
            self.status_label.setText(f"Camera error: {str(e)}")
            print(f"Camera initialization error: {e}")
            
            # Try fallback to default camera
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Unable to access any camera.")
                self.status_label.setText("Camera initialized with fallback settings")
            except Exception as e2:
                self.status_label.setText("Camera error: Unable to access camera")
                QMessageBox.critical(self, "Camera Error", 
                                    "Unable to access the camera. Please check the camera connection or settings.")
                print(f"Fallback camera error: {e2}")

    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            self.status_label.setText("Camera is not available")
            return

        success, frame = self.cap.read()
        if not success:
            self.status_label.setText("Error reading QR")
            return

        current_time = time.time()

        # --- Preprocessing for complex QR codes ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Adaptive thresholding for better binarization
        processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
        # Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        processed = clahe.apply(processed)
        # Use processed image for decoding
        decoded_objs = pyzbar.decode(processed, symbols=[ZBarSymbol.QRCODE])
        if decoded_objs:
            # Only process the first detected QR code per frame
            obj = decoded_objs[0]
            data = obj.data.decode('utf-8')
            x, y, w, h = obj.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(frame, "QR Code Detected", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            if (not self.browser_opened and 
                (self.qr_data is None or self.qr_data != data) and
                current_time - self.last_scan_time >= self.scan_cooldown):  # Use the scan_cooldown variable
                self.qr_data = data
                self.last_scan_time = current_time
                self.status_label.setText("Processing QR code...")
                QTimer.singleShot(0, lambda: self.process_qr_code(data))
        else:
            self.qr_data = None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def process_qr_code(self, qr_data):
        try:
            document_metadata = self.process_qr_data(qr_data)
            if document_metadata:
                self.browser_opened = True
                self.sound_queue = []
                files = document_metadata.get("files", [])
                
                # Open document URLs in browser
                aadhaar_found = False
                pan_found = False
                for doc in files:
                    doc_url = doc.get("document_url", "")
                    if doc_url:
                        try:
                            webbrowser.open(doc_url, new=2)
                            print(f"Opening URL: {doc_url}")
                        except Exception as e:
                            print(f"Error opening browser: {e}")
                    
                    # Sound logic
                    doc_type = doc.get("document_type", "Unknown")
                    if not aadhaar_found and doc_type == "Aadhaar" and doc.get("aadhaar_numbers", []):
                        aadhaar_found = True
                    if not pan_found and doc_type == "PAN" and doc.get("pan_numbers", []):
                        pan_found = True
                
                # Populate details panel
                self.populate_details_panel(files, qr_data)
                self.details_panel.show()
                self.status_label.setText("Verification summary ready.")
                
                # Play only one sound per scan
                if aadhaar_found:
                    self.sound_queue.append(AADHAAR_DETECTED_SOUND)
                elif pan_found:
                    self.sound_queue.append(PAN_VERIFICATION_SOUND)
                else:
                    self.sound_queue.append(MANUAL_VERIFICATION_SOUND)
                self.process_sound_queue()
            else:
                # Show error in details panel
                self.clear_layout(self.details_layout)
                error_card = QFrame()
                error_card.setStyleSheet('''
                    QFrame { background: rgba(255, 152, 0, 0.15); border-radius: 16px; 
                    border: 1px solid rgba(255, 152, 0, 0.3); }
                ''')
                error_layout = QVBoxLayout()
                error_layout.setContentsMargins(20, 18, 20, 18)
                error_title = QLabel("<b>Unsupported QR Code Format</b>")
                error_title.setFont(QFont("Arial", 14, QFont.Bold))
                error_title.setStyleSheet("color: #ff9800;")
                error_layout.addWidget(error_title)
                error_msg = QLabel("This QR code is not supported by Veriquick.")
                error_msg.setFont(QFont("Arial", 11))
                error_msg.setStyleSheet("color: #b0bec5; margin-top: 8px;")
                error_layout.addWidget(error_msg)
                raw_data_box = QLabel(f"<pre style='font-size:10px; color:#cfd8dc;'>{qr_data[:200]}...</pre>")
                raw_data_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
                raw_data_box.setStyleSheet("background: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px; margin-top: 12px;")
                error_layout.addWidget(raw_data_box)
                error_card.setLayout(error_layout)
                self.details_layout.addWidget(error_card)
                self.details_panel.show()
                self.status_label.setText("Unsupported QR code scanned.")
                self.sound_queue = [ERROR_SCANNING]
                self.process_sound_queue()
                QTimer.singleShot(2000, self.reset_for_next_scan)
        except Exception as e:
            self.status_label.setText(f"Error processing QR code: {str(e)}")
            print(f"Error processing QR code: {e}")
            self.sound_queue = [ERROR_SCANNING]
            self.process_sound_queue()
            QTimer.singleShot(1500, lambda: self.status_label.setText("Scanner Ready"))

    def populate_details_panel(self, files, qr_data):
        """Populate the right-side details panel with verification information."""
        self.clear_layout(self.details_layout)
        
        if not files:
            return
        
        primary_doc = files[0]
        
        # Logo at the top
        logo_container = QFrame()
        logo_container.setStyleSheet("QFrame { background: transparent; }")
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.addStretch()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH)
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(120, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("VeriQuick")
            logo_label.setFont(QFont("Arial", 16, QFont.Bold))
            logo_label.setStyleSheet("color: #ffffff;")
        logo_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        logo_layout.addWidget(logo_label)
        logo_container.setLayout(logo_layout)
        self.details_layout.addWidget(logo_container)
        
        # Add spacing after logo
        spacer = QWidget()
        spacer.setFixedHeight(20)
        self.details_layout.addWidget(spacer)
        
        # Header with QR code
        header_card = QFrame()
        header_card.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #3730a3, stop:1 #5b21b6); border-radius: 16px; }"
        )
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(30, 30, 30, 30)
        header_layout.setSpacing(20)
        
        # Document summary
        doc_type = primary_doc.get("document_type", "Document")
        holder = (primary_doc.get("holder_name") or primary_doc.get("document_holder")
                  or primary_doc.get("customer_name") or "")
        summary_text = f"<b style='font-size:24px;'>{doc_type}</b>"
        if holder:
            summary_text += f"<br/><span style='font-size:16px; opacity:0.9;'>{holder}</span>"
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("color: #ffffff;")
        summary_label.setTextFormat(Qt.RichText)
        header_layout.addWidget(summary_label)
        
        # QR code
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setFixedSize(180, 180)
        pixmap = self.generate_qr_pixmap(qr_data)
        if pixmap:
            scaled = pixmap.scaled(qr_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            qr_label.setPixmap(scaled)
            qr_label.setStyleSheet(
                "background: rgba(255, 255, 255, 0.1); border-radius: 12px;"
            )
        else:
            qr_label.setText("QR")
            qr_label.setStyleSheet(
                "background: rgba(255, 255, 255, 0.1); border-radius: 12px;"
                "color: rgba(255,255,255,0.5); font-size: 12px;"
            )
        header_layout.addWidget(qr_label, alignment=Qt.AlignCenter)
        
        # Primary details
        details_lines = []
        file_name = primary_doc.get("file_name", "")
        if file_name:
            details_lines.append(f"Document: <span style='color:#ff7043;'>{file_name}</span>")
        key_options = ["document_number", "aadhaar_numbers", "pan_numbers", "gst_numbers", "cin_numbers"]
        for key in key_options:
            value = primary_doc.get(key)
            if value:
                formatted = self.format_detail_value(value)
                details_lines.append(f"ID: <span style='color:#ff7043;'>{formatted}</span>")
                break
        expiry = primary_doc.get("expiry_date") or primary_doc.get("expires_on")
        if expiry:
            details_lines.append(f"Valid till <span style='color:#ff7043;'>{expiry}</span>")
        issued = primary_doc.get("issued_on")
        if issued:
            details_lines.append(f"Issued on <span style='color:#ff7043;'>{issued}</span>")
        
        if details_lines:
            primary_details = QLabel("<br/>".join(details_lines))
            primary_details.setWordWrap(True)
            primary_details.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 15px;")
            primary_details.setTextFormat(Qt.RichText)
            header_layout.addWidget(primary_details)
        
        header_card.setLayout(header_layout)
        self.details_layout.addWidget(header_card)
        
        # Document detail cards
        for index, doc in enumerate(files):
            card = self.build_detail_card(doc, index)
            self.details_layout.addWidget(card)
        
        self.details_layout.addStretch()
    
    def build_detail_card(self, doc, index):
        """Build a detail card for a document."""
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: rgba(28, 31, 43, 0.8); border-radius: 14px;"
            "border: 1px solid rgba(255,255,255,0.06); }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        
        title = QLabel(doc.get("file_name") or f"Document {index + 1}")
        title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        layout.addWidget(title)
        
        subtitle = QLabel(doc.get("document_type", "Unknown"))
        subtitle.setStyleSheet("color: #8b90a7; font-size: 14px;")
        layout.addWidget(subtitle)
        
        # Add document details
        for key, label in self.DETAIL_LABELS.items():
            if key not in doc or key in ["file_name", "document_type"]:
                continue
            value = doc[key]
            if not value:
                continue
            formatted_value = self.format_detail_value(value)
            if not formatted_value:
                continue
            detail_label = QLabel(
                f"<span style='color:#6b7280; font-size:13px;'>{label}</span><br/>"
                f"<span style='color:#ff7043; font-size:14px;'>{formatted_value}</span>"
            )
            detail_label.setTextFormat(Qt.RichText)
            detail_label.setWordWrap(True)
            layout.addWidget(detail_label)
        
        return card
    
    @staticmethod
    def format_detail_value(value):
        """Format a detail value for display."""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value if v)
        if isinstance(value, dict):
            parts = []
            for k, v in value.items():
                if v:
                    parts.append(f"{k}: {v}")
            return ", ".join(parts)
        return str(value)
    
    def generate_qr_pixmap(self, qr_data):
        """Generate QR code pixmap from data."""
        if not qr_data or qrcode is None:
            return None
        try:
            qr_img = qrcode.make(qr_data)
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), "PNG")
            return pixmap
        except Exception as exc:
            print(f"QR generation failed: {exc}")
            return None

    def process_qr_data(self, qr_data):
        """Parse and validate QR code data."""
        try:
            data = json.loads(qr_data)
            
            # Validate the expected structure
            if not isinstance(data, dict) or "files" not in data:
                print("Invalid QR data format: missing 'files' key")
                return None
                
            if not isinstance(data["files"], list) or len(data["files"]) == 0:
                print("Invalid QR data format: 'files' is empty or not a list")
                return None
                
            return data
            
        except json.JSONDecodeError as e:
            print(f"Error decoding QR data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing QR data: {e}")
            return None

    def process_sound_queue(self):
        """Process the sound queue to play sounds sequentially."""
        if self.is_playing_sound:
            # Check if current sound is finished
            if not pygame.mixer.music.get_busy():
                self.is_playing_sound = False
                self.current_sound = None
            else:
                return  # Still playing current sound
        
        # Play next sound in queue if available
        if self.sound_queue and not self.is_playing_sound:
            sound_path = self.sound_queue.pop(0)
            self.play_sound(sound_path)

    def play_sound(self, sound_path):
        """Play sound at specified path with error handling."""
        try:
            pygame.mixer.music.stop()  # Stop any previous sound
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            self.is_playing_sound = True
            self.current_sound = sound_path
            print(f"Playing sound: {sound_path}")
        except pygame.error as e:
            print(f"Error playing sound {sound_path}: {e}")
            self.is_playing_sound = False
            self.current_sound = None

    def queue_ready_sound(self, prioritize=False):
        """Ensure the EDV ready sound plays when the scanner becomes idle."""
        if not self.ready_sound_path:
            self.ready_sound_path = next((path for path in READY_SOUND_CANDIDATES if os.path.exists(path)), None)
            if not self.ready_sound_path:
                return
        if self.current_sound == self.ready_sound_path:
            return
        if self.ready_sound_path in self.sound_queue:
            return
        if prioritize:
            self.sound_queue.insert(0, self.ready_sound_path)
        else:
            self.sound_queue.append(self.ready_sound_path)
        self.process_sound_queue()

    def copy_link_to_clipboard(self):
        if self.last_result:
            QApplication.clipboard().setText(self.last_result)
            self.status_label.setText("Link copied to clipboard!")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready to scan QR codes"))

    def reset_for_next_scan(self):
        self.qr_data = None
        self.browser_opened = False
        self.details_panel.hide()
        self.clear_layout(self.details_layout)
        self.last_result = None
        self.status_label.setText("Ready to scan QR codes")
        self.queue_ready_sound()
        print("Scanner reset, ready for next scan")

    def closeEvent(self, event):
        """Clean up resources when the application is closed."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = IntroSplash(SPLASH_LOGO_PATH)
    scanner = QRScannerApp()

    def launch_scanner():
        splash.close()
        scanner.show()
        scanner.status_label.setText("Ready to scan QR codes")
        scanner.queue_ready_sound(prioritize=True)

    splash.finished.connect(launch_scanner)
    splash.start()

    sys.exit(app.exec_())

