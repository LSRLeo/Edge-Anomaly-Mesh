Team 2: Motion Classification & Anomaly Detection

Goal: Process raw sensor data in real-time, classify motion types, and detect anomalies using machine learning.

To Build:

Data Listener - Subscribe to all sensor:raw:* channels, handle multiple nodes
Windowing - Buffer 2-5 second windows of raw data
Feature Extraction - Compute RMS, peaks, variance, FFT features (15-20 dimensions)
Motion Classifier - Use TensorFlow Lite model to classify into 4 motion typesAnomaly DetectorK-means clustering to identify unusual patternsREDIS PublisherPublish classification + anomaly results

REDIS channel inference:results:{node_id} receives messages like:
json{
  "node_id": "node_001",
  "timestamp": 1702656000.123456,
  "window_start": 1702655998.123456,
  "window_end": 1702656000.123456,
  "motion_class": "IDLE",
  "motion_confidence": 0.95,
  "anomaly_flag": false,
  "anomaly_score": 0.12,
  "feature_vector": [0.05, 0.02, 9.81, ...],
  "processing_time_ms": 45
}

Key Constraints:
motion_class must be one of: IDLE, TERRESTRIAL, MARITIME, LIFT, UNKNOWN
anomaly_score must be in [0, 1]
Handle out-of-order messages gracefully

---

# ML Module — Sprint 1 Summary

**Team 2: Motion Classification & Anomaly Detection**

This document describes everything completed during `ml-team-sprint-1`.

---

## Sprint 1 Goals

Build the offline training pipeline for a motion classifier that can:
- Ingest raw IoT sensor data (accelerometer + gyroscope at 50 Hz)
- Segment continuous streams into fixed-size windows
- Extract meaningful features from each window
- Train a neural network to classify motion type and detect anomalies
- Produce a trained model artifact ready for inference

---

## Deliverables Completed

### 1. JSON Data Loader — `data_pipeline.py: load_json_data()`

Loads raw sensor recordings from the node-simulator's JSON output format.

- Accepts both single-object and list-of-objects JSON files
- Handles dual key names (`accel_mss` / `accel`, `gyro_rads` / `gyro`) for compatibility with simulator versions
- Sorts events by `seq` field when present to guard against out-of-order records
- Parses `meta.sim_mode` and `meta.sim_anomaly` to produce **combined labels (0–7)**:

| Label | Meaning |
|-------|---------|
| 0 | IDLE |
| 1 | TERRESTRIAL |
| 2 | MARITIME |
| 3 | LIFT |
| 4 | IDLE + anomaly |
| 5 | TERRESTRIAL + anomaly |
| 6 | MARITIME + anomaly |
| 7 | LIFT + anomaly |

---

### 2. Sliding Window Segmentation — `data_pipeline.py: create_windows()`

Converts continuous sensor streams into fixed-size windows suitable for ML input.

- Input: dict of 6 sensor axes as 1D numpy arrays
- Output: `(n_windows, window_size, 6)` array
- Configurable `window_size` (default 100 samples = 2 s at 50 Hz) and `overlap` (default 0.5 = 50%)
- **Majority-label assignment**: each window is labeled with the most common label within its sample range, handling motion transitions gracefully
- Step size formula: `step = int(window_size * (1 - overlap))`

---

### 3. Feature Extraction — `feature_extraction.py`

`FeatureExtractor` converts each `(window_size, 6)` window into a **20-dimensional feature vector**.

#### Feature categories

**Time-domain** (5 features × 6 axes):

| Feature | Description |
|---------|-------------|
| `mean` | Average value; accel_z ≈ 9.81 for IDLE (gravity) |
| `std` | Standard deviation; low for IDLE, high for MARITIME |
| `rms` | Root mean square — signal energy including DC component |
| `peak_to_peak` | `max − min`; large Z-axis values indicate LIFT |
| `zero_crossings` | Oscillation frequency proxy; high for TERRESTRIAL vibration |

**Frequency-domain** (2 features × 3 accel axes):

| Feature | Description |
|---------|-------------|
| `dominant_freq` | Frequency with peak FFT magnitude (Hz); TERRESTRIAL ≈ 2–5 Hz |
| `spectral_energy` | Sum of squared FFT magnitudes; high for active motion |

DC component is removed before FFT; only positive frequencies are used.

**Cross-axis** (2 features):

| Feature | Description |
|---------|-------------|
| `accel_magnitude_mean` | Mean of `sqrt(ax² + ay² + az²)`; ≈ 9.81 for IDLE |
| `gyro_magnitude_mean` | Mean of `sqrt(gx² + gy² + gz²)`; high for rotating cargo |

**Total: 20 features per window** (`FeatureExtractor.n_features`)

Key methods:
- `extract(window)` → `(20,)` array for a single window
- `extract_batch(windows)` → `(n_windows, 20)` array

---

### 4. Feature Normalization — `feature_extraction.py: normalize_features()`

Applies zero-mean, unit-variance normalization across the feature matrix.

- Computes `mean` and `std` per feature during training
- Returns a `scaler = (mean, std)` tuple for reuse at inference time
- Handles constant features (`std == 0`) safely by substituting `1`

```python
X_normalized, scaler = normalize_features(X_train)
X_test_normalized, _ = normalize_features(X_test, scaler=scaler)
```

---

### 5. Data Pipeline Orchestration — `data_pipeline.py`

End-to-end helpers that wire together loading → windowing → feature extraction:

