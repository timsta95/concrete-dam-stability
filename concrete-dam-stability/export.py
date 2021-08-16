import stability, evaluation
import os
import pandas as pd

class Export:
    """
    Export evaluations and dam geometries as Excel files;
    files can then be read by Civil 3D Dynamo when creating
    3D dwg files
    - names: Segment names
    - axes: Segment axes
    - weights: Segment weights
    - widths: Segment widths
    - x: X coordinates of segment vertices
    - y: Y coordinates of segment vertices
    """    
    def __init__(self, dam, levels):
        self.dam = dam
        self.levels = levels
        
    def export(self):
        
        new_dir = '../export'
        
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
 
        segs_list = []
        for level in self.levels:
            if level == min(self.levels):
                segs_list.append(
                    stability.Stability(self.dam, level).draw()
                    )
            else:
                segs_list.append(
                    stability.Stability(self.dam, level, ice = 0).draw()
                    )
        
        eval_dir = f'{new_dir}/evaluation.xlsx'       
        evaluation.Evaluation(self.dam, self.levels).write_file(eval_dir)
                
        filtered = [[i for i in segs if i.load() > 0] for segs in segs_list]
        
        names = [[i.name for i in segs] for segs in filtered]
        axes = [[i.axis for i in segs] for segs in filtered]
        weights = [[i.spec_weight for i in segs] for segs in filtered]
        widths = [[i.width for i in segs] for segs in filtered]
        x = [[list(i.poly.exterior.coords.xy[0]) for i in segs] for segs in filtered]
        y = [[list(i.poly.exterior.coords.xy[1]) for i in segs] for segs in filtered]

        
        for idx, i in enumerate(self.levels):
            
            if i == min(self.levels):
                name = 'HRV + is'
            elif i == max(self.levels):
                name = 'MFV'
            else:
                name = 'DFV'
            
            data_df = pd.DataFrame(list(zip(names[idx], axes[idx], weights[idx], widths[idx])),
                                   columns =['Names', 'Axes', 'Weights', 'Widths'])
            file_dir = f'{new_dir}/{name}_data.xlsx'
            data_df.to_excel(file_dir, index = False, header = False)
            
            x_df = pd.DataFrame(x[idx])
            file_dir = f'{new_dir}/{name}_x.xlsx'
            x_df.to_excel(file_dir, index = False, header = False)
            
            y_df = pd.DataFrame(y[idx])
            file_dir = f'{new_dir}/{name}_y.xlsx'
            y_df.to_excel(file_dir, index = False, header = False)
        
        return f'Export finished ({new_dir})'