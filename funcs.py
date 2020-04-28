def convert_all_to_text(x, X):
    return X

def value_by_age(x, X, y, Y, z, Z):
    return x.where(z < 11, y)

def prepend_age_at_onset(x, X):
    return x.mask(x.notna(), 'Age at onset: ' + X)

def if_18(x, X, y, Y, z, Z):
    return x.where(z >= 18, y),

def split_by_gender(x, X, y, Y):
    return (x.where(y=="F"), x.where(y=="M"))

def format_date(x, X):
    return x.astype("datetime64").dt.strftime("%m/%d/%Y")

funcs = {
    "convert_all_to_text": convert_all_to_text,
    "value_by_age": value_by_age,
    "prepend_age_at_onset": prepend_age_at_onset,
    "if_18": if_18,
    "split_by_gender": split_by_gender,
    "format_date": format_date
}
