import sys, re, chardet
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QGroupBox, QRadioButton, QCheckBox
from PyQt5.QtGui import QIcon

class TestbenchGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Verilog Testbench Generator')
        self.resize(900, 700)
        self.setWindowIcon(QIcon('images/verilog.png'))
        
        self.fileenstate = 0
        self.realtimestate = 0
        self.modestate = 1
        self.alignstate = 3
        self.operatestate = 2
        self.tb_content = ''


        # component
        self.module_label = QLabel('Verilog Module:')
        self.module_input = QLineEdit()
        self.module_input.setEnabled(False)
        self.browse_button = QPushButton('Browse')
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_button.setEnabled(False)
        self.file_en = QCheckBox('EN')
        self.file_en.stateChanged.connect(self.file_en_state)
        self.input_text = QTextEdit()
        self.input_text.textChanged.connect(self.inputtext_change)
        self.output_textedit = QTextEdit()
        self.gen_button = QPushButton('Gen')
        self.gen_button.setFixedWidth(80)
        self.gen_button.clicked.connect(self.Gen)
        self.realtime = QCheckBox('RT')
        self.realtime.stateChanged.connect(self.realtime_state)
        self.result_label = QLabel('')
        self.copy_button = QPushButton('Copy')
        self.copy_button.setFixedWidth(135)
        self.copy_button.clicked.connect(self.copy_to_clipboard)


        self.mode_option = QGroupBox("")
        self.mode_option1 = QRadioButton('TestBench')
        self.mode_option2 = QRadioButton('Instance')
        self.mode_option1.setChecked(True)
        mode_option_layout = QHBoxLayout()
        mode_option_layout.addWidget(self.mode_option1)
        mode_option_layout.addWidget(self.mode_option2)
        self.mode_option.setLayout(mode_option_layout)

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

        self.operate_option = QGroupBox("operate")
        self.operate_option1 = QRadioButton('EN')
        self.operate_option2 = QRadioButton('OFF')
        self.operate_option2.setChecked(True)
        operate_option_layout = QHBoxLayout()
        operate_option_layout.addWidget(self.operate_option1)
        operate_option_layout.addWidget(self.operate_option2)
        self.operate_option.setLayout(operate_option_layout)

        self.mode_option1.toggled.connect(self.mode_state)
        # self.mode_option2.toggled.connect(self.mode_state)
        self.align_option1.toggled.connect(self.align_state)
        self.align_option2.toggled.connect(self.align_state)
        self.align_option3.toggled.connect(self.align_state)
        self.operate_option1.toggled.connect(self.operate_state)
        # self.operate_option2.toggled.connect(self.operate_state)


        # layout
        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(self.module_label)
        layoutH1.addWidget(self.module_input)
        layoutH1.addWidget(self.browse_button)
        layoutH1.addWidget(self.file_en)

        layoutV2 = QVBoxLayout()
        layoutV2.addWidget(self.mode_option)
        layoutV2.addWidget(self.align_option)
        layoutV2.addWidget(self.operate_option)
        layoutV2.addWidget(self.input_text)

        layoutH2 = QHBoxLayout()
        layoutH2.addLayout(layoutV2)
        layoutH2.addWidget(self.output_textedit)
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
        file_dialog.selectFile("test.v")

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.module_input.setText(file_path)

        self.Gen()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_textedit.toPlainText())
        self.result_label.setText(f"Content copied to clipboard.")

    def file_en_state(self):
        if self.file_en.isChecked():
            self.browse_button.setEnabled(True)
            self.module_input.setEnabled(True)
            self.fileenstate = 1
        else:
            self.browse_button.setEnabled(False)
            self.module_input.setEnabled(False)
            self.fileenstate = 0

    def realtime_state(self):
        if self.realtime.isChecked():
            self.realtimestate = 1
        else:
            self.realtimestate = 0

    def mode_state(self):
        if self.mode_option1.isChecked():
            self.modestate = 1
            self.operate_option.setEnabled(True)
        else:
            self.modestate = 2
            self.operate_option.setEnabled(False)
        self.Gen()

    def align_state(self):
        if self.align_option1.isChecked():
            self.alignstate = 1
        elif self.align_option2.isChecked():
            self.alignstate = 2
        elif self.align_option3.isChecked():
            self.alignstate = 3
        self.Gen()

    def operate_state(self):
        if self.operate_option1.isChecked():
            self.operatestate = 1
        else:
            self.operatestate = 2
        self.Gen()

    def inputtext_change(self):
        if self.realtimestate:
            self.Gen()



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
            for pl in AllPortList:
                if pl != []:
                    if self.alignstate == 1:
                        str = ',\n'.join( [' '*4 + '.' + i[0]
                                    + ' ( ' + (i[0] + i[1]) + ' )' for i in pl])
                    elif self.alignstate == 2:
                        str = ',\n'.join( [' '*4 + '.' + i[0].ljust(l1)
                                    + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                    elif self.alignstate == 3:
                        str = ',\n'.join( [' '*4 + '.' + i[0].ljust(l1)
                                    + '( ' + (i[0].ljust(l1-1)) + ' )' for i in pl])
                    strList += [str]
            str = ',\n\n'.join(strList)

        return str

    def formatDeclare(self, PortList, portArr, init = ""):
        str = ''

        if PortList != []:
            if self.alignstate == 1:
                pass
            elif self.alignstate == 2:
                l1 = max([len(i[0]) for i in PortList if i[1] == ''])
            elif self.alignstate == 3:
                l1 = max([len(i[0]) for i in PortList])
                l2 = max([len(i[1]) for i in PortList])

            if init != "":
                init = " = " + init

                if self.alignstate == 1:
                    str = '\n'.join([portArr + ' ' + (i[1] + min(len(i[1]), 1)*' ' + i[0]) + init + ';' for i in PortList])
                elif self.alignstate == 2:
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                                + i[0]).ljust(l1) + init + ';' for i in PortList])
                elif self.alignstate == 3:
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1].ljust(l2+1)
                                + i[0]).ljust(l1+l2+1) + init + ';' for i in PortList])
            else:
                if self.alignstate == 1:
                    str = '\n'.join([portArr + ' ' + (i[1] + min(len(i[1]), 1)*' ' + i[0]) + ';' for i in PortList])
                elif self.alignstate == 2:
                    str = '\n'.join([portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                                + i[0]) + ';' for i in PortList])
                elif self.alignstate == 3:
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

            if self.alignstate == 1:
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0], i[1]) for i in p])
            elif self.alignstate == 2:
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1]) for i in p])
            elif self.alignstate == 3:
                paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1].ljust(l2)) for i in p])

            if self.alignstate == 1:
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0] + ' ( ' + i[0] + ' )' for i in p]) + ')\n'
            elif self.alignstate == 2:
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0].ljust(l1 + 1)
                            + '( ' + i[0].ljust(l1) + ' )' for i in p]) + ')\n'
            elif self.alignstate == 3:
                paraDef = '#(\n' + ',\n'.join( ['    .'+ i[0].ljust(l1 + 1)
                            + '( ' + i[0].ljust(l1) + ' )' for i in p]) + ')\n'

        if self.modestate == 1:
            if self.alignstate == 1:
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T', '10')])
            elif self.alignstate == 2:
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10')])
            elif self.alignstate == 3:
                preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10'.ljust(l2))])
        elif self.modestate == 2:
            preDec = ''

        paraDec = preDec + paraDec
        return paraDec, paraDef


    def Gen(self):
        if self.fileenstate:
            input_file = self.module_input.text()
            if not input_file:
                return
            with open(input_file, 'rb') as f:
                f_info = chardet.detect(f.read())
                f_encoding = f_info['encoding']
            with open(input_file, encoding=f_encoding) as inFile:
                inText = inFile.read()
        else:
            inText = self.input_text.toPlainText()

        try:
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
        except:
            self.result_label.setText(f"Error!")

    """ generate testbench """
    def GEN(self):
        # write testbench
        if self.modestate == 1:
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
        if self.modestate == 1:
            clk = '''\ninit begin\n    forever #(T/2) clk = ~clk;\nend\n'''
            rst = '''\ninit begin\n    #(T*2) rst_n = 1;\nend\n'''
            self.tb_content += "%s%s" % (clk,rst)

        # print operation
        if self.operatestate == 1 & self.modestate == 1:
            self.tb_content += '''\ninit\nbegin\n\n    $finish;\nend\n'''

        # UUT
        self.tb_content += "\n%s %su_%s (\n%s\n);" % (self.name, self.paraDef, self.name, self.portList)

        # endmodule
        if self.modestate == 1:
            self.tb_content += "\n\nendmodule"

        self.output_textedit.setPlainText(self.tb_content)
        self.result_label.setText("Gen success!")
        self.tb_content = ''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestbenchGenerator()
    window.show()
    sys.exit(app.exec_())



# TODO:
# UUT 名字 回车 i/o
# 时钟频率

