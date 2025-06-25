import gedcom.parser
import gedcom.element.individual
import gedcom.element.family

def find_relatives(gedcom_parser):
    relatives = set()
    related_families = set()
    target_individual = None
    families = {}
    individuals = {}
    
    # First pass: Map all individuals and families
    for element in gedcom_parser.get_root_child_elements():
        if isinstance(element, gedcom.element.individual.IndividualElement):
            individuals[element.get_pointer()] = element
        elif isinstance(element, gedcom.element.family.FamilyElement):
            families[element.get_pointer()] = element
    
    # Find Clemens
    for individual_id, individual in individuals.items():
        name = individual.get_name()
        if "clemens" in name[0].lower() and "koldehoff" in name[0].lower():
            target_individual = individual
            relatives.add(individual)
            break
    
    def add_relatives(person):
        if not person:
            return
        
        person_id = person.get_pointer()
        relatives.add(person)
        
        # Find all families where person is a spouse or child
        for family_id, family in families.items():
            if person_id in [family.get_husband_id(), family.get_wife_id()] or person_id in family.get_child_ids():
                related_families.add(family)
                
                # Add spouse
                spouse_id = family.get_husband_id() if person_id == family.get_wife_id() else family.get_wife_id()
                if spouse_id and spouse_id in individuals:
                    if individuals[spouse_id] not in relatives:
                        add_relatives(individuals[spouse_id])
                
                # Add children
                for child_id in family.get_child_ids():
                    if child_id in individuals and individuals[child_id] not in relatives:
                        add_relatives(individuals[child_id])
                
                # Add parents
                for parent_id in [family.get_husband_id(), family.get_wife_id()]:
                    if parent_id and parent_id in individuals and individuals[parent_id] not in relatives:
                        add_relatives(individuals[parent_id])
    
    if target_individual:
        add_relatives(target_individual)
    
    return relatives, related_families

def write_element_and_children(element, file):
    file.write(str(element))
    for child in element.get_child_elements():
        write_element_and_children(child, file)

def filter_gedcom(input_file, output_file):
    gedcom_parser = gedcom.parser.Parser()
    gedcom_parser.parse_file(input_file)
    
    relatives, related_families = find_relatives(gedcom_parser)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("0 HEAD\n1 CHAR UTF-8\n")
        
        # Write individuals with all their details
        for element in gedcom_parser.get_root_child_elements():
            if element in relatives:
                write_element_and_children(element, f)
            elif element in related_families:
                write_element_and_children(element, f)
        
        # Write trailer
        f.write("0 TRLR\n")

if __name__ == "__main__":
    filter_gedcom("Anneliese2023.ged", "Anneliese2023_filtered.ged")
