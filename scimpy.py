#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:20:04 2016

@author: showard
"""

import sys
from PySide import QtGui
import pyaudio
import scimpy.speakertest as speakertest
import scimpy.speakermodel as speakermodel
import numpy as np
from math import sqrt


class ImpTester(QtGui.QWidget):
    def __init__(self):
        super(ImpTester, self).__init__()
        self.measurement_engine = speakertest.SpeakerTestEngine()
        self.init_ui()

    def init_ui(self):
        def update_textbox(current, previous):
            new_row = listwidg.row(current)
            print(sc_info[new_row])
            infotext.setText("Name: {0}\n"
                             "Default Sampling Rate (Hz): {1}\n"
                             "Max Input Channels: {2}\n"
                             "Max Output Channels: {3}\n"
                             "Suggested Output Buffer (frames): {4}-{5}\n"
                             .format(sc_info[new_row]["name"],
                                     sc_info[new_row]["defaultSampleRate"],
                                     sc_info[new_row]["maxInputChannels"],
                                     sc_info[new_row]["maxOutputChannels"],
                                     int(sc_info[new_row][
                                         "defaultLowOutputLatency"] *
                                         sc_info[new_row]["defaultSampleRate"]
                                        ),
                                     int(sc_info[new_row][
                                         "defaultHighOutputLatency"] *
                                         sc_info[new_row]["defaultSampleRate"])
                                    ))
            test2lineedit.setText(str(sc_info[new_row]["defaultSampleRate"]))

        def get_sc_info():
            pya = pyaudio.PyAudio()
            sc_info = [pya.get_device_info_by_index(n)
                       for n in range(pya.get_device_count())]
            default_device = pya.get_default_host_api_info()[
                "defaultInputDevice"]
            return [sc_info, default_device]

        def verify_sc_settings():
            pya = pyaudio.PyAudio()
            try:
                supported = pya.is_format_supported(
                    rate=float(test2lineedit.text()),
                    input_device=listwidg.row(listwidg.currentItem()),
                    input_channels=2,
                    input_format=pya.get_format_from_width(
                        int(test4combobox.currentText())/8),
                    output_device=listwidg.row(listwidg.currentItem()),
                    output_channels=2,
                    output_format=pya.get_format_from_width(
                        int(test4combobox.currentText())/8))
                if supported:
                    statusbar.showMessage(
                        "These settings are supported!", 3000)
            except ValueError as err:
                statusbar.showMessage("ERROR: "+str(err), 3000)

        def run_measurement():
            print(test2lineedit.text())
            self.measurement_engine.run(
                framesize=int(test3lineedit.text()),
                datarate=int(float(test2lineedit.text())),
                duration=float(test6lineedit.text()),
                width=int(test4combobox.currentText())/8)

        [sc_info, default_device] = get_sc_info()

        statusbar = QtGui.QStatusBar(self)

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QtGui.QPushButton('Verify Soundcard Capabillities')
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.clicked.connect(verify_sc_settings)

        runbtn = QtGui.QPushButton('Begin Test')
        runbtn.clicked.connect(run_measurement)

        layout = QtGui.QGridLayout()

        infotext = QtGui.QLabel()
        #  TODO make each widget its own class, with get/set functions to access data
        formwidget = QtGui.QGroupBox("Measurement Parameters")
        formwidgetlayout = QtGui.QFormLayout()
        test2lineedit = QtGui.QLineEdit()
        test3lineedit = QtGui.QLineEdit("1024")
        test4combobox = QtGui.QComboBox()
        test4combobox.addItem("8")
        test4combobox.addItem("16")
        test4combobox.addItem("32")
        test4combobox.setCurrentIndex(1)
        test5lineedit = QtGui.QLineEdit("10")
        test6lineedit = QtGui.QLineEdit("2")
        formwidgetlayout.addRow("Sampling Rate (kHz):", test2lineedit)
        formwidgetlayout.addRow("I/O Buffer Size (frames, 0=auto):",
                                test3lineedit)
        formwidgetlayout.addRow("Data width (bits):", test4combobox)
        formwidgetlayout.addRow("Display Freq Resolution (Hz):", test5lineedit)
        formwidgetlayout.addRow("Measurement Duration (s):", test6lineedit)
        formwidget.setLayout(formwidgetlayout)

        listwidg = QtGui.QListWidget()
        for k in sc_info:
            listwidg.addItem("%s" % k["name"])
        listwidg.currentItemChanged.connect(update_textbox)
        listwidg.setCurrentItem(listwidg.item(default_device))

        layout.addWidget(listwidg, 0, 0)
        layout.addWidget(btn, 1, 0)
        layout.addWidget(runbtn, 2, 0)
        layout.addWidget(infotext, 0, 1)
        layout.addWidget(formwidget, 0, 3, 3, 1)
        layout.addWidget(statusbar, 3, 0, 1, 4)

        self.setLayout(layout)

        self.setWindowTitle('Impedance Tester')
        self.center()
        self.show()

    def center(self):
        framegeo = self.frameGeometry()
        centerpoint = QtGui.QDesktopWidget().availableGeometry().center()
        framegeo.moveCenter(centerpoint)
        self.move(framegeo.topLeft())

class SealedBoxWidget(QtGui.QGroupBox):
    def __init__(self,
                 title,
                 fslineedit,
                 qtslabel,
                 vasllineedit,
                 vasflineedit,
                 relineedit,
                 cmslineedit,
                 mmslineedit,
                 rmslineedit,
                 sdlineedit,
                 bllineedit):  # eventually just pass the while widget
                 # or we can keep an object somewhere that keeps all of these and pass that object to each widget

        def set_f3():
            qt = float(qtlabel.text())
            alpha =float(vasflineedit.text())/float(vbflineedit.text())
            f3 =   float(fslineedit.text()) * sqrt(alpha +1) * sqrt((1/qt**2-2+sqrt((2-1/qt**2)**2+4))/2)
            f3lineedit.setText("{0:.0f}".format(f3))

        def calcIdealParams():
            alpha_inv = 2*float(qtslabel.text())**2/(1-2*float(qtslabel.text())**2)
            f3 =  float(fslineedit.text()) * sqrt(1/alpha_inv +1)
            vbflineedit.setText("{0:.2g}".format(
                float(vasflineedit.text())*alpha_inv ))
            self.vbllineedit.setText("{0:.2g}".format(
                float(vasllineedit.text())*alpha_inv ))
            qtlabel.setText("{0:0.2g}".format(1/sqrt(2)))
            # f3lineedit.setText("{0:.0f}".format(f3))
            set_f3()
            
        def vbflineedit_callback():
            alpha =float(vasflineedit.text())/float(vbflineedit.text())
            qt = float(qtslabel.text()) * sqrt(alpha+1)
            qtlabel.setText("{0:0.2g}".format(qt))
            self.vbllineedit.setText("{0:0.2g}".format(float(vbflineedit.text())*0.0283168*1000))
            set_f3()

        def vbllineedit_callback():
            alpha =float(vasllineedit.text())/float(self.vbllineedit.text())
            qt = float(qtslabel.text()) * sqrt(alpha+1)
            qtlabel.setText("{0:0.2g}".format(qt))
            vbflineedit.setText("{0:0.2g}".format(float(self.vbllineedit.text())/0.0283168/1000 ))
            set_f3()

        def calcParamsf3():
            print("TESTING STUB")
            print(speakermodel.cheby_find_k(float(qtslabel.text())))
            print(speakermodel.sealed_find_vb_qt(vas=float(vasllineedit.text())/1000,
                                                 fs=float(fslineedit.text()),
                                                 f3=float(f3lineedit.text()),
                                                 qts=float(qtslabel.text())))
            
        def resetParams():
            self.vbllineedit.setText("inf")
            vbflineedit.setText("inf")
            f3lineedit.setText("")
            qt = float(qtslabel.text())
            qtlabel.setText("{0:0.2g}".format(qt))
            set_f3()

        super(SealedBoxWidget, self).__init__(title)
        layout = QtGui.QFormLayout()
        self.vbllineedit = QtGui.QLineEdit()
        self.vbllineedit.editingFinished.connect(vbllineedit_callback)
        layout.addRow("Box Volume (Vb) litres:", self.vbllineedit)
        vbflineedit = QtGui.QLineEdit()
        vbflineedit.editingFinished.connect(vbflineedit_callback)
        layout.addRow("Box Volume (Vb) ft^3:", vbflineedit)
        qtlabel = QtGui.QLabel()
        layout.addRow("Qt:", qtlabel)
        f3lineedit = QtGui.QLineEdit()
        layout.addRow("Cutoff Frequency (f3) Hz:", f3lineedit)
        idealbtn = QtGui.QPushButton("Set to Ideal Closed Box")
        idealbtn.clicked.connect(calcIdealParams)
        f3btn = QtGui.QPushButton("Calculate Parameters Given f3 && Vb")
        f3btn.clicked.connect(calcParamsf3)
        resetbtn = QtGui.QPushButton("Set to Infinite Baffle")
        resetbtn.clicked.connect(resetParams)
        layout.addRow(idealbtn)
        layout.addRow(f3btn)
        layout.addRow(resetbtn)
        resetParams()
        self.setLayout(layout)


class SpeakerModelWidget(QtGui.QWidget):
    def __init__(self):
        super(SpeakerModelWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        def set_eta0(sd, re, mms, bl):
            efficiency = sd**2 * 1.18/345/2/np.pi/re/(mms/bl**2)**2/bl**2
            eta0label.setText("{0:2.1f} %".format(efficiency*100))
            spllabel.setText(
                "{0:.0f} dB 1w1m".format(112.1+10*np.log10(efficiency)))

        def find_enclosure():
            speakermodel.calc_impedance(re=float(relineedit.text()),
                                        le=float(lelineedit.text())/1000,
                                        cms=float(cmslineedit.text())/1000,
                                        mms=float(mmslineedit.text())/1000,
                                        rms=float(rmslineedit.text()),
                                        sd=float(sdlineedit.text())/(100*100),
                                        bl=float(bllineedit.text()),
                                        vb=float(sealedboxwidg.vbllineedit.text())/1000)

        def calc_component_params():
            try:
                re = float(relineedit.text())
                qes = float(qeslineedit.text())
                qms = float(qmslineedit.text())
                bl = float(bllineedit.text())
                sd = float(sdlineedit.text())/(100*100)
                fs = float(fslineedit.text())

                rms = bl**2/(qms/qes*re)
                rmslineedit.setText("{0:.2g}".format(rms))
                cms = (1/2/np.pi/fs/qms/rms)*1000  # mm/N
                cmslineedit.setText("{0:.2g}".format(cms))
                mms = 1/(cms*(2*np.pi*fs)**2)*1000  # grams
                mmslineedit.setText("{0:.2g}".format(mms*1000))

                cmslineedit_set()

                set_eta0(sd, re, mms, bl)

                qtslabel.setText("{0:.2g}".format(qms*qes/(qms+qes)))
            except ValueError:
                pass  # might not be set yet

        def calc_system_params():
            try:
                re = float(relineedit.text())
                cms = float(cmslineedit.text())/1000
                mms = float(mmslineedit.text())/1000
                rms = float(rmslineedit.text())
                sd = float(sdlineedit.text())/(100*100)
                bl = float(bllineedit.text())

                fs = 1/2/np.pi/sqrt(cms*mms)
                qes = 2*np.pi*fs*mms*re/bl**2
                qms = 2*np.pi*fs*mms/rms
                qts = qms*qes/(qms+qes)
                set_eta0(sd, re, mms, bl)

                fslineedit.setText("{0:2.0f}".format(fs))
                qeslineedit.setText("{0:1.2g}".format(qes))
                qmslineedit.setText("{0:1.2g}".format(qms))
                qtslabel.setText("{0:1.2g}".format(qts))
            except ValueError:
                pass  # might not be set yet

        def vasflineedit_callback():
            sd = float(sdlineedit.text())/(100*100)
            vas = float(vasflineedit.text())*0.0283168
            cms = vas/(1.18*345**2*sd**2)*1000
            cmslineedit.setText("{0:.2g}".format(cms))
            cmslineedit_callback()

        def vasllineedit_callback():
            sd = float(sdlineedit.text())/(100*100)
            vas = float(vasllineedit.text())/1000
            cms = vas/(1.18*345**2*sd**2)*1000
            cmslineedit.setText("{0:.2g}".format(cms))
            cmslineedit_callback()

        def cmslineedit_set():
            sd = float(sdlineedit.text())/(100*100)
            vas = (float(cmslineedit.text())/1000) * 1.18*345**2*sd**2
            vasf = vas/0.0283168
            vasl = vas*1000  # litres
            vasflineedit.setText("{0:.2g}".format(vasf))
            vasllineedit.setText("{0:.2g}".format(vasl))

        def cmslineedit_callback():
            cmslineedit_set()
            calc_system_params()

        layout = QtGui.QGridLayout()

        formwidget = QtGui.QGroupBox("Component T/S Parameters")
        formwidgetlayout = QtGui.QFormLayout()
        relineedit = QtGui.QLineEdit("6")
        relineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow("DC Resistance (Re) Ohms:", relineedit)
        lelineedit = QtGui.QLineEdit("0.1")
        lelineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow("Voice Coil Inductance (Le) mH:", lelineedit)
        sdlineedit = QtGui.QLineEdit("25")
        sdlineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow(
            "Surface Area of Cone (Sd) cm^2:", sdlineedit)
        bllineedit = QtGui.QLineEdit("4.5")
        bllineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow(
            "Mag. Flux Density - Length (BL) Tm:", bllineedit)
        cmslineedit = QtGui.QLineEdit("0.16")
        cmslineedit.editingFinished.connect(cmslineedit_callback)
        formwidgetlayout.addRow(
            "Mechanical Compliance of Suspension (Cms) mm/N:", cmslineedit)
        vasllineedit = QtGui.QLineEdit("0.14")
        vasllineedit.editingFinished.connect(vasllineedit_callback)
        formwidgetlayout.addRow(
            "Driver Compliance Volume (Vas) litres:", vasllineedit)
        vasflineedit = QtGui.QLineEdit("0.005")
        vasflineedit.editingFinished.connect(vasflineedit_callback)
        formwidgetlayout.addRow(
            "Driver Compliance Volume (Vas) ft^3:", vasflineedit)
        mmslineedit = QtGui.QLineEdit("1.8")
        mmslineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow(
            "Diaphragm Mass w/ Airload (Mms) g:", mmslineedit)
        rmslineedit = QtGui.QLineEdit("3.4")
        rmslineedit.editingFinished.connect(calc_system_params)
        formwidgetlayout.addRow(
            "Mechanical Resistance (Rms) Ns/m=Mech. ohm:", rmslineedit)

        formwidget.setLayout(formwidgetlayout)

        runbtn = QtGui.QPushButton(
            'Model Speaker Impedance and Infinite Baffle Performance (need Vb=inf)')
        runbtn.clicked.connect(find_enclosure)

        systemformwidget = QtGui.QGroupBox("Speaker T/S Parameters")
        systemformwidgetlayout = QtGui.QFormLayout()
        fslineedit = QtGui.QLineEdit("300")
        fslineedit.editingFinished.connect(calc_component_params)
        systemformwidgetlayout.addRow("Resonant Freq. (Fs) Hz:", fslineedit)
        qtslabel = QtGui.QLabel("0.5")
        systemformwidgetlayout.addRow("Qts:", qtslabel)
        qeslineedit = QtGui.QLineEdit("1")
        qeslineedit.editingFinished.connect(calc_component_params)
        systemformwidgetlayout.addRow("Qes:", qeslineedit)
        qmslineedit = QtGui.QLineEdit("1")
        qmslineedit.editingFinished.connect(calc_component_params)
        systemformwidgetlayout.addRow("Qms:", qmslineedit)
        eta0label = QtGui.QLabel("0.4 %")
        systemformwidgetlayout.addRow(
            "Reference Efficiency (eta0):", eta0label)
        spllabel = QtGui.QLabel("88 dB 1W1m")
        systemformwidgetlayout.addRow(
            "Sound Power Level (SPL):", spllabel)

        systemformwidget.setLayout(systemformwidgetlayout)

        sealedboxwidg = SealedBoxWidget("Enclosure Parameters",
                                        fslineedit,
                                        qtslabel,
                                        vasllineedit,
                                        vasflineedit,
                                        relineedit,
                                        cmslineedit,
                                        mmslineedit,
                                        rmslineedit,
                                        sdlineedit,
                                        bllineedit)
        sealedboxbtn = QtGui.QPushButton("Calculate Sealed Box Performace")
        sealedboxbtn.clicked.connect(find_enclosure)

        layout.addWidget(runbtn, 1, 0, 1, 2)
        layout.addWidget(formwidget, 0, 0, 1, 1)
        layout.addWidget(systemformwidget, 0, 1, 1, 1)
        layout.addWidget(sealedboxwidg,0,2,1,1)
        layout.addWidget(sealedboxbtn,1,2,1,1)
        self.setLayout(layout)

        self.setWindowTitle('Speaker Performance')
        self.center()
        self.show()

    def center(self):
        framegeo = self.frameGeometry()
        centerpoint = QtGui.QDesktopWidget().availableGeometry().center()
        framegeo.moveCenter(centerpoint)
        self.move(framegeo.topLeft())


def main():
    app = QtGui.QApplication(sys.argv)
    _ = ImpTester()
    _ = SpeakerModelWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
