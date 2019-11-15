import os
from collections import OrderedDict
import json
import spacy
from spacy.gold import biluo_tags_from_offsets

nlp = spacy.load(config.DEPLOYED_MODEL_TEXT)


def rasa_to_spacy_json(rasa_path, spacy_json_path):
    """
    convert rasa format files to spacy json files for training
    :param rasa_path:
    :param spacy_json_path:
    :return:
    """
    filtered_sent_counter = 0
    spacy_list = []

    with open(rasa_path) as rasa_file, open(spacy_json_path, "w") as spacy_json_file:

        rasa_format = json.load(rasa_file)
        for counter, section in enumerate(rasa_format["rasa_nlu_data"]["common_examples"]):
            temp_para = OrderedDict()
            text = section["text"]
            entities = []
            for i in section["entities"]:
                entities.append((i["start"], i["end"], i["entity"]))
            doc = nlp(text)
            bilou_tags = biluo_tags_from_offsets(doc, entities)
            error_in_entity_span = False

            for i in bilou_tags:  # character offset does not match with tokens,flag it and skip it
                if i == "-":
                    error_in_entity_span = True
                    break
            tokens = [t.text for t in doc]
            orth_list = [t.orth_ for t in doc]
            tags_list = [t.tag_ for t in doc]
            assert len(bilou_tags) == len(tokens)

            if error_in_entity_span is False:
                temp_token = []
                for i, (orth, tag, bilou) in enumerate(zip(orth_list, tags_list, bilou_tags)):
                    temp_dict = OrderedDict()
                    temp_dict["id"] = i
                    temp_dict["orth"] = str(orth)
                    temp_dict["tag"] = str(tag)
                    temp_dict["ner"] = str(bilou)
                    temp_token.append(temp_dict)
                temp_para["id"] = filtered_sent_counter
                temp_para["paragraphs"] = [{"raw": text, "sentences": [{"tokens": temp_token}]}]
                # print(temp_para["id"])
                spacy_list.append(temp_para)
                filtered_sent_counter += 1

        json.dump(spacy_list, spacy_json_file, indent=2)

        print("total no. of sentences", counter)
        print("filtered sentence", filtered_sent_counter)
        print("problematic sentences", counter - filtered_sent_counter)


if __name__ == '__main__':
    PROJECT_ROOT = "" //put path here
    rasa_file = os.path.join(PROJECT_ROOT, "experiment/test/test.json")
    spacy_json = os.path.join(PROJECT_ROOT, "experiment/test/test_filtered_spacy.json")
    rasa_to_spacy_json(rasa_file, spacy_json)
