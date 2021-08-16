import stability
import pandas as pd

class Evaluation:
    """
    Evaluate stability (sliding, overturning) in accordance with NVE's guidelines/
    directives

    """
    
    def __init__(self, dam, levels):
        """
        Parameters
        ----------
        dam : instance of Dam
        levels: list
            List of water levels (HRV, DFV, MFV)

        Returns
        -------
        None.

        """
        self.dam = dam
        self.levels = levels
    
    def stability(self):
        """
        Calculate dam stability for the given water levels

        Returns
        -------
        list
            List of stability coefficients
        """
        stab_list = []
        for level in self.levels:
            if level == min(self.levels):
                stab_list.append(
                    stability.Stability(self.dam, level)
                    )
            else:
                stab_list.append(
                    stability.Stability(self.dam, level, ice = 0)
                    )
        return stab_list
    
    def glidning(self):
        """
        Evaluate stability coefficients by comparing them to
        threshold values from NVE's guidelines (sliding)

        Returns
        -------
        list
            List of tuples:
            - failure mode (sliding)
            - water level name (HRV, DFV, MFV)
            - pillar name
            - stability coefficient
            - threshold
            - stability (yes/ no)
        """
        gl_list = [i.glidning() for i in self.stability()]
        
        gr_normal = 1.5
        gr_ulykke = 1.1
        pl_normal = 1.4
        pl_ulykke = 1.1
        
        result_list = []
        
        for (level, gl) in zip(self.levels, gl_list):
            
            if level == max(self.levels):
                level_name = 'MFV'
            elif level == min(self.levels):
                level_name = 'HRV + is'
            else:
                level_name = 'DFV'
            
            for (gl_i, p) in zip(gl, self.dam.pillars):
                
                if p.dam_type.startswith('Gr'):
                    normal = gr_normal
                    ulykke = gr_ulykke
                elif p.dam_type.startswith('Pl'):
                    normal = pl_normal
                    ulykke = pl_ulykke
                    
                if level == max(self.levels):
                    threshold = ulykke
                else:
                    threshold = normal
                    
                if gl_i >= threshold:
                    result = 'ok'
                else:
                    result = 'ikke ok'
                
                result_list.append(
                    ['Glidning', level_name, p.name, round(gl_i, 2),
                     threshold, result]
                    )
        
        return result_list
    
    def velting(self):
        """
        Evaluate stability coefficients by comparing them to
        threshold values from NVE's guidelines (overturning)

        Returns
        -------
        list
            List of tuples:
            - failure mode (overturning)
            - water level name (HRV, DFV, MFV)
            - pillar name
            - stability coefficient
            - threshold
            - stability (yes/ no)
        """
        vm_list = [i.velting_moment() for i in self.stability()]
        vr_list = [i.velting_resultant() for i in self.stability()]
        
        vm_normal = 1.4
        vm_ulykke = 1.3
        
        vr_normal = 1 / 12
        vr_ulykke = 1 / 6
        
        result_list = []
        
        for (level, vm, vr) in zip(self.levels, vm_list, vr_list):
            
            if level == max(self.levels):
                level_name = 'MFV'
            elif level == min(self.levels):
                level_name = 'HRV + is'
            else:
                level_name = 'DFV'
            
            for (vm_i, vr_i, p) in zip(vm, vr, self.dam.pillars):
                
                if p.dam_type.startswith('Gr'):
                    normal = vr_normal
                    ulykke = vr_ulykke
                    
                    if level == max(self.levels):
                        threshold = ulykke
                    else:
                        threshold = normal
                        
                    dist = p.right_contact().x - p.left_contact().x
                    min_dist = dist * threshold
                    max_dist = dist - (dist * threshold)
                    
                    if vr_i >= min_dist and vr_i <= max_dist:
                        result = 'ok'
                    else:
                        result = 'ikke ok'
                    result_list.append(
                        ['Velting', level_name, p.name, round(vr_i, 2),
                        f'{round(min_dist, 2)} - {round(max_dist, 2)}',
                        result]
                        )
                    
                    
                elif p.dam_type.startswith('Pl'):
                    normal = vm_normal
                    ulykke = vm_ulykke
                    
                    if level == max(self.levels):
                        threshold = ulykke
                    else:
                        threshold = normal
                        
                    if vm_i >= threshold:
                        result = 'ok'
                    else:
                        result = 'ikke ok'
                    
                    result_list.append(
                        ['Velting', level_name, p.name, round(vm_i, 2),
                         threshold, result]
                        )
        return result_list
    
    def write_file(self, file_name):
        """
        Create simple overview of results ofstability calculations
        as Excel file

        Returns
        -------
        None.
        
        """
        gl = self.glidning()
        ve = self.velting()
        
        header = ['Sikkerhet mot', 'Lasttilfelle', 'Damseksjon',
                  'Sikkherhetsfaktor', 'Sikkerhetskrav', 'Stabilitet']
        df = pd.DataFrame(gl + ve, columns = header)
        df.to_excel(file_name, index = False)
        print(f'Evaluation written to Excel file ({file_name})')    