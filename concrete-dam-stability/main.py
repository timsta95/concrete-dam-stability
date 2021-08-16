import dam_setup, report, export
import time

def main():
    """
    Main function
    
    """
    #start timer
    start_time = time.time()
    print(f'Started at {time.ctime()}')
    
    #load dam and levels from setup.py
    dam = dam_setup.dam_construction
    levels = dam_setup.levels

    #stability analysis & reports
    print(report.Report(dam, levels).create_report()) #create reports
    print(export.Export(dam, levels).export()) #export data to dynamo
    
    #end timer, print run time
    time_diff = round(time.time() - start_time, 2)
    print(f'Elapsed after {time_diff} seconds')

if __name__ == '__main__':
    main()