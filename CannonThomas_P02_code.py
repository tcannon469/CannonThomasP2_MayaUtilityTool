# Thomas Cannon Project 2: Maya Utility Tool
#    Maya Scatter Tool for Artists: To easily populate a scene with objects and assets

# Call from the Script Editor in Maya!
#    import CannonThomas_P02_code
#    CannonThomas_P02_code.show()

import math  # Math Operations
import random # For random properties
import maya.cmds as cmds 

from maya import OpenMayaUI as omui 

try:
    from shiboken2 import wrapInstance  
except ImportError:
    from shiboken6 import wrapInstance

try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
 
WINDOW_OBJECT_NAME = "ScatterTool"
WINDOW_TITLE = "Scatter Tool for Maya"
ROOT_GROUP_NAME = "ScatterTool_grp"

def delete_existing_window(object_name: str = WINDOW_OBJECT_NAME) -> None:
    """Delete an existing Maya UI window with the same object name."""
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == object_name:
            widget.close()
            widget.deleteLater()

#  Main UI window and the heart of the program
class ScatterToolUI(QtWidgets.QDialog):
     
    # Object constructor // initialization of the Scatter UI
     
    def __init__(self, parent=None):
        super().__init__(parent or maya_main_window())
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle("Scatter Tool")
        self.setMinimumWidth(460)
        self.setMinimumHeight(1250)

        #self.logic = ScatterToolLogic()
        self.source_rows = [] # a table that host the objects to scatter
        self._build_ui()
        self._connect_signals()

    #  Creation of the UI elements // NO FUNCTIONALITY
     
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Scatter Tool")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        main_layout.addWidget(title)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Defining the UI sections

        self.target_section()
        self.source_section()
        self.distribution_section()
        self.randomization_section()
        self.alignment_section()
        self.advanced_section()

        # Creating the acting buttons at the bottom of the UI

        button_layout = QtWidgets.QHBoxLayout()
        self.scatter_btn = QtWidgets.QPushButton("SCATTER")
        self.update_btn = QtWidgets.QPushButton("UPDATE")
        self.clear_btn = QtWidgets.QPushButton("CLEAR")
        self.bake_btn = QtWidgets.QPushButton("BAKE")

        self.scatter_btn.setMinimumHeight(34)
        self.scatter_btn.setStyleSheet("font-weight: bold;")

        # Placing the acting buttons at the bottom of the UI

        button_layout.addWidget(self.scatter_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.bake_btn)

        main_layout.addLayout(button_layout)

    # Creating the Target Section (1) and its layout

    def target_section(self):
        box = QtWidgets.QGroupBox("1. Target Surface")
        layout = QtWidgets.QGridLayout(box)

        self.target_field = QtWidgets.QLineEdit()
        self.target_field.setPlaceholderText("Select a mesh and click Load Selected")
        self.load_target_btn = QtWidgets.QPushButton("Load Selected")
        self.target_status = QtWidgets.QLabel("No mesh loaded")

        layout.addWidget(QtWidgets.QLabel("Target Mesh"), 0, 0) 
        layout.addWidget(self.target_field, 0, 1)
        layout.addWidget(self.load_target_btn, 0, 2)
        layout.addWidget(self.target_status, 1, 1, 1, 2)

        self.content_layout.addWidget(box)

    # Creating the Source Section (2) as a Table // Buttons implemented after Table

    def source_section(self):
        box = QtWidgets.QGroupBox("2. Source Objects")
        layout = QtWidgets.QVBoxLayout(box)

        self.source_table = QtWidgets.QTableWidget(0, 2)
        self.source_table.setHorizontalHeaderLabels(["Object", "Weight"])
        self.source_table.horizontalHeader().setStretchLastSection(True)
        self.source_table.setMinimumHeight(130)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_source_btn = QtWidgets.QPushButton("Add Selected")
        self.remove_source_btn = QtWidgets.QPushButton("Remove")
        self.clear_source_btn = QtWidgets.QPushButton("Clear All")
        btn_layout.addWidget(self.add_source_btn)
        btn_layout.addWidget(self.remove_source_btn)
        btn_layout.addWidget(self.clear_source_btn)

        layout.addWidget(self.source_table)
        layout.addLayout(btn_layout)

        self.content_layout.addWidget(box)

    # Creating the Distribution Modes (3) 

    def distribution_section(self):
        box = QtWidgets.QGroupBox("3. Distribution Settings")
        layout = QtWidgets.QFormLayout(box)

        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Whole Mesh", "Selected Faces", "Vertex Based", "Curve Guided"])

        self.count_spin = QtWidgets.QSpinBox()
        self.count_spin.setRange(1, 10000)
        self.count_spin.setValue(50)

        self.spacing_spin = QtWidgets.QDoubleSpinBox()
        self.spacing_spin.setRange(0.0, 1000.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(0.5)

        self.seed_spin = QtWidgets.QSpinBox()
        self.seed_spin.setRange(0, 999999999)
        self.seed_spin.setValue(12345)

        layout.addRow("Mode", self.mode_combo)
        layout.addRow("Count / Density", self.count_spin)
        layout.addRow("Spacing", self.spacing_spin)
        layout.addRow("Seed", self.seed_spin)

        self.content_layout.addWidget(box)

    # Creating the Randomizaton Section (4)

    def randomization_section(self):
        box = QtWidgets.QGroupBox("4. Randomization")
        layout = QtWidgets.QGridLayout(box)

        self.scale_min = self._double_spin(0.01, 100.0, 0.8)
        self.scale_max = self._double_spin(0.01, 100.0, 1.3)
        self.ry_min = self._double_spin(-360.0, 360.0, 0.0)
        self.ry_max = self._double_spin(-360.0, 360.0, 360.0)
        self.tx_min = self._double_spin(-90.0, 90.0, -5.0)
        self.tx_max = self._double_spin(-90.0, 90.0, 5.0)
        self.tz_min = self._double_spin(-90.0, 90.0, -5.0)
        self.tz_max = self._double_spin(-90.0, 90.0, 5.0)

        layout.addWidget(QtWidgets.QLabel("Scale"), 0, 0)
        layout.addWidget(QtWidgets.QLabel("Min"), 0, 1)
        layout.addWidget(self.scale_min, 0, 2)
        layout.addWidget(QtWidgets.QLabel("Max"), 0, 3)
        layout.addWidget(self.scale_max, 0, 4)

        layout.addWidget(QtWidgets.QLabel("Rotate Y"), 1, 0)
        layout.addWidget(QtWidgets.QLabel("Min"), 1, 1)
        layout.addWidget(self.ry_min, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Max"), 1, 3)
        layout.addWidget(self.ry_max, 1, 4)

        layout.addWidget(QtWidgets.QLabel("Tilt X"), 2, 0)
        layout.addWidget(QtWidgets.QLabel("Min"), 2, 1)
        layout.addWidget(self.tx_min, 2, 2)
        layout.addWidget(QtWidgets.QLabel("Max"), 2, 3)
        layout.addWidget(self.tx_max, 2, 4)

        layout.addWidget(QtWidgets.QLabel("Tilt Z"), 3, 0)
        layout.addWidget(QtWidgets.QLabel("Min"), 3, 1)
        layout.addWidget(self.tz_min, 3, 2)
        layout.addWidget(QtWidgets.QLabel("Max"), 3, 3)
        layout.addWidget(self.tz_max, 3, 4)

        self.content_layout.addWidget(box)

    # Creating the Alignment Section (5)

    def alignment_section(self):
        box = QtWidgets.QGroupBox("5. Surface Alignment")
        layout = QtWidgets.QVBoxLayout(box)

        self.align_normals_cb = QtWidgets.QCheckBox("Align to Surface Normals")
        self.random_up_cb = QtWidgets.QCheckBox("Random Up Vector")
        self.random_up_cb.setEnabled(False)
        self.max_slope_spin = self._double_spin(0.0, 90.0, 45.0)
        self.max_slope_spin.setEnabled(False)

        layout.addWidget(self.align_normals_cb)
        layout.addWidget(self.random_up_cb)
        layout.addWidget(QtWidgets.QLabel("Max Slope placeholder - not active yet"))
        layout.addWidget(self.max_slope_spin)

        self.content_layout.addWidget(box)

    # Creating the Advanced Section (6) 

    def advanced_section(self):
        box = QtWidgets.QGroupBox("6. Advanced")
        layout = QtWidgets.QFormLayout(box)

        self.instance_cb = QtWidgets.QCheckBox("Use Instancing")
        self.instance_cb.setChecked(True)
        self.group_cb = QtWidgets.QCheckBox("Group Results")
        self.group_cb.setChecked(True)
        self.live_preview_cb = QtWidgets.QCheckBox("Live Preview")
        self.live_preview_cb.setEnabled(False)

        self.group_name_field = QtWidgets.QLineEdit("Scatter_Grp")

        layout.addRow(self.instance_cb)
        layout.addRow(self.group_cb)
        layout.addRow(self.live_preview_cb)
        layout.addRow("Group Name", self.group_name_field)

        self.content_layout.addWidget(box)

    # Connects UI buttons to functions

    def _connect_signals(self):
        self.load_target_btn.clicked.connect(self.load_selected_target)
        self.add_source_btn.clicked.connect(self.add_selected_sources)
        self.remove_source_btn.clicked.connect(self.remove_selected_source_rows)
        self.clear_source_btn.clicked.connect(lambda: self.source_table.setRowCount(0))
        self.scatter_btn.clicked.connect(self.run_scatter)
        self.update_btn.clicked.connect(self.run_scatter)

    #   self.clear_btn.clicked.connect(self.logic.clear_last_scatter)
        self.bake_btn.clicked.connect(self.bake_instances)

    # Reusable code to handle Double Spin Boxes

    def _double_spin(self, min_value, max_value, value):
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(min_value, max_value)
        spin.setDecimals(3)
        spin.setSingleStep(0.1)
        spin.setValue(value)
        return spin
     
    # Load the selected mesh from Maya into the UI

    def load_selected_target(self):
        mesh = get_first_selected_mesh()
        if not mesh:
            cmds.warning("Select a polygon mesh first.")
            self.target_status.setText("Invalid selection")
            return
        self.target_field.setText(mesh)
        self.target_status.setText("Valid mesh")
     
    # Loads the selected sources (mesh objects) if not loaded yet // Objects from Maya interface into the UI

    def add_selected_sources(self):
        selected = get_selected_transforms()
        target = self.target_field.text().strip()
        existing = self._get_source_objects()

        for obj in selected:
            if obj == target or obj in existing:
                continue
            row = self.source_table.rowCount()
            self.source_table.insertRow(row)
            self.source_table.setItem(row, 0, QtWidgets.QTableWidgetItem(obj))
            self.source_table.setItem(row, 1, QtWidgets.QTableWidgetItem("1"))
     
    # Removes the selected rows from the source-object table
     
    def remove_selected_source_rows(self):
        rows = sorted({index.row() for index in self.source_table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.source_table.removeRow(row)
     
    # Get the source objects (from the table) into a list

    def _get_source_objects(self):
        objects = []
        for row in range(self.source_table.rowCount()):
            item = self.source_table.item(row, 0)
            if item:
                objects.append(item.text())
        return objects

    # Get the source objects weights (from the table) into a list

    def _get_source_weights(self):
        weights = []
        for row in range(self.source_table.rowCount()):
            item = self.source_table.item(row, 1)
            try:
                weights.append(float(item.text()))
            except Exception:
                weights.append(1.0)
        return weights

    # Gathers all the values from the UI and packages them into one clean settings object

    def collect_settings(self):
        target = self.target_field.text().strip()
        if not is_valid_mesh_transform(target):
            raise ValueError("Please load a valid target mesh.")

        return ScatterSettings(
            target_mesh=target,
            source_objects=self._get_source_objects(),
            source_weights=self._get_source_weights(),
            count=self.count_spin.value(),
            min_spacing=self.spacing_spin.value(),
            seed=self.seed_spin.value(),
            scale_min=self.scale_min.value(),
            scale_max=self.scale_max.value(),
            rotate_y_min=self.ry_min.value(),
            rotate_y_max=self.ry_max.value(),
            tilt_x_min=self.tx_min.value(),
            tilt_x_max=self.tx_max.value(),
            tilt_z_min=self.tz_min.value(),
            tilt_z_max=self.tz_max.value(),
            align_to_normals=self.align_normals_cb.isChecked(),
            use_instances=self.instance_cb.isChecked(),
            group_results=self.group_cb.isChecked(),
            group_name=self.group_name_field.text().strip() or "Scatter_Grp",
        )

    # Execute the Scatter function on the target mesh

    def run_scatter(self):
        try:
            settings = self.collect_settings()
            created = self.logic.scatter(settings)
            cmds.inViewMessage(
                amg=f"Scatter: created <hl>{len(created)}</hl> objects.",
                pos="midCenter",
                fade=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))
            print(traceback.format_exc())

    # Convert the procedural scatter result into normal permanent Maya objects

    def bake_instances(self):
        """Placeholder: instances are already scene nodes; this is a future expansion point."""
        cmds.inViewMessage(amg="Bake placeholder: add conversion/export logic later.", pos="midCenter", fade=True)

def show_window():
    delete_existing_window()
    window = ScatterToolUI()
    window.show()
    return window
