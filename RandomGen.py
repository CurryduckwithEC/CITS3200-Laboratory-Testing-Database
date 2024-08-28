import random

def test_type_random(length):
    data_properties = {
        "Drainage": ["drained", "undrained"],
        "Shearing": ["compression", "extension"],
        "Anisotropy": ["isotropic", "anisotropic", "range from 0.3 - 1.0"],
        "Consolidation": ["range from 10 - 1000"],
        "Availability": ["public", "confidential"]
    }

    arr_category = []
    arr_values = []
    counter = 0

    while counter < length:
        keys = list(data_properties.keys())
        random_dict_val = random.randrange(0,len(keys))
        selected_value_array = list(data_properties.values())[random_dict_val]
        arr_category.append(keys[random_dict_val])

        random_key_val = random.randrange(0,len(selected_value_array))
        propertyval = selected_value_array[random_key_val]
        arr_values.append(propertyval)

        counter += 1

    return(arr_category, arr_values)

def sample_properties_random(length):
    soil_properties = {
        "Density": ["loose", "dense"],
        "Plasticity": ["plastic", "non-plastic", "unknown"],
        "PSD": ["clay", "silt", "sand"]
        }
    
    arr_type =[]
    arr_property = []
    counter = 0
    while counter < length:
        keys = list(soil_properties.keys())
        random_dict_val = random.randrange(0,len(keys))
        selected_value_array = list(soil_properties.values())[random_dict_val]
        arr_type.append(keys[random_dict_val])

        random_key_val = random.randrange(0,len(selected_value_array))
        propertyval = selected_value_array[random_key_val]
        arr_property.append(propertyval)

        counter += 1

    return(arr_type, arr_property)
