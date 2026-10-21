"""Clinical and intake enumerations."""
from enum import Enum


class SexEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class DietTypeEnum(str, Enum):
    omnivore = "omnivore"
    pescatarian = "pescatarian"
    vegetarian = "vegetarian"
    vegan = "vegan"


class MenstrualFlowEnum(str, Enum):
    none = "none"
    light = "light"
    moderate = "moderate"
    heavy = "heavy"


class FrequencyEnum(str, Enum):
    rarely_never = "rarely_never"
    sometimes = "sometimes"
    frequently = "frequently"


class SunExposureEnum(str, Enum):
    under_15_min = "under_15_min"
    min_15_to_30 = "min_15_to_30"
    min_30_to_60 = "min_30_to_60"
    over_60_min = "over_60_min"


class RiskTierEnum(str, Enum):
    low = "low"
    moderate = "moderate"
    elevated = "elevated"


class BmiCategoryEnum(str, Enum):
    underweight = "Underweight"
    normal = "Normal weight"
    overweight = "Overweight"
    obese = "Obesity"


class WhtrCategoryEnum(str, Enum):
    healthy = "Healthy"
    increased_risk = "Increased risk"
    substantial_risk = "Substantial risk"
