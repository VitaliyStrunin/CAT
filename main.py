import pandas as pd
import pyqtgraph as pg
import sys
import datetime
import os
import shutil
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pyqtgraph import DateAxisItem

Form, _ = uic.loadUiType(r"C:\Users\sthap\OneDrive\Рабочий стол\Carbon Analysis Tool (CAT)\MainWindow - untitled.ui")


class CAT(QtWidgets.QMainWindow, Form):

    def __init__(self):
        super(CAT, self).__init__()
        self.setupUi(self)
        self.graphWidget = pg.PlotWidget()
        self.csv_data = pd.DataFrame()
        self.data_loaded = False
        self.root_directory = "c:\\"
        self.data_columns_list.hide()
        self.mainGraph.addWidget(self.graphWidget)
        self.actionDownload_DATA_file.triggered.connect(self.download_DATA_file)
        self.actionDownload_CSV_file.triggered.connect(self.download_csv_file)
        self.actionSelect_root_directory.triggered.connect(self.select_root_directory)
        self.data_columns_list.currentIndexChanged.connect(self.draw_plot)

    def delete_3_sigma(self, column):
        mean_value = self.csv_data[column].mean()
        three_sigma = 3 * self.csv_data[column].std()
        self.csv_data = self.csv_data[self.csv_data[column].between(mean_value - three_sigma,
                                                                    mean_value + three_sigma)]


    def show_data_status(self, loaded_successfully):
        message = QMessageBox()
        message.setIcon(QMessageBox.Information)
        if loaded_successfully:
            message.setText("Data loaded successfully!")
            message.setWindowTitle("Success!")
        else:
            message.setText("No loaded data!")
            message.setWindowTitle("Choose a data file!")
        message.setStandardButtons(QMessageBox.Ok)
        message.exec()

    def select_root_directory(self):
        self.root_directory = QFileDialog.getExistingDirectory(directory=self.root_directory)

    def fill_data_columns_list(self):
        if "CH4_PPB" in self.csv_data.columns:
            self.data_columns_list.clear()
            self.data_columns_list.addItems(["CH4_PPB", "CO2_PPM", "H2O_PPM"])
        else:
            self.data_columns_list.clear()
            self.data_columns_list.addItems(["N2O_PPB", "H2O_PPM"])
        self.data_columns_list.show()

    def download_csv_file(self):
        csv_file_name = QFileDialog.getOpenFileName(self, "Open CSV", self.root_directory, "*.csv")[0]
        self.csv_data = pd.read_csv(csv_file_name, delimiter=';')
        print(self.csv_data.columns)
        if "MEASUREMENT_DATETIME" not in self.csv_data.columns:
            self.csv_data["MEASUREMENT_DATETIME"] = self.csv_data["MEASUREMENT_DATE"] + " " \
                                                    + self.csv_data["MEASUREMENT_TIME"]

        self.data_loaded = True
        self.fill_data_columns_list()
        self.show_data_status(True)
        dates = list(self.csv_data["MEASUREMENT_DATETIME"])
        try:
            timestamp_dates = [datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S").timestamp() for date in dates]
        except ValueError:
            timestamp_dates = [datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp() for date in dates]
        start_datetime = datetime.datetime.fromtimestamp(timestamp_dates[0])
        end_datetime = datetime.datetime.fromtimestamp(timestamp_dates[-1])
        self.start_datetime.setDateTime(start_datetime)
        self.end_datetime.setDateTime(end_datetime)
        print(self.csv_data.head(10))

    def draw_plot(self):
        if self.data_loaded:
            self.graphWidget.clear()
            selected_column = self.data_columns_list.currentText()
            self.delete_3_sigma(selected_column)
            dates = list(self.csv_data["MEASUREMENT_DATETIME"])
            try:
                timestamp_dates = [datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S").timestamp() for date in dates]
            except ValueError:
                timestamp_dates = [datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp() for date in dates]
            date_axis = DateAxisItem()
            self.graphWidget.setLabel("left", selected_column)
            self.graphWidget.setLabel("bottom", "Measurement Datetime")
            self.graphWidget.setAxisItems({'bottom': date_axis})
            self.graphWidget.setXRange(timestamp_dates[0],
                                       timestamp_dates[-1])
            self.graphWidget.setYRange(self.csv_data[selected_column].min(), self.csv_data[selected_column].max())
            self.graphWidget.plot(timestamp_dates, list(self.csv_data[selected_column]))
        else:
            self.show_data_status(False)

    def download_DATA_file(self):
        data_file_name = QFileDialog.getOpenFileName(self, "Open DATA", self.root_directory, "*.DATA")[0]
        filename = os.path.splitext(data_file_name)[0]
        data_path = filename + ".tsv"
        shutil.copy2(filename + ".DATA", data_path)
        self.csv_data = pd.read_csv(data_path, sep="\t", skiprows=5)
        self.csv_data = self.csv_data.drop(columns=['DATAH', 'SECONDS', 'NANOSECONDS', 'NDX', 'REMARK',
                                                    'CAVITY_P', 'CAVITY_T', 'LASER_PHASE_P', 'LASER_T',
                                                    'RESIDUAL', 'RING_DOWN_TIME', 'THERMAL_ENCLOSURE_T',
                                                    'PHASE_ERROR', 'LASER_T_SHIFT', 'INPUT_VOLTAGE', 'CHK'
                                                    ], index=0)
        self.csv_data = self.csv_data.loc[self.csv_data["DIAG"] == 0]
        self.csv_data = self.csv_data.drop(columns=["DIAG"])

        if "CH4" in self.csv_data.columns:
            self.csv_data.columns = ["MEASUREMENT_DATE", "MEASUREMENT_TIME", "H2O_PPM", "CO2_PPM", "CH4_PPB"]
        else:
            self.csv_data.columns = ["MEASUREMENT_DATE", "MEASUREMENT_TIME", "H2O_PPM", "N2O_PPB"]
        if "MEASUREMENT_DATETIME" not in self.csv_data.columns:
            self.csv_data["MEASUREMENT_DATETIME"] = self.csv_data["MEASUREMENT_DATE"] + " " \
                                                    + self.csv_data["MEASUREMENT_TIME"]
        # self.DATA_data[["LONGITUDE", "LATITUDE", "ELEVATION"]] = None
        dates = list(self.csv_data["MEASUREMENT_DATETIME"])
        try:
            timestamp_dates = [datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S").timestamp() for date in dates]
        except ValueError:
            timestamp_dates = [datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp() for date in dates]
        start_datetime = datetime.datetime.fromtimestamp(timestamp_dates[0])
        end_datetime = datetime.datetime.fromtimestamp(timestamp_dates[-1])
        self.csv_data.to_csv(filename + ".csv", index=False)
        self.data_loaded = True
        self.fill_data_columns_list()
        self.show_data_status(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    cat = CAT()
    cat.show()
    sys.exit(app.exec_())
