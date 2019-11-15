import json
import spacy
from spacy.gold import biluo_tags_from_offsets
import os

nlp = spacy.load(config.DEPLOYED_MODEL_TEXT)


def entity_offset_to_bilou(rasa_path,
                           bilou_path, filtered_txt_path):
    """
    convert entity offset to bilou format
    :param rasa_path:
    :param bilou_path:
    :param filtered_txt_path:
    :return:
    """
    filtered_sent_counter = 0
    with open(rasa_path) as rasa_file, open(bilou_path, "w") as bilou_file, open(filtered_txt_path,
                                                                                 "w") as filtered_text_file:
        rasa_format = json.load(rasa_file)
        for counter, section in enumerate(rasa_format["rasa_nlu_data"]["common_examples"]):
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
                    print(text)
                    print(bilou_tags)
                    break
            tokens = [t.text for t in doc]
            assert len(bilou_tags) == len(tokens)

            if error_in_entity_span is False:
                filtered_text_file.write(text + "\n")
                filtered_sent_counter += 1
                for u, v in zip(tokens, bilou_tags):
                    temp = u + "\t" + v + "\n"
                    bilou_file.write(temp)

            if counter == len(rasa_format["rasa_nlu_data"]["common_examples"]) - 1:  # end of file
                pass
            else:
                bilou_file.write(" \n")
        print("total no. of sentences", counter)
        print("filtered sentence", filtered_sent_counter)
        print("problematic sentences", counter - filtered_sent_counter)


if __name__ == '__main__':
    PROJECT_ROOT = "" // put path here
    rasa_path = os.path.join(PROJECT_ROOT, "/manually_tagged_subset/fixed_enron_ner_1.json")
    bilou_path = os.path.join(PROJECT_ROOT, "/manually_tagged_subset/fixed_enron_ner_1_fileterd.bilou")
    filtered_text = os.path.join(PROJECT_ROOT, "/manually_tagged_subset/fixed_enron_ner_1_fileterd.txt")

    entity_offset_to_bilou(rasa_path, bilou_path, filtered_text)
