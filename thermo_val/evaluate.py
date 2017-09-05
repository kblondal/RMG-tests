import os
import argparse
import pandas as pd

from data import get_datasets, get_data
from model import ThermoEstimator

def evaluate_performance(dataset_file, 
                        model_kernel='GA'):
    
    # get a list of test table names
    # from files or input
    test_tables = get_datasets(dataset_file)

    # model instantiation
    model = ThermoEstimator(kernel_type=model_kernel)

    # start test evaluation
    performance_dict = {}
    for _, db_name, collection_name in test_tables:

        data = get_data(db_name, collection_name)

        spec_labels = []
        spec_dict = {}
        H298s_true = []
        H298s_pred = []

        comments = []
        
        for db_mol in data:
            smiles_in = str(db_mol["SMILES_input"])
            H298_true = float(db_mol["Hf298(kcal/mol)"]) # unit: kcal/mol
            
            thermo = model.predict_thermo(smiles_in)
            H298_pred = thermo.H298.value_si/4184.0
            
            spec_labels.append(smiles_in)
            H298s_true.append(H298_true)
            H298s_pred.append(H298_pred)
            comments.append(thermo.comment)

        # create pandas dataframe
        test_df = pd.DataFrame(index=spec_labels)
        test_df['SMILES'] = test_df.index

        test_df['H298_pred(kcal/mol)'] = pd.Series(H298s_pred, index=test_df.index)
        test_df['H298_true(kcal/mol)'] = pd.Series(H298s_true, index=test_df.index)

        diff = abs(test_df['H298_pred(kcal/mol)']-test_df['H298_true(kcal/mol)'])
        test_df['H298_diff(kcal/mol)'] = pd.Series(diff, index=test_df.index)
        test_df['Comments'] = pd.Series(comments, index=test_df.index)

        # save test_df for future reference and possible comparison
        test_df_save_path = os.path.join(os.path.dirname(dataset_file),
                                        'test_df_{0}_{1}.csv'.format(db_name, collection_name))
        with open(test_df_save_path, 'w') as fout:
            test_df.to_csv(fout, index=False)

        performance_dict[(db_name, collection_name)] = test_df['H298_diff(kcal/mol)'].describe()['mean']

    return performance_dict

def parseCommandLineArguments():
   
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--datasets', metavar='FILE', type=str, 
        nargs='+', help='a file specifies on which datasets to test')

    return parser.parse_args()

def main():

    args = parseCommandLineArguments()
    dataset_file = args.datasets[0]

    performance_dict = evaluate_performance(dataset_file, 
                                            model_kernel='GA')

    print_str = "\nValidation Test Results"
    for db_name, collection_name in performance_dict:

        performance = performance_dict[(db_name, collection_name)]

        print_str += "\n========================="
        print_str += "\nDatabase: {0}".format(db_name)
        print_str += "\nDataset: {0}".format(collection_name)
        print_str += "\nPerformance (MAE): {0:0.2f} kcal/mol".format(performance)

    print(print_str)
    validataion_summary_path = os.path.join(os.path.dirname(dataset_file),
                                    'validation_summary.txt')
    with open(validataion_summary_path, 'w') as fout:
            fout.write(print_str) 

if __name__ == '__main__':
    main()
