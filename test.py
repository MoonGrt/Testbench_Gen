import sys, re, chardet
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QTextEdit, QGroupBox, QRadioButton, QCheckBox
from PyQt5.QtGui import QIcon

class TestbenchGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Verilog Testbench Generator')
        self.resize(900, 800)
        self.setWindowIcon(QIcon('images/verilog.png'))
        
        self.tb_content = ''
        self.TFupdating = False

        # component
        self.module_label = QLabel('Verilog Module:')
        self.module_input = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self.browse_file)
        self.input_text = QTextEdit()
        self.input_text.setLineWrapMode(QTextEdit.NoWrap)
        self.input_text.textChanged.connect(self.RT_Gen)
        self.output_text = QTextEdit()
        self.output_text.setLineWrapMode(QTextEdit.NoWrap)


        self.mode_option = QGroupBox("")
        self.mode_option1 = QRadioButton('TestBench')
        self.mode_option2 = QRadioButton('Instance')
        self.mode_option1.setChecked(True)
        mode_option_layout = QHBoxLayout()
        mode_option_layout.addWidget(self.mode_option1)
        mode_option_layout.addWidget(self.mode_option2)
        self.mode_option.setLayout(mode_option_layout)
        self.mode_option1.toggled.connect(self.mode_change)

        self.align_option = QGroupBox("align")
        self.align_option1 = QRadioButton('None')
        self.align_option2 = QRadioButton('Half')
        self.align_option3 = QRadioButton('Full')
        self.align_option3.setChecked(True)
        align_option_layout = QHBoxLayout()
        align_option_layout.addWidget(self.align_option1)
        align_option_layout.addWidget(self.align_option2)
        align_option_layout.addWidget(self.align_option3)
        self.align_option.setLayout(align_option_layout)
        self.align_option1.toggled.connect(self.RT_Gen)
        self.align_option2.toggled.connect(self.RT_Gen)
        self.align_option3.toggled.connect(self.RT_Gen)

        self.init_label = QLabel('Init:')
        self.clk_option = QCheckBox('clk')
        self.clk_option.setChecked(True)
        self.clk_option.stateChanged.connect(self.RT_Gen)
        self.rst_option = QCheckBox('rst')
        self.rst_option.setChecked(True)
        self.rst_option.stateChanged.connect(self.RT_Gen)
        self.operate_option = QCheckBox('operate')
        self.operate_option.stateChanged.connect(self.RT_Gen)
        init_layout = QHBoxLayout()
        init_layout.addWidget(self.init_label)
        init_layout.addWidget(self.clk_option)
        init_layout.addWidget(self.rst_option)
        init_layout.addWidget(self.operate_option)
        # TODO: clk rst自定义

        self.time_label = QLabel('T:')
        self.time_input = QLineEdit('20')
        self.time_input.textChanged.connect(self.time_input_changed)
        self.time_unit = QComboBox()
        self.time_unit.addItems(["ps", "ns", "us", "ms", "s"])
        self.time_unit.setCurrentIndex(1)
        self.time_unit.currentIndexChanged.connect(self.time_unit_changed)
        self.frequency_label = QLabel('f:')
        self.frequency_input = QLineEdit('50')
        self.frequency_input.textChanged.connect(self.frequency_input_changed)
        self.frequency_unit = QComboBox()
        self.frequency_unit.addItems(["", "K", "M", "G"])
        self.frequency_unit.setCurrentIndex(2)
        self.frequency_unit.currentIndexChanged.connect(self.frequency_unit_changed)
        clk_layout = QHBoxLayout()
        clk_layout.addWidget(self.time_label)
        clk_layout.addWidget(self.time_input)
        clk_layout.addWidget(self.time_unit)
        clk_layout.addWidget(self.frequency_label)
        clk_layout.addWidget(self.frequency_input)
        clk_layout.addWidget(self.frequency_unit)
        # TODO: 生成修改

        self.UUT_label = QLabel('UUT:')
        self.UUT_IO_option = QCheckBox('IO')
        self.UUT_IO_option.setChecked(False)
        self.UUT_IO_option.stateChanged.connect(self.RT_Gen)
        self.UUT_CR_option = QCheckBox('CR')
        self.UUT_CR_option.setChecked(False)
        self.UUT_CR_option.stateChanged.connect(self.RT_Gen)
        UUT_layout = QHBoxLayout()
        UUT_layout.addWidget(self.UUT_label)
        UUT_layout.addWidget(self.UUT_IO_option)
        UUT_layout.addWidget(self.UUT_CR_option)
        # TODO: clk rst自定义

        self.gen_button = QPushButton('Gen')
        self.gen_button.setFixedWidth(80)
        self.gen_button.clicked.connect(self.Gen)
        self.realtime = QCheckBox('RT')
        self.realtime.setChecked(True)
        self.result_label = QLabel('')
        self.copy_button = QPushButton('Copy')
        self.copy_button.setFixedWidth(135)
        self.copy_button.clicked.connect(self.copy_to_clipboard)


        # layout
        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(self.module_label)
        layoutH1.addWidget(self.module_input)
        layoutH1.addWidget(self.browse_button)

        layoutV2 = QVBoxLayout()
        layoutV2.addWidget(self.mode_option)
        layoutV2.addWidget(self.align_option)
        layoutV2.addLayout(init_layout)
        layoutV2.addLayout(clk_layout)
        layoutV2.addLayout(UUT_layout)
        layoutV2.addWidget(self.input_text)

        layoutH2 = QHBoxLayout()
        layoutH2.addLayout(layoutV2)
        layoutH2.addWidget(self.output_text)
        layoutH2.setStretch(0, 4)
        layoutH2.setStretch(1, 6)

        layoutH3 = QHBoxLayout()
        layoutH3.addWidget(self.gen_button)
        layoutH3.addWidget(self.realtime)
        layoutH3.addWidget(self.result_label)
        layoutH3.addWidget(self.copy_button)

        layoutV1 = QVBoxLayout()
        layoutV1.addLayout(layoutH1)
        layoutV1.addLayout(layoutH2)
        layoutV1.addLayout(layoutH3)

        self.setLayout(layoutV1)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Verilog Files (*.v)")
        # file_dialog.selectFile("test.v")

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.module_input.setText(file_path)

            input_file = self.module_input.text()
            if not input_file:
                return
            with open(input_file, 'rb') as f:
                f_info = chardet.detect(f.read())
                f_encoding = f_info['encoding']
            with open(input_file, encoding=f_encoding) as inFile:
                self.input_text.setPlainText(inFile.read())

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.result_label.setText(f"Content copied to clipboard.")

    def mode_change(self):
        if self.mode_option1.isChecked():
            self.clk_option.setEnabled(True)
            self.rst_option.setEnabled(True)
            self.operate_option.setEnabled(True)
            self.time_input.setEnabled(True)
            self.time_unit.setEnabled(True)
            self.frequency_input.setEnabled(True)
            self.frequency_unit.setEnabled(True)
        else:
            self.clk_option.setEnabled(False)
            self.rst_option.setEnabled(False)
            self.operate_option.setEnabled(False)
            self.time_input.setEnabled(False)
            self.time_unit.setEnabled(False)
            self.frequency_input.setEnabled(False)
            self.frequency_unit.setEnabled(False)
        self.RT_Gen()

    def RT_Gen(self):
        if self.realtime.isChecked():
            self.Gen()

    def time_input_changed(self, text):
        if not self.TFupdating:
            try:
                value = float(text)
            except ValueError:
                value = 0.0
            self.update_frequency_from_time(value)

    def frequency_input_changed(self, text):
        if not self.TFupdating:
            try:
                value = float(text)
            except ValueError:
                value = 0.0
            self.update_time_from_frequency(value)

    def time_unit_changed(self, index):
        if not self.TFupdating:
            frequency = float(self.frequency_input.text())
            self.update_time_from_frequency(frequency)

    def frequency_unit_changed(self, index):
        if not self.TFupdating:
            time = float(self.time_input.text())
            self.update_frequency_from_time(time)

    def update_frequency_from_time(self, time):
        self.TFupdating = True
        try:
            frequency = round(self.convert_to_frequency(time), 2)
            self.frequency_input.setText(str(frequency))
        except:
            pass
        self.TFupdating = False

    def update_time_from_frequency(self, frequency):
        self.TFupdating = True
        try:
            time = round(self.convert_to_time(frequency), 2)
            self.time_input.setText(str(time))
        except:
            pass
        self.TFupdating = False

    def convert_to_frequency(self, time):
        time_unit_index = self.time_unit.currentIndex()
        time_unit_value = 10 ** ((time_unit_index+2) * 3)
        frequency_unit_index = self.frequency_unit.currentIndex()
        frequency_unit_value = 10 ** (frequency_unit_index * 3)
        return time_unit_value / (time * frequency_unit_value)

    def convert_to_time(self, frequency):
        frequency_unit_index = self.frequency_unit.currentIndex()
        frequency_unit_value = 10 ** (frequency_unit_index * 3)
        time_unit_index = self.time_unit.currentIndex()
        time_unit_value = 10 ** ((4-time_unit_index) * 3)
        return time_unit_value / (frequency * frequency_unit_value)



    # testbench 生成逻辑
    def delComment(self, Text):
        """ removed comment """
        single_line_comment = re.compile(r"//(.*)$", re.MULTILINE)
        multi_line_comment  = re.compile(r"/\*(.*?)\*/", re.DOTALL)
        Text = multi_line_comment.sub('\n', Text)
        Text = single_line_comment.sub('\n', Text)
        return Text

    def delBlock(self, Text):
        """ removed task and function block """
        Text = re.sub(r'\Wtask\W[\W\w]*?\Wendtask\W', '\n', Text)
        Text = re.sub(r'\Wfunction\W[\W\w]*?\Wendfunction\W', '\n', Text)
        return Text

    def findName(self, inText):
        """ find module name and port list"""
        p = re.search(r'([a-zA-Z_][a-zA-Z_0-9]*)\s*', inText)
        mo_Name = p.group(0).strip()
        return mo_Name

    def paraDeclare(self, inText ,portArr):
        """ find parameter declare """
        pat = r'\s'+ portArr + r'\s[\w\W]*?[;,)]'
        ParaList = re.findall(pat, inText)
        return ParaList

    def portDeclare(self, inText, portArr):
        """find port declare, Syntax:
           input [ net_type ] [ signed ] [ range ] list_of_port_identifiers
           return list as : (port, [range])
        """
        port_definition = re.compile(
            r'\b' + portArr +
            r''' (\s+(wire|reg)\s+)* (\s*signed\s+)*  (\s*\[.*?:.*?\]\s*)*
            (?P<port_list>.*?)
            (?= \binput\b | \boutput\b | \binout\b | ; | \) )
            ''',
            re.VERBOSE | re.MULTILINE | re.DOTALL
        )

        pList = port_definition.findall(inText)

        t = []
        for ls in pList:
            if len(ls) >=2:
                t += self.portDic(ls[-2:])
        return t

    def portDic(self, port) :
        """delet as : input a =c &d;
            return list as : (port, [range])
        """
        pRe = re.compile(r'(.*?)\s*=.*', re.DOTALL)

        pRange = port[0]
        pList  = port[1].split(',')
        pList  = [i.strip() for i in pList if i.strip() != '']
        pList  = [(pRe.sub(r'\1', p), pRange.strip()) for p in pList]

        return pList

    def formatPort(self, AllPortList):
        PortList = AllPortList[0] + AllPortList[1] + AllPortList[2]

        str = ''
        if PortList != []:
            l1 = max([len(i[0]) for i in PortList]) + 1
            l2 = max([len(i[1]) for i in PortList])

            strList = []
            for idx, pl in enumerate(AllPortList):
                if pl != []:
                    if self.UUT_IO_option.isChecked():
                        if self.align_option1.isChecked():
                            if idx == 0:
                                str = ',\n'.join(['/*i*/' + '.' + i[0] + ' ( ' + (i[0] + i[1]) + ' )' for i in pl])
                            if idx == 1:
                                str = ',\n'.join(['/*o*/' + '.' + i[0] + ' ( ' + (i[0] + i[1]) + ' )' for i in pl])
                            if idx == 2:
                                str = ',\n'.join(['/*io*/' + '.' + i[0] + ' ( ' + (i[0] + i[1]) + ' )' for i in pl])
                        elif self.align_option2.isChecked():
                            if idx == 0:
                                str = ',\n'.join(['/*i*/' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                            if idx == 1:
                                str = ',\n'.join(['/*o*/' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                            if idx == 2:
                                str = ',\n'.join(['/*io*/' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                        elif self.align_option3.isChecked():
                            if idx == 0:
                                str = ',\n'.join(['/*i*/ ' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                            if idx == 1:
                                str = ',\n'.join(['/*o*/ ' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                            if idx == 2:
                                str = ',\n'.join(['/*io*/' + '.' + i[0].ljust(l1) + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                    else:
                        if self.align_option1.isChecked():
                            str = ',\n'.join([' '*4 + '.' + i[0]
                                        + ' ( ' + (i[0] + i[1]) + ' )' for i in pl])
                        elif self.align_option2.isChecked():
                            str = ',\n'.join([' '*4 + '.' + i[0].ljust(l1)
                                        + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                        elif self.align_option3.isChecked():
                            str = ',\n'.join([' '*4 + '.' + i[0].ljust(l1)
                                        + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                    strList += [str]
            if self.UUT_CR_option.isChecked():
                str = ',\n\n'.join(strList)
            else:
                str = ',\n'.join(strList)

        return str

    def formatDeclare(self, PortList, portArr, init = ""):
        str = ''

        if PortList != []:
            try:
                if self.align_option1.isChecked():
                    pass
                elif self.align_option2.isChecked():
                    l1 = max([len(i[0]) for i in PortList if i[1] == ''])
                elif self.align_option3.isChecked():
                    l1 = max([len(i[0]) for i in PortList])
                    l2 = max([len(i[1]) for i in PortList])
            except:
                l1 = 0
                l2 = 0

            if init != "":
                init = " = " + init

                if self.align_option1.isChecked():
                    str = '\n'.join([portArr + ' ' + (i[1] + min(len(i[1]), 1)*' ' + i[0]) + init + ';' for i in PortList])
                elif self.align_option2.isChecked():
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                                + i[0]).ljust(l1) + init + ';' for i in PortList])
                elif self.align_option3.isChecked():
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1].ljust(l2+1)
                                + i[0]).ljust(l1+l2+1) + init + ';' for i in PortList])
            else:
                if self.align_option1.isChecked():
                    str = '\n'.join([portArr + ' ' + (i[1] + min(len(i[1]), 1)*' ' + i[0]) + ';' for i in PortList])
                elif self.align_option2.isChecked():
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                                + i[0]) + ';' for i in PortList])
                elif self.align_option3.isChecked():
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1].ljust(l2+1)
                                + i[0]).ljust(l1+l2+1) + ';' for i in PortList])
        return str

    def formatPara(self, ParaList):
        paraDec = ''
        paraDef = ''
        l1 = 0
        l2 = 0
        if ParaList != []:
            s = '\n'.join(ParaList)
            pat = r'([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*([\w\W]*?)\s*[;,)]'
            p = re.findall(pat, s)

            l1 = max([len(i[0]) for i in p])
            l2 = max([len(i[1]) for i in p])

            if self.align_option1.isChecked():
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0], i[1]) for i in p])
            elif self.align_option2.isChecked():
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1]) for i in p])
            elif self.align_option3.isChecked():
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1].ljust(l2)) for i in p])

            if self.align_option1.isChecked():
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0] + ' ( ' + i[0] + ' )' for i in p]) + ')\n'
            elif self.align_option2.isChecked():
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0].ljust(l1 + 1)
                            + '( ' + i[0].ljust(l1) + ' )' for i in p]) + ')\n'
            elif self.align_option3.isChecked():
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0].ljust(l1 + 1)
                            + '( ' + i[0].ljust(l1) + ' )' for i in p]) + ')\n'

        if self.mode_option1.isChecked():
            if self.align_option1.isChecked():
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T', '10')])
            elif self.align_option2.isChecked():
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10')])
            elif self.align_option3.isChecked():
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10'.ljust(l2))])
        else:
            preDec = ''

        paraDec = preDec + paraDec
        return paraDec, paraDef


    def Gen(self):
        inText = self.input_text.toPlainText()

        if not inText:
            self.result_label.setText(f"No input!")
            return

        # try:
        # removed comment, task, function
        inText = self.delComment(inText)
        inText = self.delBlock(inText)

        # moduel ... endmodule #
        moPos_begin = re.search(r'(\b|^)module\b', inText).end()
        moPos_end = re.search(r'\bendmodule\b', inText).start()
        inText = inText[moPos_begin: moPos_end]

        self.name = self.findName(inText)
        paraList = self.paraDeclare(inText, 'parameter')
        self.paraDec, self.paraDef = self.formatPara(paraList)

        ioPadAttr = ['input', 'output', 'inout']
        self.input  = self.portDeclare(inText, ioPadAttr[0])
        self.output = self.portDeclare(inText, ioPadAttr[1])
        self.inout  = self.portDeclare(inText, ioPadAttr[2])

        self.portList = self.formatPort([self.input, self.output, self.inout])
        self.input  = self.formatDeclare(self.input, 'reg', '0')
        self.output = self.formatDeclare(self.output, 'wire')
        self.inout  = self.formatDeclare(self.inout, 'wire')

        self.GEN()
        # except:
        #     self.result_label.setText(f"Error!")

    """ generate testbench """
    def GEN(self):
        # write testbench
        if self.mode_option1.isChecked():
            self.tb_content += '`timescale 1ns / 1ps\n'
            self.tb_content += "module tb_%s;\n\n" % self.name

        # module_parameter_port_list
        if(self.paraDec != ''):
            self.tb_content += "// %s Parameters\n%s\n" % (self.name, self.paraDec)

        # list_of_port_declarations
        if(self.input != ''):
            self.tb_content += "\n// %s Inputs\n%s\n" % (self.name, self.input)
        if(self.output != ''):
            self.tb_content += "\n// %s Outputs\n%s\n" % (self.name, self.output)
        if(self.inout != ''):
            self.tb_content += "\n// %s Inouts\n%s\n" % (self.name, self.inout)

        # print clock
        if self.mode_option1.isChecked():
            if self.clk_option.isChecked():
                self.tb_content += '''\ninit begin\n    forever #(T/2) clk = ~clk;\nend\n'''
            if self.rst_option.isChecked():
                self.tb_content += '''\ninit begin\n    #(T*2) rst_n = 1;\nend\n'''
            # self.tb_content += "%s%s" % (clk,rst)

        # print operation
        if self.operate_option.isChecked() & self.mode_option1.isChecked():
            self.tb_content += '''\ninit begin\n\n    $finish;\nend\n'''

        # UUT
        self.tb_content += "\n%s %su_%s (\n%s\n);\n" % (self.name, self.paraDef, self.name, self.portList)

        # endmodule
        if self.mode_option1.isChecked():
            self.tb_content += "\nendmodule"

        self.output_text.setPlainText(self.tb_content)
        self.result_label.setText("Gen success!")
        self.tb_content = ''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestbenchGenerator()
    window.show()
    sys.exit(app.exec_())



# TODO:
# UUT 名字 回车 i/o

