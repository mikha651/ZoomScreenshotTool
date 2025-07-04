from qgis.PyQt.QtCore import QCoreApplication, QSize, QEventLoop, QTimer
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QInputDialog, QApplication, QProgressDialog
from qgis.PyQt.QtGui import QImage, QPainter, QColor
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsProject,
    QgsSymbol,
    QgsSimpleFillSymbolLayer,
)
from qgis.utils import iface
import os

class ZoomScreenshotTool:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.loop = None

    def initGui(self):
        # Emoji action, no external icon needed
        self.action = QAction("📸 Zoom Screenshot Tool", self.iface.mainWindow())
        self.action.triggered.connect(self.run_tool)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Zoom Screenshot Tool", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Zoom Screenshot Tool", self.action)

    def tr(self, message):
        return QCoreApplication.translate("ZoomScreenshotTool", message)

    def run_tool(self):
        layers = [lyr for lyr in self.iface.mapCanvas().layers() if lyr.type() == lyr.VectorLayer]
        if not layers:
            QMessageBox.warning(None, "Zoom Screenshot Tool", "No vector layers loaded.")
            return

        # Layer selection
        layer_names = [lyr.name() for lyr in layers]
        layer_idx, ok = QInputDialog.getItem(None, "Select Layer", "Choose vector layer:", layer_names, 0, False)
        if not ok:
            return

        layer = layers[layer_names.index(layer_idx)]

        # Field selection
        fields = [f.name() for f in layer.fields()]
        if not fields:
            QMessageBox.warning(None, "Zoom Screenshot Tool", "Layer has no fields.")
            return

        field_name, ok = QInputDialog.getItem(None, "Select Field", "Choose attribute field for filenames:", fields, 0, False)
        if not ok:
            return

        # Folder selection
        output_folder = QFileDialog.getExistingDirectory(None, "Select Output Folder")
        if not output_folder:
            return

        canvas = self.iface.mapCanvas()

        # Get current canvas size
        canvas_size = canvas.size()

        # Initial wait
        QMessageBox.information(None, "Zoom Screenshot Tool", "Starting screenshots in 3 seconds...")
        loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()

        feature_count = layer.featureCount()

        progress = QProgressDialog("Processing features...", "Cancel", 0, feature_count, self.iface.mainWindow())
        progress.setWindowTitle("Zoom Screenshot Tool")
        progress.setMinimumDuration(0)
        progress.show()

        count = 0

        for idx, feature in enumerate(layer.getFeatures()):
            progress.setValue(idx)
            QApplication.processEvents()

            if progress.wasCanceled():
                QMessageBox.information(None, "Zoom Screenshot Tool", "Operation canceled by user.")
                break

            attr_value = feature[field_name]
            if attr_value is None:
                attr_value = f"feature_{feature.id()}"
            filename = f"{str(attr_value)}.png"
            output_path = os.path.join(output_folder, filename)

            geom = feature.geometry()
            if geom is None:
                continue

            extent = geom.boundingBox()
            extent.scale(1.3)  # zoom out 30%

            # Create highlight layer
            highlight_layer = self.create_highlight_layer(geom, layer.crs())
            QgsProject.instance().addMapLayer(highlight_layer)

            # Connect renderComplete to know when canvas is ready
            canvas.setExtent(extent)

            self.loop = QEventLoop()
            canvas.renderComplete.connect(self.on_render_complete)
            canvas.refresh()
            self.loop.exec_()  # wait for rendering to complete

            # Capture
            img = QImage(canvas_size, QImage.Format_ARGB32_Premultiplied)
            img.fill(0xFFFFFFFF)

            painter = QPainter(img)
            canvas.render(painter)
            painter.end()

            img.save(output_path, "PNG")
            count += 1

            # Remove highlight layer
            QgsProject.instance().removeMapLayer(highlight_layer)

        progress.close()

        if not progress.wasCanceled():
            QMessageBox.information(None, "Zoom Screenshot Tool", f"Done. Saved {count} images to:\n{output_folder}")

    def on_render_complete(self, painter):
        """
        Slot called when rendering completes.
        """
        if self.loop:
            self.loop.quit()

    def create_highlight_layer(self, geom, crs):
        """
        Create a memory layer containing the current feature to highlight it.
        """
        highlight_layer = QgsVectorLayer("Polygon?crs={}".format(crs.authid()), "highlight", "memory")
        highlight_layer.startEditing()
        f = QgsFeature()
        f.setGeometry(geom)
        highlight_layer.dataProvider().addFeature(f)
        highlight_layer.commitChanges()

        # Create outline-only symbol
        symbol = QgsSymbol.defaultSymbol(highlight_layer.geometryType())
        if symbol is not None:
            symbol.deleteSymbolLayer(0)
            symbol_layer = QgsSimpleFillSymbolLayer(
                color=QColor(0, 0, 0, 0),          # fully transparent fill
                strokeColor=QColor(255, 0, 0),    # red outline
                strokeWidth=0.8
            )
            symbol.appendSymbolLayer(symbol_layer)
            highlight_layer.renderer().setSymbol(symbol)

        return highlight_layer
