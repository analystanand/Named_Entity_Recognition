import json
import os

def standoff_to_entity_offset(txt_path, ann_path, rasa_file):
    """
    convert brat standoff format to entity offset format
    :param txt_path: txt file path from brat
    :param ann_path: ann file path for respective text file from brat
    :param rasa_file: output file path
    :return:
    """
    rasa_format = {"rasa_nlu_data": {"common_examples": []}}
    sentence_list = []

    with open(txt_path) as txt_file:
        for sent in txt_file.read().split("\n"):
            if sent:
                sentence_list.append(sent)

    entity_counter = 0
    previous_cur_pos = 0
    cursor_pos = len(sentence_list[0])  # first sentence length

    with open(ann_path) as ann_file:
        tag_list = ann_file.read().split("\n")

        for index in range(len(sentence_list)):
            text = sentence_list[index]
            temp_entites = []
            for i, ann in enumerate(tag_list[entity_counter:]):
                if ann:
                    entity, start, end = ann.split("\t")[1].split()[0], ann.split("\t")[1].split()[1], \
                                         ann.split("\t")[1].split()[2]
                    value = ann.split("\t")[2]
                    if int(end) <= cursor_pos:  # when end value is less than length of current sentence
                        if index == 0:  # special case for first sentence
                            temp_dict = {"start": int(start), "end": int(end), "value": value, "entity": entity}
                        else:
                            temp_dict = {"start": int(start) - previous_cur_pos - 1,
                                         "end": int(end) - previous_cur_pos - 1,
                                         "value": value, "entity": entity}
                        temp_entites.append(temp_dict)
                        if index == len(sentence_list) - 1 and i == len(
                                tag_list) - entity_counter - 1:  # special case for last sent
                            entities = temp_entites
                            if test_entity_offset_check(text, entities):
                                rasa_format["rasa_nlu_data"]["common_examples"].append(
                                    {"text": text, "entities": entities})
                            else:
                                print(entities)
                                print("Error in Entities,Exiting Program")
                                exit()
                    else:
                        entities = temp_entites
                        if test_entity_offset_check(text, entities):
                            rasa_format["rasa_nlu_data"]["common_examples"].append({"text": text, "entities": entities})
                        else:
                            print("Error in Entities,Error in Entities,Exiting Program")
                            exit()
                        entity_counter += len(temp_entites)
                        previous_cur_pos = cursor_pos
                        cursor_pos += len(sentence_list[index + 1]) + 1
                        break

        print("No. of sentences", len(sentence_list))
    with open(rasa_file, "w") as json_file:
        json.dump(rasa_format, json_file)


def test_entity_offset_check(text, entities):
    """
    :param text:
    :param entities:
    :return: True if entities span are correct or not w.r.t sentence
    """
    flag = True
    for ent in entities:
        if text[ent["start"]:ent["end"]] != ent["value"]:
            flag = False
            return flag
    return flag


def check_rasa_format(path):
    """
    check rasa file are filled with correct span of entities for each sentences
    :param rasa_path:
    :return:
    """
    with open(path, "r") as rasa_file:
        rasa_format = json.load(rasa_file)
    for index, section in enumerate(rasa_format["rasa_nlu_data"]["common_examples"]):
        text = section["text"]
        entities = section["entities"]
        if test_entity_offset_check(text, entities):
            pass
        else:
            print("Entities span is wrong")


if __name__ == '__main__':
    PROJECT_ROOT = "" //put root directory path
    txt_path = os.path.join(PROJECT_ROOT,
                            "sample.txt")
    ann_path = os.path.join(PROJECT_ROOT,
                            "sample.ann")
    rasa_path = os.path.join(PROJECT_ROOT,
                             "sample.json")

    standoff_to_entity_offset(txt_path, ann_path, rasa_path)
    check_rasa_format(rasa_path)
