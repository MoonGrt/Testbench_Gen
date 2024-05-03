import sys, re, chardet
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QGroupBox, QRadioButton
from PyQt5.QtGui import QIcon

class TestbenchGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Verilog Testbench Generator')
        self.resize(800, 600)
        self.setWindowIcon(QIcon('images/verilog.png'))

        self.module_label = QLabel('Verilog Module:')
        self.module_input = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self.browse_file)
        self.copy_button = QPushButton('Copy')
        self.copy_button.setFixedWidth(80)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.pattern_text = QTextEdit()
        self.output_textedit = QTextEdit()
        self.result_label = QLabel('')

        self.mode_option = QGroupBox("mode")
        self.mode_option1 = QRadioButton('TestBench')
        self.mode_option2 = QRadioButton('Instance')
        self.mode_option1.setChecked(True)  # Set default option
        mode_option_layout = QHBoxLayout()
        mode_option_layout.addWidget(self.mode_option1)
        mode_option_layout.addWidget(self.mode_option2)
        self.mode_option.setLayout(mode_option_layout)

        self.align_option = QGroupBox("align")
        self.align_option1 = QRadioButton('None')
        self.align_option2 = QRadioButton('Half')
        self.align_option3 = QRadioButton('Full')
        self.align_option1.setChecked(True)  # Set default option
        align_option_layout = QHBoxLayout()
        align_option_layout.addWidget(self.align_option1)
        align_option_layout.addWidget(self.align_option2)
        align_option_layout.addWidget(self.align_option3)
        self.align_option.setLayout(align_option_layout)

        # layout
        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(self.module_label)
        layoutH1.addWidget(self.module_input)
        layoutH1.addWidget(self.browse_button)
        layoutH1.addWidget(self.copy_button)

        layoutV2 = QVBoxLayout()
        layoutV2.addWidget(self.mode_option)
        layoutV2.addWidget(self.align_option)
        layoutV2.addWidget(self.pattern_text)

        layoutH2 = QHBoxLayout()
        layoutH2.addLayout(layoutV2)
        layoutH2.addWidget(self.output_textedit)
        layoutH2.setStretch(0, 3)
        layoutH2.setStretch(1, 7)

        layoutV1 = QVBoxLayout()
        layoutV1.addLayout(layoutH1)
        layoutV1.addLayout(layoutH2)
        layoutV1.addWidget(self.result_label)

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
        # QMessageBox.information(self, 'Copied', 'Content copied to clipboard.')
        self.result_label.setText(f"Content copied to clipboard.")


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
            # l2 = max([len(i[1]) for i in PortList])

            strList = []
            for pl in AllPortList:
                if pl != []:
                    # str = ',\n'.join( [' '*4 + '.' + i[0].ljust(l1)
                    #                   + '( ' + (i[0].ljust(l1) + i[1].ljust(l2))
                    #                   + ' )' for i in pl])
                    str = ',\n'.join( [' '*4 + '.' + i[0].ljust(l1)
                                      + '( ' + (i[0].ljust(l1-1))
                                      + ' )' for i in pl])
                    strList += [str]

            str = ',\n\n'.join(strList)

        return str

    def formatDeclare(self, PortList, portArr, initial = ""):
        str = ''

        if PortList != []:
            l1 = max([len(i[0]) for i in PortList if i[1] == ''])

            if initial != "":
                initial = " = " + initial
                str = '\n'.join( [portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                               + i[0]).ljust(l1) + initial + ';' for i in PortList])
            else:
                str = '\n'.join( [portArr.ljust(4) + ' ' + (i[1] + min(len(i[1]), 1)*' '
                               + i[0]) + ';' for i in PortList])
        return str

    def formatPara(self, ParaList):
        paraDec = ''
        paraDef = ''
        if ParaList != []:
            s = '\n'.join(ParaList)
            pat = r'([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*([\w\W]*?)\s*[;,)]'
            p = re.findall(pat, s)

            l1 = max([len(i[0]) for i in p])
            # l2 = max([len(i[1]) for i in p])
            # paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1].ljust(l2)) for i in p])
            paraDec = '\n'.join( ['parameter %s = %s;' % (i[0].ljust(l1 + 1), i[1]) for i in p])
            paraDef = '#(\n' +',\n'.join( ['    .'+ i[0].ljust(l1 + 1)
                        + '( ' + i[0].ljust(l1 ) + ' )' for i in p]) + ')\n'
        else:
            l1 = 6
            # l2 = 2
        # preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10'.ljust(l2))])
        preDec = '\n'.join(['parameter %s = %s;\n' % ('T'.ljust(l1+1), '10')])
        paraDec = preDec + paraDec
        return paraDec, paraDef


    def Gen(self):
        input_file = self.module_input.text()
        with open(input_file, 'rb') as f:
            f_info = chardet.detect(f.read())
            f_encoding = f_info['encoding']
        with open(input_file, encoding=f_encoding) as inFile:
            inText = inFile.read()

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

        self.tb_content = ''
        self.Testbench_Gen()
        # self.Instance_Gen()

    """ generate testbench """
    def Testbench_Gen(self):
        # write testbench
        self.tb_content += '`timescale 1ns / 1ps\n'
        self.tb_content += "module tb_%s;\n" % self.name

        # module_parameter_port_list
        if(self.paraDec!=''):
            self.tb_content += "\n// %s Parameters\n%s\n" % (self.name, self.paraDec)

        # list_of_port_declarations
        if(self.input != ''):
            self.tb_content += "\n// %s Inputs\n%s\n" % (self.name, self.input)
        if(self.output != ''):
            self.tb_content += "\n// %s Outputs\n%s\n" % (self.name, self.output)
        if(self.inout != ''):
            self.tb_content += "\n// %s Inouts\n%s\n" % (self.name, self.inout)

        # print clock
        clk = '''\ninitial\nbegin\n    forever #(T/2) clk = ~clk;\nend\n'''
        rst = '''\ninitial\nbegin\n    #(T*2) rst_n = 1;\nend\n'''
        self.tb_content += "%s%s" % (clk,rst)

        # print operation
        self.tb_content += '''\ninitial\nbegin\n\n    $finish;\nend\n'''

        # UUT
        self.tb_content += "\n%s %su_%s (\n%s\n);\n" % (self.name, self.paraDef, self.name, self.portList)

        # endmodule
        self.tb_content += "endmodule"

        self.output_textedit.setPlainText(self.tb_content)

    """ generate instance """
    def Instance_Gen(self):
        # write Instance
        # module_parameter_port_list
        if(self.paraDec!=''):
            self.tb_content += "\n// %s Parameters\n%s\n" % (self.name, self.paraDec)

        # list_of_port_declarations
        if(self.input != ''):
            self.tb_content += "\n// %s Inputs\n%s\n" % (self.name, self.input)
        if(self.output != ''):
            self.tb_content += "\n// %s Outputs\n%s\n" % (self.name, self.output)
        if(self.inout != ''):
            self.tb_content += "\n// %s Inouts\n%s\n" % (self.name, self.inout)

        # UUT
        self.tb_content += "\n%s %su_%s (\n%s\n);\n" % (self.name, self.paraDef, self.name, self.portList)

        self.output_textedit.setPlainText(self.tb_content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestbenchGenerator()
    window.show()
    sys.exit(app.exec_())
