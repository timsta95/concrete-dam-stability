import stability, evaluation

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Table, TableStyle, Paragraph
from svglib.svglib import svg2rlg
from PyPDF2 import PdfFileMerger, PdfFileReader

class Report:
    """
    Create pdf report containing calculations and figures;
    current layout: one page per pillar
    """
    def __init__(self, dam, levels):
        self.dam = dam
        self.levels = levels
        
    def unlevel(self, obj):
        #removes unnecessary levels from nested lists
        while isinstance(obj, list) and len(obj) == 1:
            obj = obj[0]
        if isinstance(obj, list):
            return [self.unlevel(item) for item in obj]
        else:
            return obj
        
    def rearrange_loads(self):
        #necessary to match the order of loads to the order of moments
        loads = [stability.Stability(self.dam, l).loads() for l in self.levels]
        collected = []
        for loads_level in loads:
            collected.append(list(zip(*loads_level)))
        return collected
            
        
    def calc_arms(self):
        #calculate moment arms from moments and loads, return 0 if attempting
        #to divide by zero
        l = self.rearrange_loads()
        m = [stability.Stability(self.dam, lv).moment() for lv in self.levels]
        loads, moments = np.array(l), np.array(m)
        return np.divide(
            moments, loads, out = np.zeros_like(moments), where = loads != 0
            )
        
        
    def create_level_tables(self):
        #summaries of stability analyses at each water level
        
        #loads (rearranged), moments, moment arms
        l = self.rearrange_loads()
        m = [stability.Stability(self.dam, lv).moment() for lv in self.levels]
        a = self.calc_arms()
        
        load_names = ('Islast', 'Vanntrykk', 'Vannvekt', 'Overtopping',
                      'Opptrykk', 'Egenvekt')
        
        collected = []
        
        for level, loads, moments, arms in zip(self.levels, l, m, a):
            
            if level == max(self.levels):
                level_name = 'MFV'
            elif level == min(self.levels):
                level_name = 'HRV + is'
            else:
                level_name = 'DFV'
                
            dfs = []
                
            col_names = (level_name, 'F [kN]', 'a [m]', 'M [kNm]')
            
            for load, moment, arm in zip(loads, moments, arms):
                
                df = pd.DataFrame(list(zip(load_names, load, arm, moment)),
                                  columns = col_names)
                
                if level != min(self.levels):
                    df.iloc[0, 1:4] = 0
                    
                df = df.round(2)
                
                dfs.append(df)
             
            collected.append(dfs)
        
        #remove unnecessary levels from nested list of pandas dataframes
        rearranged = self.unlevel([list(zip(*collected))])
        return rearranged
    
    def create_summary_tables(self):
        
        ev = evaluation.Evaluation(self.dam, self.levels)
        glidning, velting = ev.glidning(), ev.velting()
        
        no_pillars = int(len(glidning) / len(self.levels))
        
        gl_rearranged, ve_rearranged = [], []
        
        for i in range(0, no_pillars):
            gl_rearranged.append(glidning[i::no_pillars])
            ve_rearranged.append(velting[i::no_pillars])
        
        dfs = []
            
        for gl, ve in zip(gl_rearranged, ve_rearranged):
            
            col_names = (gl[0][2], 'HRV + is', 'DFV', 'MFV')
            first_col =  ('Glidning', 'Velting', 'Sikkerhet')
            
            level_names = [i[1] for i in gl]
            l_idx = [level_names.index(i) for i in col_names[1:]]          
            
            gl_vals, gl_ok = [], []
            for i in gl:
                if isinstance(i[4], str):
                    gl_vals.append(f'{i[3]} i [{i[4]}]')
                else:
                    gl_vals.append(f'{i[3]} >= {i[4]}')
                gl_ok.append(i[5])
                
            ve_vals, ve_ok = [], []
            for i in ve:
                if isinstance(i[4], str):
                    ve_vals.append(f'{i[3]} in [{i[4]}]')
                else:
                    ve_vals.append(f'{i[3]} >= {i[4]}')
                ve_ok.append(i[5])
            
            ok = []
            for i, j in zip(gl_ok, ve_ok):
                if i == 'ok' and j == 'ok':
                    ok.append('ok')
                else:
                    ok.append('ikke ok')
                    
            hrv_col = gl_vals[l_idx[0]], ve_vals[l_idx[0]], ok[l_idx[0]]
            dfv_col = gl_vals[l_idx[1]], ve_vals[l_idx[1]], ok[l_idx[1]]
            mfv_col = gl_vals[l_idx[2]], ve_vals[l_idx[2]], ok[l_idx[2]]
                    
            
            df = pd.DataFrame(list(zip(first_col, hrv_col, dfv_col, mfv_col)),
                              columns = col_names)
            dfs.append(df)
                    
        return dfs
    
    def create_images(self):
        
        new_dir = '../img'
        
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        #specificy color codes for loads (optional)
        load_colors = {'Islast': 'blue', 'Opptrykk': 'blue',
                       'Vanntrykk': 'blue', 'Vannvekt': 'blue',
                       'Overtopping': 'blue'}
        
        #pillars
        pillars = self.dam.pillars
        
        file_dirs = []
        
        for level in self.levels:
            
            if level == min(self.levels):
                ice = 100
                level_name = 'HRV + is'
            elif level == max(self.levels):
                ice = 0
                level_name = 'MFV'
            else:
                ice = 0
                level_name = 'DFV'
            
            #get segments for level "level" as list of lists of segments
            #(per pillar)
            segs = stability.Stability(self.dam, level, ice).draw_per_pillar()
            
            for p, segs_p in zip(pillars, segs):
                
                pillar_name = p.name
                
                #set up figure and axes
                fig, ax = plt.subplots()
                ax.set_aspect('equal', 'datalim')
                
                #pivot point
                pp = p.right_contact()
                ax.plot(pp.x, pp.y, 'o', color = 'black')
                
                #plot segments
                for seg in segs_p:
                    if seg.name in load_colors.keys():
                        fc = load_colors[seg.name]
                    else:
                        fc = 'gray'
                    if seg.load() > 0:
                        xs, ys = seg.poly.exterior.xy
                        ax.fill(xs, ys, fc = fc, ec = 'black', alpha = 0.3)
                        
                        #plot centroids
                        if seg.name in ('Vanntrykk', 'Islast'):
                            symb = '>'
                        elif seg.name in ('Opptrykk'):
                            symb = '^'
                        else:
                            symb = 'v'
                        
                        xs, ys = seg.centroid().xy
                        ax.plot(xs, ys, symb, color = 'yellow')
                        
                ax.set_title(f'{level_name}: Tverrsnitt {pillar_name}')
                ax.set_xlabel('X [m]')
                ax.set_ylabel('Høyde over havet [m]')
                    
                file_dir = f'{new_dir}/{level_name}_{pillar_name}.svg'
                fig.savefig(file_dir, format = 'svg')
                plt.close(fig)
                file_dirs.append(file_dir)
                
        print(f'Images created ({new_dir})')
                
        rearranged = []
        for i in range(0, len(pillars)):
            rearranged.append(file_dirs[i::len(pillars)])
        
        return rearranged
    
    def create_report(self):
        
        new_dir = '../result'
        
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        summary_tables = self.create_summary_tables()
        level_tables = self.create_level_tables()
        fig_dirs = self.create_images()
        pillars = self.dam.pillars
        
        cwidth = 24
        
        file_dirs = []
    
        for summary, level, figs, p in zip(
                summary_tables, level_tables, fig_dirs, pillars
                ):
            
            t_style = TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                              ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                              ('INNERGRID', (0,0), (-1,-1), 0.25,
                               colors.black)])
            
            name = list(summary.columns)[0]
            file_dir = f'{new_dir}/{name}_summary.pdf'
            file_dirs.append(file_dir)
            
            c = canvas.Canvas(file_dir, pagesize = A4)
            width, height = A4
            
            for idx, l in enumerate(level):
                table = l.to_records(index = False).tolist()
                table.insert(0, list(l.columns))
                t = Table(table, colWidths = cwidth * mm)
                t.setStyle(t_style)
                t.wrapOn(c, width, height)
                t.drawOn(c, 0.1 * width, (0.55 - idx * 0.2) * height)
                
            for idx, fig in enumerate(figs):
                drawing = svg2rlg(fig)
                sx = sy = 0.4
                drawing.width = drawing.minWidth() * sx
                drawing.height = drawing.height * sy
                drawing.scale(sx, sy)
                drawing.wrapOn(c, width, height)
                drawing.drawOn(c, 0.58 * width, (0.54 - idx * 0.2) * height)
                
            table = summary.to_records(index = False).tolist()
            table.insert(0, list(summary.columns))
            t = Table(table, colWidths = (cwidth + 10) * mm)
            
            for row, values, in enumerate(table):
                for column, value in enumerate(values):
                    if value == 'ikke ok':
                        t_style.add(
                            'BACKGROUND', (column, row),
                            (column, row), colors.red
                            )
                    if value == 'ok':
                        t_style.add(
                            'BACKGROUND', (column, row),
                            (column, row), colors.green
                            )
            t.setStyle(t_style)
            
            t.wrapOn(c, width, height)
            t.drawOn(c, 0.18 * width, 0.75 * height)
            
            styles = getSampleStyleSheet()    
            ptext = f'{name} er beregnet som: {p.dam_type}'
            p = Paragraph(ptext, style = styles['Normal'])
            p.wrapOn(c, 150 * mm, 25 * mm)
            p.drawOn(c, 0.17 * width , 0.84 * height)
            
            styles.add(ParagraphStyle(name = 'Header',
                                      parent = styles['Heading1'],
                                      alignment = TA_CENTER,
                                      fontSize = 16
                                      ))
            
            ptext = f'Stabilitetsberegning: {name}'
            p = Paragraph(ptext, style = styles['Header'])
            p.wrapOn(c, 150 * mm, 40 * mm)
            p.drawOn(c, 0.17 * width , 0.9 * height)
            
            c.save()
            
        file_dir = f'{new_dir}/Dam_summary.pdf'
        merger = PdfFileMerger()
        
        for pdf_dir in file_dirs:
            with open(pdf_dir,'rb') as pdf:
                merger.append(PdfFileReader(pdf))
            
        merger.write(file_dir)
        merger.close()
        
        for pdf_dir in file_dirs:
            os.remove(pdf_dir)
            
        return f'PDFs created ({new_dir})'
        