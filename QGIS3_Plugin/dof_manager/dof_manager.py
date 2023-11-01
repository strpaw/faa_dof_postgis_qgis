# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigitalObstacleFileManager
                                 A QGIS plugin
 Manage FAA DOF
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-09-17
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Paweł Strzelewicz
        email                : @
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QDate, QRegExp
from qgis.PyQt.QtGui import QIcon, QValidator, QDoubleValidator, QIntValidator, QRegExpValidator
from qgis.PyQt.QtWidgets import QAction, QWidget, QMessageBox, QLineEdit, QMessageBox
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .dof_manager_dialog import DigitalObstacleFileManagerDialog
import os.path
import logging

from .db_utils import DBUtils
from .loging_configuration import configure_logging


LENGTH_OBSTACLE_IDENT = 6

configure_logging(log_dir=os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "logs"
))


class DigitalObstacleFileManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DigitalObstacleFileManager_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FAA_DOF')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.layers = {}
        """Layers required in project"""
        self.data_uri = None
        """Database URI"""

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DigitalObstacleFileManager', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/dof_manager/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'DOF Manager'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FAA_DOF'),
                action)
            self.iface.removeToolBarIcon(action)

    def _is_layer_loaded(self, layer_name: str) -> bool:
        """Check if layer is loaded to QGIS project.
        :param layer_name: layer name to be checked
        :type layer_name: str
        :return: True if only one layer with given name is loaded
        :rtype: bool
        """
        layers = QgsProject.instance().mapLayersByName(layer_name)
        layers_count = len(layers)
        if not layers:
            msg = f"'{layer_name}' layer not found!\nAdd layer."
            QMessageBox.critical(QWidget(), "Message", msg)
            logging.error(msg.replace("\n", " "))
            return False
        elif layers_count > 1:
            msg = f"{layers_count} layers  '{layer_name}' found in Layers.\n"\
                  f"Only one layer '{layer_name}' is allowed!\nRemove unnecessary layers."
            QMessageBox.critical(QWidget(), "Message", msg)
            logging.error(msg.replace("\n", " "))
            return False

        self.layers[layer_name] = layers[0]

        return True

    def _is_postgis_storage(self, layer_name: str) -> bool:
        """Check if layer is 'PostgreSQL database with PostGIS extension' storage type.
        :param layer_name: layer name to be checked
        :type layer_name: str
        :return: True if 'PostgreSQL database with PostGIS extension' is storage type for given layer
        :rtype: bool
        """
        expected_storage = "PostgreSQL database with PostGIS extension"
        provider = self.layers[layer_name].dataProvider()
        actual_storage = provider.storageType()

        if actual_storage != expected_storage:
            msg = f"Current provider type: {actual_storage} for layer '{layer_name}'.\n" \
                  f"Expected provider type: {expected_storage}."
            QMessageBox.critical(QWidget(), "Message", msg)
            logging.error(msg.replace("\n", " "))
            return False

        return True

    def _is_layer_correct(self, layer_name):
        """Check if correct layers is loaded (layer name, storage type)
        :param layer_name: layer name to be checked
        :type layer_name: str
        :return: True if given layer name is loaded and has 'PostgreSQL database with PostGIS extension' storage type
        :rtype: bool
        """
        return self._is_layer_loaded(layer_name) and self._is_postgis_storage(layer_name)

    def _check_loaded_layers(self) -> bool:
        """Check required layers in current QGIS project.
        :return: True if required layers and their storage type are correct
        :rtype: bool
        """
        logging.info("Checking required layers...")
        layers = ["country", "obstacle", "us_state"]
        result = all([self._is_layer_correct(layer) for layer in layers])
        if result:
            logging.info("Check successful.")
        else:
            logging.error("Check failed. Load correct layers and run plugin again.")
        return result

    def _get_data_uri(self):
        obstacle_layer = self.layers["obstacle"]
        provider = obstacle_layer.dataProvider()
        logging.info(provider.dataSourceUri())
        self.data_uri = QgsDataSourceUri(provider.dataSourceUri())
        logging.info(self.data_uri)

    def _fill_in_country_state(self, db: DBUtils) -> None:
        """Fill in Country/state combobox with data from database"""
        fetched_data = db.execute_select("select name, code from dof.states_countries_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxCountryState.addItem(label, data)

    def _fill_in_horizontal_acc(self, db: DBUtils) -> None:
        """Fill in horizontal accuracy combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.horizontal_acc_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxHorAcc.addItem(label, data)

    def _fill_in_vertical_acc(self, db: DBUtils) -> None:
        """Fill in vetical accuracy combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.vertical_acc_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxVertAcc.addItem(label, data)

    def _fill_in_obstacle_type(self, db: DBUtils) -> None:
        """Fill in obstacle type combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.obstacle_type_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxObstacleType.addItem(label, data)

    def _fill_in_marking(self, db: DBUtils) -> None:
        """Fill in marking combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.marking_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxMarking.addItem(label, data)

    def _fill_in_lighting(self, db: DBUtils) -> None:
        """Fill in lighting combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.lighting_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxLighting.addItem(label, data)

    def _fill_in_verif_status(self, db: DBUtils) -> None:
        """Fill in verification status combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.verif_status_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxVerificationStatus.addItem(label, data)

    def _fill_in_action(self, db: DBUtils):
        """Fill in action combobox with data from database"""
        fetched_data = db.execute_select("select * from dof.action_labels;")
        for label, data in fetched_data:
            self.dlg.comboBoxAction.addItem(label, data)

    def _fill_in_comboboxes(self) -> None:
        """Fill in comboboxes such as obstacle type, marking with values from database"""
        db = DBUtils(self.data_uri.host(), self.data_uri.database(), self.data_uri.username(), self.data_uri.password())
        self._fill_in_country_state(db)
        self._fill_in_horizontal_acc(db)
        self._fill_in_vertical_acc(db)
        self._fill_in_obstacle_type(db)
        self._fill_in_marking(db)
        self._fill_in_lighting(db)
        self._fill_in_verif_status(db)
        self._fill_in_action(db)

    def _set_validators(self) -> None:
        """Set validators for line edits when they are required"""
        self.dlg.lineEditObstacleIdent.setValidator(
            QRegExpValidator(QRegExp("\d+"))
        )

        self.dlg.lineEditAgl.setValidator(
            QDoubleValidator(
                bottom=0,
                top=9000,
                decimals=2,
                notation=QDoubleValidator.StandardNotation
            )
        )

        self.dlg.lineEditAmsl.setValidator(
            QDoubleValidator(
                bottom=0,
                top=30000,
                decimals=2,
                notation=QDoubleValidator.StandardNotation
            )
        )

        self.dlg.lineEditQuantity.setValidator(
            QIntValidator(
                bottom=1,
                top=200
            )
        )

    def _set_initial_dates(self) -> None:
        """Set valid from, valid to dates to initial values"""
        current_date = QDate.currentDate()
        self.dlg.dateEditValidFrom.setDate(current_date)
        self.dlg.dateEditValidTo.setDate(current_date.addDays(1))
        self._valid_to = self.dlg.dateEditValidTo.date()

    def _initialize(self) -> None:
        """Initialize plugin GUI settings"""
        self._get_data_uri()
        self._fill_in_comboboxes()
        self._set_validators()
        self._set_initial_dates()

    def _is_obstacle_ident_correct_length(self) -> bool:
        """Check if obstacle ident with required length has been entered"""
        if len(self.dlg.lineEditObstacleIdent.text()) < LENGTH_OBSTACLE_IDENT:
            return False
        return True

    def _change_obstacle_ident_background(self) -> None:
        """Change obstacle ident background to white while editing in case it was red.
        Purpose - to not confuse user (until editing is finished we do not know if obstacle ident length is
        correct or not)"""
        self.dlg.lineEditObstacleIdent.setStyleSheet("background: white;")

    def obstacle_ident_editing_finished(self) -> None:
        """Actions to be done when obstacle ident editing is finished"""
        is_correct_length = self._is_obstacle_ident_correct_length()

        if not is_correct_length:
            QMessageBox.critical(QWidget(), "Message", "Obstacle ident requires 6 digits!")
            self.dlg.lineEditObstacleIdent.setStyleSheet("background: red;")
            return

        self.dlg.lineEditObstacleIdent.setStyleSheet("background: white;")

    @staticmethod
    def __double_validation(item: QLineEdit) -> None:
        """ Validate LineEdit with allowed double values.
        Set background to red in case value is invalid (outside range), white otherwise/
        :param item: item for which validation is executed
        :type item: QLineEdit
        """
        validator = item.validator()
        state = validator.validate(item.text(), 0)[0]

        if state == QValidator.Intermediate:
            text = item.text()
            if text and float(text.replace(",", ".")) > validator.top():
                item.setStyleSheet("background: red;")
            else:
                item.setStyleSheet("background: white;")
        elif state == QValidator.Acceptable:
            item.setStyleSheet("background: white;")

    def agl_edited(self):
        """Check if value entered by user is valid"""
        self.__double_validation(self.dlg.lineEditAgl)

    def amsl_edited(self):
        """Check if value entered by user is valid"""
        self.__double_validation(self.dlg.lineEditAmsl)

    def quantity_edited(self):
        """Check if value entered by user is valid"""
        validator = self.dlg.lineEditQuantity.validator()
        state = validator.validate(self.dlg.lineEditQuantity.text(), 0)[0]

        if state == QValidator.Intermediate:
            text = self.dlg.lineEditQuantity.text()
            if text and int(text) > validator.top():
                self.dlg.lineEditQuantity.setStyleSheet("background: red;")
            else:
                self.dlg.lineEditQuantity.setStyleSheet("background: white;")
        elif state == QValidator.Acceptable:
            self.dlg.lineEditQuantity.setStyleSheet("background: white;")

    def _change_dates_background_color(self) -> None:
        """Set Valid from, Valid to background color to red or white depending on if
        condition is met: valid from <= valid to."""
        if self.dlg.dateEditValidFrom.date() > self.dlg.dateEditValidTo.date():
            self.dlg.dateEditValidFrom.setStyleSheet("background: red;")
            self.dlg.dateEditValidTo.setStyleSheet("background: red;")
        else:
            self.dlg.dateEditValidFrom.setStyleSheet("background: white;")
            self.dlg.dateEditValidTo.setStyleSheet("background: white;")

    def check_valid_from_date(self) -> None:
        """Ensure that valid from date is equal of before valid to date"""
        if self.dlg.dateEditValidFrom.date() > self.dlg.dateEditValidTo.date():
            QMessageBox.critical(QWidget(), "Message", "Valid from date after Valid to date!")
        self._change_dates_background_color()

    def check_valid_to_date(self) -> None:
        """Ensure that valid to date is equal or after valid from date"""
        if self.dlg.dateEditValidTo.date() < self.dlg.dateEditValidFrom.date():
            QMessageBox.critical(QWidget(), "Message", "Valid to date before Valid from date!")
        self._change_dates_background_color()

    def run(self):
        """Run method that performs all the real work"""
        if not self._check_loaded_layers():
            return

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DigitalObstacleFileManagerDialog()

            self._initialize()
            self.dlg.pushButtonCancel.clicked.connect(self.dlg.close)
            self.dlg.lineEditObstacleIdent.editingFinished.connect(self.obstacle_ident_editing_finished)
            self.dlg.lineEditObstacleIdent.textChanged.connect(self._change_obstacle_ident_background)
            self.dlg.lineEditAgl.textChanged.connect(self.agl_edited)
            self.dlg.lineEditAmsl.textChanged.connect(self.amsl_edited)
            self.dlg.lineEditQuantity.textChanged.connect(self.quantity_edited)
            self.dlg.dateEditValidFrom.dateChanged.connect(self.check_valid_from_date)
            self.dlg.dateEditValidTo.dateChanged.connect(self.check_valid_to_date)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()