| Function | Purpose |
|----------|---------|
| `windows_to_features(windows)` | Wraps `FeatureExtractor.extract_batch` |
| `process_file(filepath, ...)` | Single-file: load → window → extract → return `(features, labels)` |
| `save_features(features, labels, path)` | Persists processed data as `.npz` (compressed NumPy archive) |
| `demo(args)` | CLI demo: loads all files in a directory and prints shape/statistics |

CLI usage:
```bash
python ml/data_pipeline.py --data-dir data/generated_data --window-size 100 --overlap 0.5 --save
```

---

### 6. Neural Network Classifier — `train_classifier.py`

#### Model: `MotionClassifier` (MLP)

```
Input (20 features)
     |
Linear (20 -> 64) + ReLU + Dropout(0.3)
     |
Linear (64 -> 32) + ReLU
     |
Linear (32 -> 8)
     |
Output logits -> softmax probabilities
```

8 output classes: `IDLE`, `TERRESTRIAL`, `MARITIME`, `LIFT`, and their anomalous counterparts.

#### Dataset: `MotionDataset`

PyTorch `Dataset` wrapping feature/label numpy arrays as `FloatTensor` / `LongTensor` for use with `DataLoader`.

#### Training functions

| Function | Description |
|----------|-------------|
| `train_epoch()` | One full pass: forward → loss → backward → optimizer step; returns avg loss + accuracy |
| `evaluate()` | Validation/test pass with `model.eval()` and `torch.no_grad()`; returns loss, accuracy, all predictions and labels |
| `compute_confusion_matrix()` | Builds `(8, 8)` count matrix from predictions vs. true labels |
| `print_confusion_matrix()` | Pretty-prints the matrix |
| `print_classification_report()` | Per-class precision, recall, and F1 score |

#### Label utilities

| Function | Description |
|----------|-------------|
| `encode_combined_label(terrain, has_anomaly)` | `terrain + (4 if anomaly else 0)` |
| `decode_combined_label(label)` | Returns `(terrain_type, has_anomaly)` |
| `extract_terrain_predictions(preds)` | `preds % 4` — terrain only |
| `extract_anomaly_predictions(preds)` | `preds >= 4` — anomaly flag only |
| `compute_separate_accuracies(preds, labels)` | Reports joint, terrain-only, and anomaly-only accuracy |

#### Full training pipeline: `main()`

```
1. Parse CLI args (epochs, batch-size, lr, dropout, hidden-dims, patience, ...)
2. Load all JSON files from --data-dir via load_all_data()
3. Normalize features
4. Split 70% train / 15% val / 15% test
5. Training loop with early stopping (saves best model by val accuracy)
6. Reload best model -> evaluate on test set
7. Export per-sample inference probabilities to JSON (for database team)
8. Save training history (loss/accuracy curves) to JSON
```

```bash
# Train with defaults
python ml/train_classifier.py

# Custom hyperparameters
python ml/train_classifier.py --epochs 200 --batch-size 64 --learning-rate 0.0005 --patience 15

# Specify paths
python ml/train_classifier.py --data-dir data/generated_data --model-output models/motion_classifier.pt
```

Outputs:
- `models/motion_classifier.pt` — saved PyTorch state dict (best val accuracy)
- `models/training_history.json` — epoch-by-epoch loss and accuracy
- `models/inference_results.json` — per-sample probabilities for all 8 classes (database team handoff)

---

### 7. Data Visualization — `visualize_motion_data.py`

Standalone script to visually inspect generated sensor data before training.

| Function | Output |
|----------|--------|
| `plot_single_motion()` | Accel + gyro time series for one motion type |
| `plot_all_motions_comparison()` | Side-by-side grid of all 4 motion types |
| `plot_anomaly_comparison()` | Normal IDLE vs. IDLE with injected shocks |
| `plot_frequency_analysis()` | FFT magnitude spectrum per motion type |
| `compute_basic_stats()` | Per-axis mean/std/min/max summary table |

Plots are saved to `data/plots/` as PNG files.

```bash
python scripts/generate_init_data.py   # generate data first
python ml/visualize_motion_data.py     # then visualize
```

---

### 8. Dependencies — `ml/requirements.txt`

| Package | Purpose |
|---------|---------|
| `numpy` | Array operations, windowing, feature math |
| `scipy` | FFT (`scipy.fft`) |
| `torch` | Neural network training (MLP, DataLoader, Adam) |
| `scikit-learn` | Evaluation utilities |
| `redis` | Redis client (used in sprint 2 ingestion layer) |

---

## File Structure

```
ml/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── feature_extraction.py      # FeatureExtractor class, normalize_features()
├── data_pipeline.py           # load_json_data, create_windows, save_features, demo
├── train_classifier.py        # MotionClassifier, training loop, evaluation metrics
├── visualize_motion_data.py   # Plotting utilities for exploratory data analysis
├── redis_insteam.py           # RedisSubscriber for live ingestion (sprint 2)
└── classifier/
    └── __init__.py
```

---

## Design Decisions

**Combined 8-class output** — Rather than two separate heads (terrain + anomaly), the model uses a single 8-class softmax. This simplifies the training objective and lets `decode_combined_label()` recover both signals from one prediction.

**Majority-label windowing** — Assigning a single label to each window based on the majority of samples within it correctly handles windows that span motion transitions without introducing ambiguous multi-label targets.

**Scaler-first normalization** — The scaler computed on training data is returned and must be saved alongside the model weights. Inference must apply the same `(mean, std)` to avoid distribution shift.

**Early stopping on validation accuracy** — The best checkpoint is saved whenever `val_acc` improves; training stops after `--patience` epochs without improvement to prevent overfitting on the small generated dataset.