
from pycountry import countries
from wtforms import SelectField


# @see https://gist.github.com/mekza/516f172278c328468ea0
class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name) for country in countries]
