# -*- coding: utf-8 -*-
"""生成上架后运营引擎三张追踪表：投流追踪表 / 达人管线表 / 内容迭代表（活表，黄色可填）。"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

YELLOW = PatternFill('solid', fgColor='FFF2CC')
GREEN = PatternFill('solid', fgColor='D9EAD3')
HEAD = PatternFill('solid', fgColor='2E7D32')
BOLD = Font(bold=True)
WB = Font(bold=True, color='FFFFFF')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
THIN = Border(*[Side(style='thin', color='CCCCCC')]*4)

def hdr(ws, row, n):
    for c in range(1, n+1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEAD; cell.font = WB; cell.alignment = CENTER; cell.border = THIN

def setw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def gen(out_dir, product='产品'):
    wb = Workbook()

    # 投流追踪表
    ws = wb.active; ws.title = '投流追踪'
    ws['A1'] = '%s 投流追踪表（黄色可填，直接ROAS≥1.2续投/综合ROAS≥1.5放大）' % product
    ws['A1'].font = BOLD
    ws.append([])
    ws.append(['日期','预算(USD)','曝光','点击','GMV(VND)','直接ROAS','综合ROAS','自然单占比','决策'])
    ws.append(['示例','10','5400','54','150000','=F3*E3/1000/27000/D3*10','=IF(F3=0,"",(E3+G3*100000)/F3)','0.30','维持'])
    # 简化示例行，公式列留待回填
    ws['G3'] = '=IF(F3=0,"",E3/(D3*10*0.001))'  # 直接ROAS近似（GMV/预算VND）
    ws['H3'] = '=IF(F3=0,"",(E3*1.4)/(D3*10*0.001))'  # 综合ROAS占位
    hdr(ws, 3, 9); setw(ws, [10,12,10,10,14,12,12,12,10])
    for r in range(4, 20):
        for c in range(1, 6):
            ws.cell(row=r, column=c).fill = YELLOW
            ws.cell(row=r, column=c).border = THIN
        for c in range(6, 10):
            ws.cell(row=r, column=c).border = THIN

    # 达人管线表
    ws = wb.create_sheet('达人管线')
    ws['A1'] = '%s 达人管线表（小样先行：先10人校准建联转化率，再扩50→100）' % product
    ws['A1'].font = BOLD
    ws.append([])
    ws.append(['达人','层级','触达','寄样','出片','出单数','样品成本','达人GMV','出单ROI','复投决策'])
    ws.append(['示例A','腰部','已触达','已寄','是','8','57010','920000','=I4/H4','续投'])
    ws['I4'] = '=I4/H4'
    hdr(ws, 3, 10); setw(ws, [14,8,10,8,8,10,12,12,10,10])
    for r in range(4, 30):
        for c in range(1, 9):
            ws.cell(row=r, column=c).fill = YELLOW
            ws.cell(row=r, column=c).border = THIN
        for c in range(9, 11):
            ws.cell(row=r, column=c).border = THIN

    # 内容迭代表
    ws = wb.create_sheet('内容迭代')
    ws['A1'] = '%s 内容迭代表（爆款出3变体；14天播放<500不追投）' % product
    ws['A1'].font = BOLD
    ws.append([])
    ws.append(['视频','发布日','播放','完播率','转化单','是否爆款','变体','淘汰/追投'])
    ws.append(['开箱-惊喜','第1周','3000','0.35','2','是','换开头/场景/口播','追投'])
    hdr(ws, 3, 8); setw(ws, [16,10,12,10,10,10,18,12])
    for r in range(4, 30):
        for c in range(1, 6):
            ws.cell(row=r, column=c).fill = YELLOW
            ws.cell(row=r, column=c).border = THIN
        for c in range(6, 9):
            ws.cell(row=r, column=c).border = THIN

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, '06-投流达人内容追踪表.xlsx')
    wb.calculation = None
    wb.save(out)
    return out

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    prod = sys.argv[2] if len(sys.argv) > 2 else '产品'
    print('生成:', gen(out, prod))
