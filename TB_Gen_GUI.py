import sys, re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
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
        self.copy_button = QPushButton('Copy')
        self.output_textedit = QTextEdit()
        self.result_label = QLabel('')

        layoutH = QHBoxLayout()
        layoutH.addWidget(self.module_label)
        layoutH.addWidget(self.module_input)
        layoutH.addWidget(self.browse_button)
        layoutH.addWidget(self.copy_button)

        layoutV = QVBoxLayout()
        layoutV.addLayout(layoutH)
        layoutV.addWidget(self.output_textedit)
        layoutV.addWidget(self.result_label)

        self.setLayout(layoutV)

        self.browse_button.clicked.connect(self.browse_file)
        self.copy_button.clicked.connect(self.copy_to_clipboard)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Verilog Files (*.v)")
        file_dialog.selectFile("test.v")

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.module_input.setText(file_path)
        
        self.generate_testbench()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_textedit.toPlainText())
        # QMessageBox.information(self, 'Copied', 'Content copied to clipboard.')
        self.result_label.setText(f"Content copied to clipboard.")

    def declare_ports(self, input_ports):
        declare_ports = ''
        for line in input_ports.split(','):
            port_type = "reg " if "reg" in line or "input" in line else "wire"
            line = line.strip().replace("input", "").replace("output", "").replace("reg", "").replace("wire", "").strip()
    
            parts = line.split()
            if len(parts) > 1:
                port_width = parts[0]
                port_name = parts[1]
                declare_ports += f"{port_type} {port_width}\t{port_name};\n"
            else:
                port_width = ''
                port_name = parts[0]
                declare_ports += f"{port_type} \t\t{port_name};\n"
    
        return declare_ports
    
    def connect_parameters(self, ports_str):
        connect_ports = ''
        ports_lines = ports_str.split(",")
        for idx, line in enumerate(ports_lines):
            port_name = line.strip().replace("input", "").replace("output", "").replace("reg", "").replace("wire", "").strip()
    
            parts = port_name.split()
            if len(parts) > 1:
                port_name = parts[1]
            else:
                port_name = parts[0]
    
            connect_ports += f"    .{port_name}({port_name})"
            if idx < len(ports_lines) - 1:
                connect_ports += ",\n"
        return connect_ports
    #TODO: connect 排版

    def connect_ports(self, ports_str):
        connect_ports = ''
        ports_lines = ports_str.split(",")
        for idx, line in enumerate(ports_lines):
            port_name = line.strip().replace("input", "").replace("output", "").replace("reg", "").replace("wire", "").strip()
    
            parts = port_name.split()
            if len(parts) > 1:
                port_name = parts[1]
            else:
                port_name = parts[0]
    
            connect_ports += f"    .{port_name}({port_name})"
            if idx < len(ports_lines) - 1:
                connect_ports += ",\n"
        return connect_ports
    #TODO: connect 排版

    def generate_testbench(self):
        try:
            verilog_file = self.module_input.text()
            with open(verilog_file, "r") as module_file:
                module_content = module_file.read()

            temp = module_content.split("(")[0].split()[-1]
            if  temp != '#':
                module_name = module_content.split("(")[0].split()[-1]
                ports = module_content.split("(")[1].split(")")[0]
                declare_ports_str = self.declare_ports(ports)
                connect_ports_str = self.connect_ports(ports)
            else:
                module_name = module_content.split("(")[0].split()[-2]
                parameters = module_content.split("(")[1].split(")")[0]
                connect_parameters_str = self.connect_parameters(parameters)
                ports = module_content.split("(")[2].split(")")[0]
                declare_ports_str = self.declare_ports(ports)
                connect_ports_str = self.connect_ports(ports)

            tb_content = f"""\
`timescale 1ns/1ns

module {module_name}_tb;

// Parameters
parameter PERIOD = 10;

// Declare signals
{declare_ports_str}
// Clock generation
initial begin
    clk = 0;
    forever #(PERIOD/2) clk = ~clk;
end

// Instantiate module
{module_name} {module_name} (
{connect_ports_str}
);

// Stimulus generation
initial begin
    // Add your stimulus code here
    rst_n = 0;
    #(PERIOD*2) rst_n = 1;
end

// Monitor outputs
always @(posedge clk) begin
    // Add your output monitoring code here
end

endmodule
"""

            self.output_textedit.setPlainText(tb_content)
            self.result_label.setText(f"Verilog testbench file {module_name}_tb.v has been generated.")
        except:
            self.result_label.setText(f"error!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestbenchGenerator()
    window.show()
    sys.exit(app.exec_())
