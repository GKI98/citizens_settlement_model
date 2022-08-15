# Requirements for input data:  

The following tables must be present in the database:

**For houses:**
- buildings

**For the population:**
- administrative_units
- municipalities
- age_sex_administrative_units
- age_sex_municipalities
- age_sex_social_administrative_units

You need to store all this data in a folder and provide a path to this folder in the cli


# The data processing algorithm:

**1. Calculation of data on social groups by age for municipalities.**
- **1.1.** Based on the % of people in the municipality relative to the administrative district and the % of people in the social group in the                        administrative district we get an estimate of the number of social groups in the municipality.

**2. Calculation of the population by house.**
- **2.1.** Calculation of the maximum and probable number of people in houses relative to the population in the city (by county and municipality).
- **2.1.1.** Used parameters:  
             - Minimum number of square meters per person: 9;  
             - Balance accuracy: 1.
- **2.2.** Calculation of social groups by house (total by age).
- **2.3.** Calculation of social groups by house by age.