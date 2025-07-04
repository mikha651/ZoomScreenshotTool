# 📸 ZoomScreenshotTool

![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green)
![License](https://img.shields.io/badge/License-MIT-blue)
![Version](https://img.shields.io/badge/Version-1.0-yellow)

> **ZoomScreenshotTool** is a QGIS plugin that automatically zooms to each feature in a vector layer, highlights it, and exports a high-quality map screenshot named after an attribute value.

---

## ✨ Features

✅ Zooms to each feature with customizable margin (default 30%)  
✅ Draws a visible red outline around the selected feature  
✅ Exports screenshots as PNG images  
✅ Waits intelligently for map rendering to finish (no white screenshots)  
✅ Works at the size of your current QGIS canvas window  
✅ Allows you to cancel the process any time  
✅ Fast and efficient — no unnecessary delays

---

## 🛠 Usage

1. Load your vector layer into QGIS.
2. Click **📸 Zoom Screenshot Tool** in the toolbar or Plugins menu.
3. Follow the prompts:
  - Choose the layer.
  - Choose the attribute field to use as image filenames.
  - Select an output folder.
4. Sit back and let the plugin:
  - Zoom to each feature.
  - Highlight it with a red outline.
  - Save a screenshot as `{attribute_value}.png`.

You can **cancel the process at any time** using the Cancel button in the progress dialog.

---

Made with ❤️ by **mikha651**
