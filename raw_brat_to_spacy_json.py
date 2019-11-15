import pandas as pd
import os
from glob import glob
from src.converter.brat_to_rasa_format import standoff_to_entity_offset
from src.converter.rasa_to_spacy_json import rasa_to_spacy_json

PROJECT_ROOT = config.PROJECT_ROOT

path = os.path.join(PROJECT_ROOT, "path to manually verified brat files")


def sort_ascending_order_brat():
    """
    sort brat format files in ascending order of first offset of entities
    genrates csv files at same place as original brat format files
    :return: None
    """
    for index, file in enumerate(glob(path + "*.ann")):
        file_name = file.replace(path, "")
        temp_df = pd.read_csv(file, sep="\t", header=None, lineterminator='\n', index_col=False, quoting=3,
                              quotechar="")
        first_offset_col = [int(i.split()[1]) for i in temp_df[1]]
        temp_df = temp_df.assign(first_offset=first_offset_col)
        temp_df.sort_values(by="first_offset", inplace=True)
        temp_df.drop(["first_offset"], inplace=True, axis=1)
        outpath = path + file_name.split(".")[0] + "_sorted" + ".ann"
        if not os.path.isfile(outpath):
            temp_df.to_csv(outpath, sep="\t", header=None, index=None, quoting=3)


def convert_brat_to_rasa_bulk():
    file_list = []
    ann_files = []
    txt_files = []
    for index, file in enumerate(glob(path + "*.*")):
        file_name = file.replace(path, "")
        if file_name.endswith(".txt"):
            txt_files.append(file_name)
        if file_name.__contains__("sorted"):
            ann_files.append(file_name)

    for f in txt_files:
        temp_txt_fname = f.split(".")[0]
        for i in ann_files:
            temp_ann_fname = i.split(".")[0]
            if temp_txt_fname == temp_ann_fname.replace("_sorted", ""):
                file_list.append((f, i))

    for (txt, ann) in file_list:
        txt_fname = path + txt
        ann_fname = path + ann
        rasa_fname = path + ann.replace(".ann", ".json")
        print("======================================")
        print(txt_fname, ann_fname, rasa_fname)
        if not os.path.isfile(rasa_fname):
            standoff_to_entity_offset(txt_fname, ann_fname, rasa_fname)


def convert_rasa__to_spacy_json_bulk():
    for file in glob(path + "*.json"):
        rasa_path = file
        spacy_json_path = path + file.replace(path, "").split(".")[0] + "_filtered_spacy.json"
        rasa_to_spacy_json(rasa_path, spacy_json_path)


if __name__ == '__main__':
    pass
    # sort_ascending_order_brat()
    # convert_brat_to_rasa_bulk()
    # convert_rasa__to_spacy_json_bulk()
