'''
tb_gen.py -- generate verilog module Testbench
Usage:
    python tb_gen.py FileName.v
'''

import re, sys, chardet

def delComment(Text):
    """ removed comment """
    single_line_comment = re.compile(r"//(.*)$", re.MULTILINE)
    multi_line_comment  = re.compile(r"/\*(.*?)\*/", re.DOTALL)
    Text = multi_line_comment.sub('\n', Text)
    Text = single_line_comment.sub('\n', Text)
    return Text

def delBlock(Text):
    """ removed task and function block """
    Text = re.sub(r'\Wtask\W[\W\w]*?\Wendtask\W', '\n', Text)
    Text = re.sub(r'\Wfunction\W[\W\w]*?\Wendfunction\W', '\n', Text)
    return Text

def findName(inText):
    """ find module name and port list"""
    p = re.search(r'([a-zA-Z_][a-zA-Z_0-9]*)\s*', inText)
    mo_Name = p.group(0).strip()
    return mo_Name

def paraDeclare(inText, portArr):
    """ find parameter declare """
    pat = r'\s'+ portArr + r'\s[\w\W]*?[;,)]'
    ParaList = re.findall(pat, inText)
    return ParaList

def portDeclare(inText, portArr):
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
            t += portDic(ls[-2:])
    return t

def portDic(port) :
    """delet as : input a =c &d;
        return list as : (port, [range])
    """
    pRe = re.compile(r'(.*?)\s*=.*', re.DOTALL)

    pRange = port[0]
    pList  = port[1].split(',')
    pList  = [i.strip() for i in pList if i.strip() != '']
    pList  = [(pRe.sub(r'\1', p), pRange.strip()) for p in pList]

    return pList

def formatPort(AllPortList):
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

def formatDeclare(PortList, portArr, initial = ""):
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

def formatPara(ParaList):
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

def TestBench_gen(input_file):
    """ write testbench to file """
    with open(input_file, 'rb') as f:
        f_info = chardet.detect(f.read())
        f_encoding = f_info['encoding']
    with open(input_file, encoding=f_encoding) as inFile:
        inText = inFile.read()

    # removed comment, task, function
    inText = delComment(inText)
    inText = delBlock(inText)

    # moduel ... endmodule #
    moPos_begin = re.search(r'(\b|^)module\b', inText).end()
    moPos_end = re.search(r'\bendmodule\b', inText).start()
    inText = inText[moPos_begin: moPos_end]

    name = findName(inText)
    paraList = paraDeclare(inText, 'parameter')
    paraDec, paraDef = formatPara(paraList)

    ioPadAttr = ['input', 'output', 'inout']
    input  = portDeclare(inText, ioPadAttr[0])
    output = portDeclare(inText, ioPadAttr[1])
    inout  = portDeclare(inText, ioPadAttr[2])

    portList = formatPort([input, output, inout])
    input  = formatDeclare(input, 'reg', '0')
    output = formatDeclare(output, 'wire')
    inout  = formatDeclare(inout, 'wire')

    # write testbench
    print('`timescale 1ns / 1ps\n')
    print("module tb_%s;\n" % name)

    # module_parameter_port_list
    if(paraDec!=''):
        print("// %s Parameters\n%s\n" % (name, paraDec))

    # list_of_port_declarations
    if(input != ''):
        print("// %s Inputs\n%s\n"  % (name, input ))
    if(output != ''):
        print("// %s Outputs\n%s\n" % (name, output))
    if(inout != ''):
        print("// %s Inouts\n%s\n"  % (name, inout ))

    # print clock
    clk = '''
initial
begin
    forever #(T/2) clk = ~clk;
end'''
    rst = '''
initial
begin
    #(T*2) rst_n = 1;
end'''
    print("%s\n%s" % (clk,rst))

    # print operation
    operation = '''
initial
begin

    $finish;
end
'''
    print(operation)

    # UUT
    print("\n%s %s u_%s (\n%s\n);" % (name, paraDef, name, portList))
    # endmodule
    print("endmodule")


def Instance_gen(input_file):
    """ write testbench to file """
    with open(input_file, 'rb') as f:
        f_info =  chardet.detect(f.read())
        f_encoding = f_info['encoding']
    with open(input_file, encoding=f_encoding) as inFile:
        inText = inFile.read()

    # removed comment,task,function
    inText = delComment(inText)
    inText = delBlock(inText)

    # moduel ... endmodule  #
    moPos_begin = re.search(r'(\b|^)module\b', inText).end()
    moPos_end = re.search(r'\bendmodule\b', inText).start()
    inText = inText[moPos_begin: moPos_end]

    name = findName(inText)
    paraList = paraDeclare(inText, 'parameter')
    paraDec, paraDef = formatPara(paraList)

    ioPadAttr = ['input', 'output', 'inout']
    input  = portDeclare(inText, ioPadAttr[0])
    output = portDeclare(inText, ioPadAttr[1])
    inout  = portDeclare(inText, ioPadAttr[2])

    portList = formatPort([input, output, inout])
    input  = formatDeclare(input, 'reg')
    output = formatDeclare(output, 'wire')
    inout  = formatDeclare(inout, 'wire')

    # write Instance
    # module_parameter_port_list
    if(paraDec != ''):
        print("// %s Parameters\n%s\n" % (name, paraDec))

    # list_of_port_declarations
    if(input != ''):
        print("// %s Inputs\n%s\n"  % (name, input ))
    if(output != ''):
        print("// %s Outputs\n%s\n" % (name, output))
    if(inout != ''):
        print("// %s Inouts\n%s\n"  % (name, inout ))

    # UUT
    print("%s %su_%s (\n%s\n);" % (name, paraDef, name, portList))


if __name__ == '__main__':
    TestBench_gen("./test.v")
    Instance_gen("./test.v")
